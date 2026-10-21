"""DET4 behavior gates for independent warning and confirmation detectors."""

from __future__ import annotations

import numpy as np

from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector
from src.config import PipelineConfig
from src.ecpf_detector import ECPFZoneDetector
from src.pipeline import ConceptDriftPipeline


class _Arm:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.updates = 0
        self.resets = 0
        self.drift_detected = False

    def update(self, value):
        self.updates += 1
        result = bool(self.outputs.pop(0))
        self.drift_detected = result
        return result

    def reset(self):
        self.resets += 1
        self.drift_detected = False

    def reset_after_confirmation(self):
        self.reset()


class _ScriptedDetector:
    combo_name = "scripted"
    stats = {}

    def __init__(self, outputs, *, zone=False):
        self.outputs = list(outputs)
        self.zone = zone
        self.resets = 0
        self.warning_resets = 0

    def update_values(self, warning_value, drift_value):
        return self.outputs.pop(0)

    def reset(self):
        self.resets += 1

    def reset_warning(self):
        self.warning_resets += 1


def _small_pipeline(**overrides):
    values = dict(
        use_ecpf=True,
        model_type="ht",
        ecpf_signal_mode="dual_adwin",
        ecpf_learn_during_warning=True,
        ecpf_record_warning_events=True,
    )
    values.update(overrides)
    pipe = ConceptDriftPipeline(PipelineConfig(**values))
    x = np.arange(160, dtype=float).reshape(80, 2) / 10.0
    y = ((x[:, 0] + x[:, 1]) % 3 > 1).astype(float)
    pipe.warm_start(x[:40], y[:40])
    return pipe, x, y


def test_warning_and_confirm_arms_are_independent_and_each_updates_once():
    pair = ECPFAdwinFamilyDetector()
    warning = _Arm([True])
    confirm = _Arm([False])
    pair._warn = warning
    pair._drift = confirm

    assert pair.update_values(1.0, 0.0) == (True, False)
    assert warning is not confirm
    assert warning.updates == confirm.updates == 1


def test_any_confirm_resets_both_arms_even_without_pipeline_warning():
    pair = ECPFAdwinFamilyDetector()
    warning = _Arm([False])
    confirm = _Arm([True])
    pair._warn = warning
    pair._drift = confirm

    assert pair.update_values(0.0, 1.0) == (False, True)
    assert warning.resets == confirm.resets == 1


def test_hddma_and_rddm_diagonals_match_existing_zone_detector_flags():
    errors = [int(i % 10 == 0) for i in range(2000)]
    errors += [i % 2 for i in range(2000)]
    errors += [int(i % 10 == 0) for i in range(1000)]

    for kind in ("hddm_a", "rddm"):
        existing = ECPFZoneDetector(kind)
        pair = ECPFAdwinFamilyDetector(
            warning_detector_type=kind,
            drift_detector_type=kind,
        )
        existing_flags = [existing.update_values(v, v) for v in errors]
        pair_flags = [pair.update_values(v, v) for v in errors]
        assert pair_flags == existing_flags


def test_zone_exit_closes_warning_and_clears_buffer():
    pipe, x, y = _small_pipeline()
    pipe._ecpf_detector = _ScriptedDetector([(True, False), (False, False)], zone=True)

    pipe.step(x[40], y[40], index=40)
    assert pipe._ecpf_warning_active
    assert len(pipe._ecpf_buffer) == 1

    pipe.step(x[41], y[41], index=41)
    assert not pipe._ecpf_warning_active
    assert pipe._ecpf_buffer == []
    assert any(e["reason"] == "zone_exit" for e in pipe._ecpf_warning_events)


def test_s1_timeout_rebaselines_warning_and_guard_confirmation_resets_both():
    timeout_pipe, x, y = _small_pipeline(ecpf_detector_warning_timeout=1)
    timeout_detector = _ScriptedDetector([(True, False)] * 3)
    timeout_pipe._ecpf_detector = timeout_detector
    for i in range(40, 43):
        timeout_pipe.step(x[i], y[i], index=i)
    assert timeout_detector.warning_resets == 1
    assert any(e["reason"] == "timeout" for e in timeout_pipe._ecpf_warning_events)

    guard_pipe, x, y = _small_pipeline(ecpf_leader_guard=True)
    main = _ScriptedDetector([(False, False)])
    guard = _ScriptedDetector([(True, True)])
    guard_pipe._ecpf_detector = main
    guard_pipe._ecpf_guard = guard
    _, detections, drifted = guard_pipe.step(x[40], y[40], index=40)
    assert drifted and detections
    assert main.resets == guard.resets == 1
    assert not guard_pipe._ecpf_warning_active
