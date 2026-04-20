import json
import os
from datetime import datetime, timedelta
from database import get_prediction_stats
import sqlite3

MONITORING_LOG = 'monitoring_log.json'

def log_prediction_event(event_type, details):
    """Log monitoring events"""
    if os.path.exists(MONITORING_LOG):
        with open(MONITORING_LOG, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    event = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'details': details
    }
    
    logs.append(event)
    
    # Keep only last 1000 events
    logs = logs[-1000:]
    
    with open(MONITORING_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

def get_model_health():
    """Check model health status"""
    stats = get_prediction_stats()
    
    # Calculate health metrics
    total = stats.get('total', 0)
    fraud_rate = stats.get('fraud_rate', 0)
    
    # Health checks
    health_status = {
        'status': 'healthy',
        'checks': {},
        'metrics': stats,
        'timestamp': datetime.now().isoformat()
    }
    
    # Check 1: Fraud detection rate
    if fraud_rate > 20:
        health_status['checks']['fraud_rate'] = {
            'status': 'warning',
            'message': f'Fraud rate unusually high: {fraud_rate}%',
            'value': fraud_rate
        }
        health_status['status'] = 'degraded'
    else:
        health_status['checks']['fraud_rate'] = {
            'status': 'ok',
            'message': 'Fraud rate within normal range',
            'value': fraud_rate
        }
    
    # Check 2: Prediction volume
    if total > 0:
        health_status['checks']['prediction_volume'] = {
            'status': 'ok',
            'message': f'{total} predictions made',
            'value': total
        }
    else:
        health_status['checks']['prediction_volume'] = {
            'status': 'warning',
            'message': 'No predictions yet',
            'value': 0
        }
    
    # Check 3: Model loaded
    try:
        with open('model/fraud_detection_complete.pkl', 'rb'):
            health_status['checks']['model_file'] = {
                'status': 'ok',
                'message': 'Model file accessible'
            }
    except:
        health_status['checks']['model_file'] = {
            'status': 'critical',
            'message': 'Model file not accessible'
        }
        health_status['status'] = 'unhealthy'
    
    return health_status

def get_performance_metrics():
    """Get performance metrics over time"""
    conn = sqlite3.connect('fraud_predictions.db')
    cursor = conn.cursor()
    
    # Get predictions from last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
            AVG(fraud_probability) as avg_probability
        FROM predictions
        WHERE timestamp > ?
    ''', (yesterday,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] > 0:
        return {
            'period': '24_hours',
            'total_predictions': row[0],
            'fraud_detected': row[1],
            'fraud_rate': round((row[1] / row[0]) * 100, 2) if row[0] > 0 else 0,
            'avg_fraud_probability': round(row[2], 2) if row[2] else 0
        }
    else:
        return {
            'period': '24_hours',
            'total_predictions': 0,
            'fraud_detected': 0,
            'fraud_rate': 0,
            'avg_fraud_probability': 0
        }