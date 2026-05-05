from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import numpy as np

class BaseMetaDetector(ABC):
    """
    Abstract interface for Meta-Detectors representing the overall drift detection architecture
    (e.g., Steps 1-6 in the traditional pipeline, or future Statistical Fusion models).
    """

    @abstractmethod
    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int, **kwargs
    ) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Update the meta-detector state with new samples and detect if a concept drift occurred.

        Args:
            x (np.ndarray): Current feature vector.
            y_true (float): True label of the current sample.
            y_pred (float): Model's prediction.
            err (float): Prediction error (e.g., 1.0 for misclassification, 0.0 for correct).
            t (int): Current time step index.

        Returns:
            is_drift (bool): True if drift is detected, False otherwise.
            time_t (int): The timestamp (step index) at which the drift occurred.
            sub_detector_stats (Dict[str, Any]): Detailed statistical metrics, p-values, 
                                                 or ensemble votes from underlying mechanisms.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the meta-detector state (usually called after a drift is confirmed).
        """
        pass

    def notify_drift(self, **kwargs) -> None:
        """
        Notification hook called when a drift has been confirmed by the pipeline.
        Default implementation is a no-op. Meta-detectors can override this to
        evolve internal state (e.g. preserve/adjust weights) instead of full reset.
        """
        return None
