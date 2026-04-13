from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, Dict, Any

class BaseIndicator(ABC):
    """
    通用的飄移指標/訊號提取器介面 (如: 參數不確定性、特徵解耦、KS Test等)。
    此介面供未來的模組 (Uncertainty, Disentanglement) 繼承與實作，
    並作為 Meta-Detector 的「代理訊號 (Proxy Signals)」。
    """
    
    @abstractmethod
    def update(self, x: np.ndarray, y_true: float, y_pred: float, err: float) -> None:
        """
        更新內部狀態 (如滑動視窗、不確定性計算、潛在空間分佈等)。
        """
        pass

    @abstractmethod
    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """
        進行偵測。
        Returns:
            warning_flag (bool): 該指標是否認為發生了異常/飄移。
            stats (Dict[str, Any]): 詳細的數值或特徵 (如 p-value, entropy, 距離等)。
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        當系統確認發生飄移並重置時，清除此指標內的狀態 (Buffer清空等)。
        """
        pass

class KSDistributionIndicator(BaseIndicator):
    """將原有的 KS Test 封裝成標準 Indicator 介面 (Data distribution-based proxy)"""
    def __init__(self, window_size: int):
        from detectors.distribution import DistributionModule
        self.detector = DistributionModule(window_size=window_size)
        
    def update(self, x: np.ndarray, y_true: float, y_pred: float, err: float) -> None:
        self.detector.update(np.asarray(x).ravel())
        
    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        return self.detector.detect()
        
    def reset(self) -> None:
        self.detector.reset()

class ErrorRateTrendIndicator(BaseIndicator):
    """
    追蹤短期錯誤率與長期錯誤率差異 (Error rate-based proxy)。
    可用作模型 Performance Degradation 的早期代理訊號。
    """
    def __init__(self, short_window: int = 50, long_window: int = 200, threshold: float = 0.15):
        self.short_window = short_window
        self.long_window = long_window
        self.threshold = threshold
        self.errors = []
        
    def update(self, x: np.ndarray, y_true: float, y_pred: float, err: float) -> None:
        self.errors.append(err)
        if len(self.errors) > self.long_window:
            self.errors.pop(0)
            
    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        if len(self.errors) < self.long_window:
            return False, {}
            
        short_err = np.mean(self.errors[-self.short_window:])
        long_err = np.mean(self.errors)
        
        diff = short_err - long_err
        warning_flag = bool(diff > self.threshold)
        
        stats = {
            "short_term_error": float(short_err),
            "long_term_error": float(long_err),
            "error_diff": float(diff)
        }
        return warning_flag, stats
        
    def reset(self) -> None:
        self.errors.clear()

class UncertaintyProxyIndicator(BaseIndicator):
    """
    模型信心度/不確定性的代理訊號 (Uncertainty/Confidence proxy)。
    這裡以預測值的短期變異度 (Variance) 或是邊緣預測來模擬不確定性的升高。
    (你的組員之後可以把這裡置換為 Entropy 或 Bayesian Uncertainty)
    """
    def __init__(self, window_size: int = 100, variance_threshold: float = 0.25):
        self.window_size = window_size
        self.variance_threshold = variance_threshold
        self.predictions = []
        
    def update(self, x: np.ndarray, y_true: float, y_pred: float, err: float) -> None:
        self.predictions.append(y_pred)
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)
            
    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        if len(self.predictions) < self.window_size:
            return False, {}
            
        var = np.var(self.predictions)
        # 如果模型預測的變異度異常飆高 (預測變得非常不穩定、不確定)
        warning_flag = bool(var > self.variance_threshold)
        
        stats = {"prediction_variance": float(var)}
        return warning_flag, stats

    def reset(self) -> None:
        self.predictions.clear()