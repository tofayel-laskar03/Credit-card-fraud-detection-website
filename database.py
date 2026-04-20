import sqlite3
from datetime import datetime
import os

DATABASE_PATH = 'fraud_predictions.db'

def init_database():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            merchant_category TEXT NOT NULL,
            country TEXT NOT NULL,
            hour INTEGER NOT NULL,
            is_fraud INTEGER NOT NULL,
            fraud_probability REAL NOT NULL,
            risk_level TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def save_prediction(amount, transaction_type, merchant_category, country, hour, 
                   is_fraud, fraud_probability, risk_level):
    """Save a prediction to the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO predictions 
        (timestamp, amount, transaction_type, merchant_category, country, hour, 
         is_fraud, fraud_probability, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, amount, transaction_type, merchant_category, country, hour,
          is_fraud, fraud_probability, risk_level))
    
    conn.commit()
    conn.close()

def get_recent_predictions(limit=20):
    """Get the most recent predictions"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, amount, transaction_type, merchant_category, 
               country, hour, is_fraud, fraud_probability, risk_level
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    
    predictions = cursor.fetchall()
    conn.close()
    
    return predictions

def get_prediction_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Total predictions
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total = cursor.fetchone()[0]
    
    # Fraud count
    cursor.execute('SELECT COUNT(*) FROM predictions WHERE is_fraud = 1')
    fraud_count = cursor.fetchone()[0]
    
    # Genuine count
    genuine_count = total - fraud_count
    
    # Fraud rate
    fraud_rate = (fraud_count / total * 100) if total > 0 else 0
    
    # Average fraud probability
    cursor.execute('SELECT AVG(fraud_probability) FROM predictions')
    avg_probability = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total': total,
        'fraud_count': fraud_count,
        'genuine_count': genuine_count,
        'fraud_rate': round(fraud_rate, 2),
        'avg_probability': round(avg_probability, 2)
    }

def clear_all_predictions():
    """Clear all predictions (for testing)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()
    print("✅ All predictions cleared!")

# Initialize database when module is imported (idempotent - uses CREATE TABLE IF NOT EXISTS)
init_database()