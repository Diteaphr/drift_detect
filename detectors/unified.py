import numpy as np
from typing import Optional, Tuple, List, Dict, Type, Any
from collections import deque

# 匯入 sudden, gradual, sudden_fast 中的基礎偵測器
from .sudden import HDDM_W, EDDM
from .gradual import DDM, HDDM_A, PageHinkley, ADWIN
from .sudden_fast import ECDD, STEPD

# 建立 Atom Detector 註冊表
ATOM_DETECTORS: Dict[str, Type] = {
    "hddm_w": HDDM_W,
    "eddm": EDDM,
    "ddm": DDM,
    "hddm_a": HDDM_A,
    "page_hinkley": PageHinkley,
    "adwin": ADWIN,
    "ecdd": ECDD,
    "stepd": STEPD,
}

class UnifiedDriftDetector:
    """
    統一的概念飄移偵測器 (Unified Drift Detector) 作為 Atom Detector 函式庫
    允許 Meta Detector 動態選擇需要的 Atom Detectors 進行實例化與管理。
    """
    def __init__(
        self, 
        min_samples: int = 30, 
        atom_kwargs: Dict[str, Dict] = None,
        selected_detectors: List[str] = None
    ):
        self.min_samples = min_samples
        self.atom_kwargs = atom_kwargs or {}
        
        # 預設使用原有的 6 種方法以保持向下相容性
        if selected_detectors is None:
            selected_detectors = ["hddm_w", "eddm", "ddm", "hddm_a", "page_hinkley", "adwin"]
            
        self.detectors: Dict[str, Any] = {}
        for name in selected_detectors:
            name_lower = name.lower()
            if name_lower in ATOM_DETECTORS:
                kwargs = self.atom_kwargs.get(name_lower, {})
                
                # 特殊處理需要 min_samples 的演算法
                if name_lower in ["hddm_w", "eddm"] and "min_samples" not in kwargs:
                    kwargs["min_samples"] = min_samples
                    
                self.detectors[name_lower] = ATOM_DETECTORS[name_lower](**kwargs)
            else:
                raise ValueError(f"Unknown atom detector: {name}")
                
        # 為了事後分析 (drift_type_classifier) 我們要保留過去的 error 記錄
        self._buffer: deque = deque(maxlen=2000)
        
        # 紀錄那些回傳 Tuple 格式 (drift, warning) 的演算法
        self._returns_tuple = ["eddm", "ddm", "ecdd", "stepd"]

    def update(self, error: float) -> None:
        """更新所有偵測器的 error"""
        self._buffer.append(error)
        
        # 部分演算法需要 binary error
        binary_error = 1 if error > 0.5 else 0
        
        for name, detector in self.detectors.items():
            if name in ["hddm_w", "eddm", "ddm", "ecdd", "stepd"]:
                if name in ["ecdd", "stepd"]:
                    detector.update(float(binary_error))
                else:
                    detector.update(binary_error)
            else:
                # ADWIN 的 update 會直接回傳是否 drift
                if name == "adwin":
                    detector._last_drift = detector.update(error)
                else:
                    detector.update(error)

    def detect(self) -> Dict[str, bool]:
        """执行並回傳所有子演算法的各自偵測結果。"""
        results = {}
        
        for name, detector in self.detectors.items():
            if name == "adwin":
                drift = getattr(detector, "_last_drift", False)
            elif name in self._returns_tuple:
                drift, _ = detector.detect()
            else:
                drift = detector.detect()
                
            results[name] = drift
            
        return results

    def get_errors(self) -> np.ndarray:
        return np.array(list(self._buffer), dtype=np.float64)

    def reset(self) -> None:
        self._buffer.clear()
        for name, detector in self.detectors.items():
            detector.reset()
            if name == "adwin":
                detector._last_drift = False
