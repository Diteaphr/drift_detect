"""
Example: how to call the recurring drift detector from your pipeline.

Assume sudden/gradual detector has just fired at index t with prediction_errors available.
"""

import numpy as np
from detectors import ConceptMemory, detect_recurring_drift

# Simulated stream of prediction errors (e.g. from your model)
np.random.seed(42)
prediction_errors = np.cumsum(np.random.randn(500) * 0.1) + np.sin(np.linspace(0, 4 * np.pi, 500)) * 0.5

# Shared concept memory (create once, pass from pipeline)
concept_memory = ConceptMemory(recurrence_threshold=0.5)

# First drift alert at t=100 (from sudden/gradual detector)
t1 = 100
is_recurring_1 = detect_recurring_drift(prediction_errors, t1, concept_memory)
print(f"Drift at t={t1} -> Recurring: {is_recurring_1}")  # False (memory empty, then stored)

# Second "similar" drift later (e.g. same concept reappears)
t2 = 250
is_recurring_2 = detect_recurring_drift(prediction_errors, t2, concept_memory)
print(f"Drift at t={t2} -> Recurring: {is_recurring_2}")  # Depends on similarity

# Use the result: if recurring -> maybe retrieve model from pool; if not -> classify as sudden/gradual
if is_recurring_2:
    print("-> Recurring drift: e.g. retrieve previous model from model pool")
else:
    print("-> New drift: send to Drift Type Classifier (sudden vs gradual)")
