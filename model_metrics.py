import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import (
    confusion_matrix, classification_report, 
    roc_auc_score, precision_recall_curve, roc_curve,
    accuracy_score, precision_score, recall_score, f1_score
)
import json

def generate_model_metrics():
    """
    Generate and save model performance metrics
    Run this once after training your model
    """
    
    # These are your actual model results from training
    # Replace with your actual test results
    metrics = {
    'models': [
        {
            'name': 'Logistic Regression',
            'precision': 0.969932,
            'recall': 1.000,
            'f1_score': 0.984737,
            'roc_auc': 0.999987,
            'true_positives': 1000,
            'false_negatives': 0
        },
        {
            'name': 'Decision Tree',
            'precision': 0.994024,
            'recall': 0.998,
            'f1_score': 0.996008,
            'roc_auc': 0.999995,
            'true_positives': 998,
            'false_negatives': 2
        },
        {
            'name': 'Random Forest',
            'precision': 0.991063,
            'recall': 0.998,
            'f1_score': 0.994519,
            'roc_auc': 0.999969,
            'true_positives': 998,
            'false_negatives': 2
        }
    
        ],
        'selected_model': 'Random Forest',
        'dataset_info': {
            'total_samples': 100000,
            'training_samples': 80000,
            'test_samples': 20000,
            'fraud_percentage': 5.0,
            'features_count': 7
        },
        'feature_importance': {
            'amount': 0.35,
            'merchant_category_enc': 0.22,
            'country_enc': 0.18,
            'is_high_amount': 0.12,
            'is_night': 0.08,
            'hour': 0.03,
            'transaction_type_enc': 0.02
        }
    }
    
    # Save to JSON file
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ Model metrics saved to model_metrics.json")
    return metrics

if __name__ == '__main__':
    generate_model_metrics()