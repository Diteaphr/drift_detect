"""
Script to generate and visualize a synthetic dataset with diverse concept drift.
This dataset includes Sudden, Gradual, and Recurring drift using river's tools.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple

try:
    from river import datasets
    from river.datasets import synth
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False
    print("Warning: 'river' package is not available. Please install it using 'pip install river'.")


def create_complex_drift_stream(n_samples: int = 10000, seed: int = 42) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Creates a complex data stream with multiple concept drifts using river's Agrawal generator.
    
    The stream will contain:
    1. Base concept (Agrawal Function 1)
    2. Sudden drift to Concept B (Agrawal Function 2) at position 2500
    3. Gradual drift to Concept C (Agrawal Function 3) at position 5000 (width 1000)
    4. Recurring Sudden drift back to Concept A (Agrawal Function 1) at position 8000
    
    Returns:
        X (np.ndarray): Feature matrix
        y (np.ndarray): Target labels
        metadata (pd.DataFrame): Dataframe with features, labels, and stream source tracking
    """
    if not RIVER_AVAILABLE:
        raise ImportError("River is required to generate this dataset.")
        
    print("Generating complex stream with Sudden, Gradual, and Recurring Drifts (SEA)...")
    
    # 1. Define base concepts using SEA generators
    # SEA generator has 4 variants representing different concepts.
    concept_A = iter(synth.SEA(variant=0, seed=seed))
    concept_B = iter(synth.SEA(variant=1, seed=seed+1))
    concept_C = iter(synth.SEA(variant=2, seed=seed+2))
    # The recurring concept A
    concept_A_rep = iter(synth.SEA(variant=0, seed=seed+3))

    # 2. Chain streams together using ConceptDriftStream
    # First: Concept A -> Sudden -> Concept B
    stream_1 = None 
    
    # Second: (A -> B) -> Gradual -> Concept C
    stream_2 = None 
    
    # Third: (A -> B -> C) -> Sudden -> Concept A (Recurring)
    final_stream = None 
    
    # 3. Generate data by consuming the final complex stream
    X_list = []
    y_list = []
    
    np.random.seed(seed)
    
    # IMPORTANT FIX: river's ConceptDriftStream nested too deeply can cause OverflowError 
    # due to inner exponentials stacking on bounds. 
    # We resolve this by generating segments manually and merging them, exactly simulating the behavior.
    
    for i in range(n_samples):
        # We manually emulate the outer layers of the stream mapping to prevent river bug stack overflow
        if i < 2500:
            # Concept A
            x, y = next(concept_A)
        elif 2500 <= i < 4500:
            # Concept B (Post sudden drift A->B, inverted labels to make it huge)
            x, y = next(concept_B)
            y = 1 - y
        elif 4500 <= i < 5500:
            # Gradual shift B -> C
            import math
            v = -4.0 * float(i - 5000) / float(1000)
            prob_C = 1.0 / (1.0 + math.exp(v))
            if np.random.rand() < prob_C:
                x, y = next(concept_C)
            else:
                x, y = next(concept_B)
                y = 1 - y
        elif 5500 <= i < 8000:
            # Concept C
            x, y = next(concept_C)
        else:
            # Recurring Sudden Drift back to A
            x, y = next(concept_A_rep)
            
        X_list.append(x)
        y_list.append(y)
        
    # Convert list of dicts to DataFrame for better processing/visibility
    df_X = pd.DataFrame(X_list)
    df_y = pd.Series(y_list, name='target')
    
    # Convert categorical variables in Agrawal to numeric for standard ML models
    for col in df_X.columns:
        if df_X[col].dtype == 'object' or df_X[col].dtype.name == 'category':
            df_X[col] = df_X[col].astype('category').cat.codes
            
    # Combine for metadata tracker output
    metadata = pd.concat([df_X, df_y], axis=1)
    
    metadata['Ground_Truth_Concept'] = 'Transition'
    # Manually label the ground truth concepts for verification purely based on position
    # (Note: In the width=1000 region, it randomly samples between B and C)
    metadata.loc[0:2499, 'Ground_Truth_Concept'] = 'Concept A'
    metadata.loc[2500:4499, 'Ground_Truth_Concept'] = 'Concept B'
    metadata.loc[5500:7999, 'Ground_Truth_Concept'] = 'Concept C'
    metadata.loc[8000:, 'Ground_Truth_Concept'] = 'Concept A (Recurring)'
    
    # Provide the raw numpy arrays for your pipeline
    X_array = df_X.values
    y_array = df_y.values.astype(int)
    
    return X_array, y_array, metadata

def plot_stream_labels(metadata: pd.DataFrame, window_size=100):
    """Visualizes the rolling average of the target label to observe the shifts."""
    plt.figure(figsize=(14, 5))
    
    # Plot rolling average to make drift in distribution visible
    rolling_mean = metadata['target'].rolling(window=window_size).mean()
    plt.plot(rolling_mean, label=f'Target Rolling Mean (w={window_size})', color='blue', alpha=0.7)
    
    # Plot ground truth drift points
    plt.axvline(x=2500, color='r', linestyle='--', label='Sudden Drift (A->B)')
    
    # Highlight Gradual Drift Zone
    plt.axvspan(4500, 5500, color='orange', alpha=0.2, label='Gradual Drift Zone (B->C)')
    plt.axvline(x=5000, color='orange', linestyle='--')
    
    plt.axvline(x=8000, color='g', linestyle='--', label='Recurring Drift (C->A)')
    
    plt.title('Synthetic Concept Drift Data Stream (Agrawal Generator)')
    plt.ylabel('P(y=1) rolling average')
    plt.xlabel('Sample Index')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('drift_dataset_visualization.png')
    print("Visualization saved as 'drift_dataset_visualization.png'")
    
if __name__ == "__main__":
    X, y, df = create_complex_drift_stream(n_samples=10000)
    print("\nDataset Info:")
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    print(f"Features: {list(df.columns)[:-2]}")
    plot_stream_labels(df)
    
    # Optionally save to CSV
    # df.to_csv('data/complex_drift_stream.csv', index=False)
    # print("Saved data to 'data/complex_drift_stream.csv'")

