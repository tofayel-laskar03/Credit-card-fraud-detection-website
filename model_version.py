import json
import os
from datetime import datetime

MODEL_VERSION_FILE = 'model_versions.json'

def get_current_version():
    """Get current model version info"""
    if not os.path.exists(MODEL_VERSION_FILE):
        return None
    
    with open(MODEL_VERSION_FILE, 'r') as f:
        versions = json.load(f)
    
    if not versions:
        return None
    
    # Return latest version
    return versions[-1]

def add_model_version(version_info):
    """Add a new model version"""
    if os.path.exists(MODEL_VERSION_FILE):
        with open(MODEL_VERSION_FILE, 'r') as f:
            versions = json.load(f)
    else:
        versions = []
    
    versions.append(version_info)
    
    with open(MODEL_VERSION_FILE, 'w') as f:
        json.dump(versions, f, indent=2)
    
    print(f"✅ Model version {version_info['version']} added!")

def create_initial_version():
    """Create initial model version entry"""
    version_info = {
        'version': '1.0.0',
        'date': '2026-02-18',
        'model_type': 'Random Forest',
        'metrics': {
            'accuracy': 0.9989,
            'precision': 0.8710,
            'recall': 0.8810,
            'f1_score': 0.8760,
            'roc_auc': 0.95
        },
        'dataset': {
            'total_samples': 100000,
            'training_samples': 80000,
            'test_samples': 20000,
            'fraud_percentage': 5.0
        },
        'features': [
            'amount',
            'hour',
            'is_night',
            'is_high_amount',
            'transaction_type_enc',
            'merchant_category_enc',
            'country_enc'
        ],
        'status': 'active',
        'deployed_by': 'ML Team',
        'notes': 'Initial production deployment with SMOTE balancing'
    }
    
    add_model_version(version_info)
    return version_info

if __name__ == '__main__':
    create_initial_version()
    print("\n✅ Model versioning initialized!")