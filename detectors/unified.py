import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import deque

# 匯入 sudden 與 gradual 中的基礎偵測器
from .sudden import HDDM_W, EDDM
from .gradual import DDM, HDDM_A, PageHinkley, ADWIN

class UnifiedDriftDetector:
    """
    統一的概念飄移偵測器 (Unified Drift Detector)
    結合原本 Sudden 與 Gradual 分開的偵測方法，共同進行投票。
    共 6 種不同方法，ADWIN 只取一個。
    """
    def __init__(self, ensemble_strategy: str = "majority", min_samples: int = 30):
        self.ensemble_strategy = ensemble_strategy
        self.min_samples = min_samples
        
        # 初始化 6 種不同的基礎偵測器
        self.hddm_w = HDDM_W(min_samples=min_samples)
        self.eddm = EDDM(min_samples=min_samples)
        self.ddm = DDM()
        self.hddm_a = HDDM_A()
        self.page_hinkley = PageHinkley()
        # 這裡使用 gradual 裡面的標準 ADWIN
        self.adwin = ADWIN()
        
        # 為了事後分析 (drift_type_classifier) 我們要保留過去的 error 記錄
        self._buffer: deque = deque(maxlen=2000)
        self._adwin_drift = False

    def update(self, error: float) -> None:
        """更新所有偵測器的 error"""
        self._buffer.append(error)
        
        # 部分演算法需要 binary error
        binary_error = 1 if error > 0.5 else 0
        
        self.hddm_w.update(binary_error)
        self.eddm.update(binary_error)
        self.ddm.update(binary_error)
        self.hddm_a.update(error)
        self.page_hinkley.update(error)
        self._adwin_drift = self.adwin.update(error)

    def detect(self) -> Tuple[bool, Dict[str, bool]]:
        """
        執行 Ensemble 投票並回傳結果與個別細節
        """
        hddm_w_drift = self.hddm_w.detect()
        eddm_drift, _ = self.eddm.detect()
        ddm_drift, _ = self.ddm.detect()
        hddm_a_drift = self.hddm_a.detect()
        ph_drift = self.page_hinkley.detect()
        adwin_drift = self._adwin_drift
        
        results = {
            "HDDM-W": hddm_w_drift,
            "EDDM": eddm_drift,
            "DDM": ddm_drift,
            "HDDM-A": hddm_a_drift,
            "PageHinkley": ph_drift,
            "ADWIN": adwin_drift,
        }
        
        # Ensemble decision (原實作策略)
        if self.ensemble_strategy == "majority":
            votes = sum(results.values())
            # 總共 6 個演算法，我們預設 3 票(含)以上過半即偵測到飄移
            drift_detected = votes >= 3
        elif self.ensemble_strategy == "any":
            drift_detected = any(results.values())
        elif self.ensemble_strategy == "all":
            drift_detected = all(results.values())
        else:
            drift_detected = False
            
        return drift_detected, results

    def get_errors(self) -> np.ndarray:
        return np.array(list(self._buffer), dtype=np.float64)

    def reset(self) -> None:
        self._buffer.clear()
        self.hddm_w.reset()
        self.eddm.reset()
        self.ddm.reset()
        self.hddm_a.reset()
        self.page_hinkley.reset()
        self.adwin.reset()
