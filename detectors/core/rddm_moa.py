"""MOA RDDM for a stream of 0/1 classification errors.

Port of ``moa.classifiers.core.driftdetection.RDDM`` from Waikato MOA:
https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/RDDM.java

Original RDDM copyright (C) 2016 Barros, Cabral, Goncalves, Santos;
DDM foundation copyright (C) 2008 University of Waikato. Licensed under
Apache-2.0; the license text is in ``detectors/core/LICENSE.rddm-moa.txt``.
This port preserves its default options, ring-buffer replay, warning limit,
and internal stable-concept reset. It does not use the older in-repo RDDM
approximation in ``detectors.core.unified``.
"""

from __future__ import annotations

import math


class MOARDDM:
    """Reactive Drift Detection Method with MOA's state transitions."""

    def __init__(
        self,
        min_n_instances: int = 129,
        warning_level: float = 1.773,
        drift_level: float = 2.258,
        max_size_concept: int = 40000,
        min_size_concept: int = 7000,
        warning_limit: int = 1400,
    ) -> None:
        self.min_n_instances = int(min_n_instances)
        self.warning_level = float(warning_level)
        self.drift_level = float(drift_level)
        self.max_size_concept = int(max_size_concept)
        self.min_size_concept = int(min_size_concept)
        self.warning_limit = int(warning_limit)
        if self.min_n_instances < 0 or self.min_size_concept < 1 or self.warning_limit < 1:
            raise ValueError("RDDM instance counts and warning limit must be positive")
        if self.max_size_concept < 1:
            raise ValueError("RDDM max_size_concept must be positive")
        self.reset()

    def reset(self) -> None:
        """Discard all history, equivalent to MOA initialize()."""
        self._stored = bytearray(self.min_size_concept)
        self._stored_count = 0
        self._first_pos = 0
        self._last_pos = -1
        self._last_warn_pos = -1
        self._last_warn_inst = -1
        self._inst_num = 0
        self._rddm_drift = False
        self.drift_detected = False
        self.warning_detected = False
        self.estimation = 1.0
        self._p_min = math.inf
        self._s_min = math.inf
        self._ps_min = math.inf
        self._reset_learning()

    def _reset_learning(self) -> None:
        self._n = 1
        self._p = 1.0
        self._s = 0.0
        # MOA only clears minima after an outwardly reported change. An
        # internal max-concept restart retains them.
        if self.drift_detected:
            self._p_min = math.inf
            self._s_min = math.inf
            self._ps_min = math.inf

    def update(self, value: int | float) -> "MOARDDM":
        """Feed one 0/1 error and expose this step's warning/drift flags."""
        error = float(value)
        if error not in (0.0, 1.0):
            raise ValueError("MOA RDDM requires a 0/1 classification error")

        if self._rddm_drift:
            self._reset_learning()
            if self._last_warn_pos != -1:
                self._first_pos = self._last_warn_pos
                self._stored_count = self._last_pos - self._first_pos + 1
                if self._stored_count <= 0:
                    self._stored_count += self.min_size_concept

            pos = self._first_pos
            for _ in range(self._stored_count):
                self._p += (self._stored[pos] - self._p) / self._n
                self._s = math.sqrt(self._p * (1.0 - self._p) / self._n)
                if (
                    self.drift_detected
                    and self._n > self.min_n_instances
                    and self._p + self._s < self._ps_min
                ):
                    self._p_min = self._p
                    self._s_min = self._s
                    self._ps_min = self._p + self._s
                self._n += 1
                pos = (pos + 1) % self.min_size_concept

            self._last_warn_pos = -1
            self._last_warn_inst = -1
            self._rddm_drift = False
            self.drift_detected = False

        self._last_pos = (self._last_pos + 1) % self.min_size_concept
        self._stored[self._last_pos] = int(error)
        if self._stored_count < self.min_size_concept:
            self._stored_count += 1
        else:
            self._first_pos = (self._first_pos + 1) % self.min_size_concept
            if self._last_warn_pos == self._last_pos:
                self._last_warn_pos = -1

        self._p += (error - self._p) / self._n
        self._s = math.sqrt(self._p * (1.0 - self._p) / self._n)
        self._inst_num += 1
        self._n += 1
        self.estimation = self._p
        self.warning_detected = False

        if self._n <= self.min_n_instances:
            return self

        if self._p + self._s < self._ps_min:
            self._p_min = self._p
            self._s_min = self._s
            self._ps_min = self._p + self._s

        if self._p + self._s > self._p_min + self.drift_level * self._s_min:
            self.drift_detected = True
            self._rddm_drift = True
            if self._last_warn_inst == -1:
                self._first_pos = self._last_pos
                self._stored_count = 1
            return self

        if self._p + self._s > self._p_min + self.warning_level * self._s_min:
            if self._last_warn_inst != -1 and self._last_warn_inst + self.warning_limit <= self._inst_num:
                self.drift_detected = True
                self._rddm_drift = True
                self._first_pos = self._last_pos
                self._stored_count = 1
                self._last_warn_pos = -1
                self._last_warn_inst = -1
                return self
            self.warning_detected = True
            if self._last_warn_inst == -1:
                self._last_warn_inst = self._inst_num
                self._last_warn_pos = self._last_pos
        else:
            self._last_warn_inst = -1
            self._last_warn_pos = -1

        if self._n > self.max_size_concept and not self.warning_detected:
            self._rddm_drift = True  # MOA's silent stable-concept restart.
        return self
