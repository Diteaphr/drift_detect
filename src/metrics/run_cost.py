"""Time and memory cost of one benchmark run.

``CostMeter`` wraps the predict-then-learn loop of a run:

* time: wall clock (``runtime_s``) and process CPU time (``cpu_time_s``);
* real memory, from the operating system's resident set size (RSS) of the run's
  own process, sampled by a background thread:
  ``rss_before_mb`` (data loaded, system not built yet), ``rss_peak_mb``
  (highest sample while the system runs), ``rss_increment_mb`` (peak - before:
  what the system itself needed) and ``ram_hours_gb`` (the increment integrated
  over wall time, GB x hours, in the spirit of MOA's RAM-Hours);
* ``model_size_final_mb``: the Python object graph of the system after the last
  instance (``deep_sizeof``), measured after the timed and sampled window so the
  traversal does not inflate the other numbers.

RSS needs ``psutil``; without it the RSS fields are ``None``. The numbers are
per process, so they stay valid when several runs execute in parallel as long
as every run gets its own fresh process and the machine does not swap. Wall
time is sensitive to parallel load; CPU time much less so.
"""

from __future__ import annotations

import gc
import logging
import os
import platform
import subprocess
import sys
import threading
import time
import types
from collections import deque
from typing import Any, Dict, Iterable, Optional

import numpy as np

try:
    import psutil
except ImportError:  # pragma: no cover - exercised only without psutil
    psutil = None

MB = 1024 ** 2
GB = 1024 ** 3

_SKIP = (type, types.ModuleType, types.FunctionType, types.BuiltinFunctionType, types.MethodType,
         types.CodeType, types.FrameType, types.GeneratorType, logging.Logger, logging.Manager,
         threading.Thread)


def rss_available() -> bool:
    return psutil is not None


def current_rss() -> Optional[int]:
    """Resident set size of this process in bytes, or None without psutil."""
    if psutil is None:
        return None
    return psutil.Process().memory_info().rss


def deep_sizeof(obj: Any, exclude: Iterable[Any] = ()) -> int:
    """Bytes of every object reachable from ``obj``, each counted once.

    Follows containers, ``__dict__`` and ``__slots__``; numpy arrays count their
    data when they own it (views count their base once). Modules, classes,
    functions and loggers are not followed. Objects in ``exclude`` (e.g. the
    input stream) and everything reachable only through them are skipped.
    Memory held inside C extensions without Python references is not seen.
    """
    seen = {id(o) for o in exclude}
    stack = [obj]
    total = 0
    while stack:
        o = stack.pop()
        if id(o) in seen:
            continue
        seen.add(id(o))
        if isinstance(o, _SKIP):
            continue
        try:
            total += sys.getsizeof(o)
        except TypeError:
            continue
        if isinstance(o, np.ndarray):
            if o.base is not None:
                stack.append(o.base)
            continue
        if isinstance(o, (str, bytes, bytearray, int, float, complex, bool)) or o is None:
            continue
        if isinstance(o, dict):
            stack.extend(o.keys())
            stack.extend(o.values())
        elif isinstance(o, (list, tuple, set, frozenset, deque)):
            stack.extend(o)
        d = getattr(o, "__dict__", None) if not isinstance(o, dict) else None
        if isinstance(d, dict):
            stack.append(d)
        for cls in type(o).__mro__:
            for name in getattr(cls, "__slots__", ()):
                if name in ("__dict__", "__weakref__"):
                    continue
                try:
                    stack.append(getattr(o, name))
                except AttributeError:
                    pass
    return total


class _RSSSampler(threading.Thread):
    def __init__(self, base: int, interval: float):
        super().__init__(daemon=True)
        self.base = base
        self.interval = interval
        self.peak = base
        self.area = 0.0  # byte-seconds above base
        self.n = 0
        self._halt = threading.Event()  # not "_stop": Thread uses that name internally
        self._last_t = time.perf_counter()
        self._last_inc = 0

    def sample(self) -> None:
        rss = current_rss()
        now = time.perf_counter()
        inc = max(0, rss - self.base)
        self.area += 0.5 * (inc + self._last_inc) * (now - self._last_t)
        self._last_t, self._last_inc = now, inc
        self.peak = max(self.peak, rss)
        self.n += 1

    def run(self) -> None:
        while not self._halt.wait(self.interval):
            self.sample()

    def stop(self) -> None:
        self._halt.set()
        self.join()
        self.sample()


class CostMeter:
    """Measure one run: ``start()`` right before the system is built, ``stop()`` right after the last instance."""

    def __init__(self, interval: float = 0.2):
        self.interval = interval
        self._sampler: Optional[_RSSSampler] = None
        self.result: Dict[str, Any] = {}

    def start(self) -> None:
        gc.collect()
        base = current_rss()
        self._rss_before = base
        if base is not None:
            self._sampler = _RSSSampler(base, self.interval)
            self._sampler.start()
        self._t0 = time.perf_counter()
        self._c0 = time.process_time()

    def stop(self, n_instances: int) -> Dict[str, Any]:
        wall = time.perf_counter() - self._t0
        cpu = time.process_time() - self._c0
        res: Dict[str, Any] = {
            "runtime_s": round(wall, 3),
            "cpu_time_s": round(cpu, 3),
            "instances_per_s": round(n_instances / wall, 1) if wall > 0 else None,
            "rss_before_mb": None, "rss_peak_mb": None, "rss_increment_mb": None,
            "ram_hours_gb": None, "rss_samples": 0, "rss_interval_s": self.interval,
        }
        if self._sampler is not None:
            self._sampler.stop()
            s = self._sampler
            res.update({
                "rss_before_mb": round(s.base / MB, 1),
                "rss_peak_mb": round(s.peak / MB, 1),
                "rss_increment_mb": round((s.peak - s.base) / MB, 1),
                "ram_hours_gb": s.area / GB / 3600.0,
                "rss_samples": s.n,
            })
        self.result = res
        return res


def process_peak_rss_mb() -> float:
    """Peak RSS of this process since it started (includes interpreter and data)."""
    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / MB if sys.platform == "darwin" else peak / 1024, 1)


def machine_info() -> Dict[str, Any]:
    """Hardware the run executed on; wall times are only comparable on the same machine."""
    cpu = platform.processor() or platform.machine()
    try:
        if sys.platform == "darwin":
            cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                 text=True, timeout=5).stdout.strip() or cpu
        elif os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu = line.split(":", 1)[1].strip()
                        break
    except (OSError, subprocess.SubprocessError):
        pass
    ram = psutil.virtual_memory().total if psutil is not None else None
    return {
        "hostname": platform.node(),
        "os": platform.platform(),
        "cpu": cpu,
        "cpu_count": os.cpu_count(),
        "ram_gb": round(ram / GB, 1) if ram else None,
        "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
    }
