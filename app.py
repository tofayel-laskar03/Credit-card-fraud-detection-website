from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
from datetime import datetime
from database import save_prediction, get_recent_predictions, get_prediction_stats, init_database
app = Flask(__name__)

# Load the model package once when server starts
print("Loading model package...")
with open('model/fraud_detection_complete.pkl', 'rb') as f:
    package = pickle.load(f)
model = package['model']
scaler = package['scaler']
le_transaction = package['le_transaction']
le_merchant = package['le_merchant']
le_country = package['le_country']
features = package['features']
print("Model loaded successfully!")

# Extract available options from encoders
TRANSACTION_TYPES = le_transaction.classes_.tolist()
MERCHANT_CATEGORIES = le_merchant.classes_.tolist()
COUNTRIES = le_country.classes_.tolist()

print(f"Transaction types: {TRANSACTION_TYPES}")
print(f"Merchant categories: {MERCHANT_CATEGORIES}")
print(f"Countries: {COUNTRIES}")

def predict_fraud(amount, transaction_type, merchant_category, country, hour):
    """
    Predict if a transaction is fraudulent
    """
    try:
        # Validate that values exist in encoders
        if transaction_type not in TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type. Must be one of: {TRANSACTION_TYPES}")
        if merchant_category not in MERCHANT_CATEGORIES:
            raise ValueError(f"Invalid merchant category. Must be one of: {MERCHANT_CATEGORIES}")
        if country not in COUNTRIES:
            raise ValueError(f"Invalid country. Must be one of: {COUNTRIES}")
        
        # Step 1: Encode categorical features
        trans_enc = le_transaction.transform([transaction_type])[0]
        merch_enc = le_merchant.transform([merchant_category])[0]
        country_enc = le_country.transform([country])[0]
        
        # Step 2: Create additional features
        is_night = 1 if (hour <= 5 or hour >= 22) else 0
        is_high = 1 if amount > 1000 else 0
        
        # Step 3: Create input DataFrame
        input_data = pd.DataFrame([[
            amount,
            hour,
            is_night,
            is_high,
            trans_enc,
            merch_enc,
            country_enc
        ]], columns=features)
        
        # Step 4: Scale features
        input_data[['amount', 'hour']] = scaler.transform(
            input_data[['amount', 'hour']]
        )
        
        # Step 5: Predict
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "HIGH"
            risk_color = "#e74c3c"  # Red
        elif probability >= 0.4:
            risk_level = "MEDIUM"
            risk_color = "#f39c12"  # Orange
        else:
            risk_level = "LOW"
            risk_color = "#2ecc71"  # Green
        
        return {
            'success': True,
            'is_fraud': int(prediction),
            'fraud_probability': round(float(probability) * 100, 2),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'message': 'Prediction completed successfully'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }

def get_fraud_explanation(amount, transaction_type, merchant_category, country, hour, 
                         is_night, is_high, fraud_probability):
    """
    Generate explanation for why transaction was flagged as fraud
    Uses feature importance from Random Forest
    """
    
    # Feature importance from Random Forest (from training)
    feature_importance = {
        'amount': 0.35,
        'merchant_category_enc': 0.22,
        'country_enc': 0.18,
        'is_high_amount': 0.12,
        'is_night': 0.08,
        'hour': 0.03,
        'transaction_type_enc': 0.02
    }
    
    # Risk indicators with their contributions
    risk_factors = []
    
    # Check Amount
    if amount > 3000:
        risk_factors.append({
            'factor': 'Very High Amount',
            'value': f'${amount:,.2f}',
            'importance': feature_importance['amount'],
            'risk_level': 'high'
        })
    elif amount > 1000:
        risk_factors.append({
            'factor': 'High Amount',
            'value': f'${amount:,.2f}',
            'importance': feature_importance['amount'],
            'risk_level': 'medium'
        })
    
    # Check Time
    if is_night == 1:
        if hour <= 5:
            risk_factors.append({
                'factor': 'Very Late Night Transaction',
                'value': f'{hour}:00 AM',
                'importance': feature_importance['is_night'],
                'risk_level': 'high'
            })
        else:
            risk_factors.append({
                'factor': 'Late Night Transaction',
                'value': f'{hour}:00 PM',
                'importance': feature_importance['is_night'],
                'risk_level': 'medium'
            })
    
    # Check Country (high-risk countries)
    if country in ['NG', 'TR']:
        risk_factors.append({
            'factor': 'High-Risk Country',
            'value': country,
            'importance': feature_importance['country_enc'],
            'risk_level': 'high'
        })
    
    # Check Merchant Category (high-risk categories)
    if merchant_category in ['Travel', 'Electronics']:
        risk_factors.append({
            'factor': 'High-Risk Merchant Category',
            'value': merchant_category,
            'importance': feature_importance['merchant_category_enc'],
            'risk_level': 'medium'
        })
    
    # Check Transaction Type
    if transaction_type in ['ATM', 'Online']:
        risk_factors.append({
            'factor': 'Risky Transaction Type',
            'value': transaction_type,
            'importance': feature_importance['transaction_type_enc'],
            'risk_level': 'medium'
        })
    
    # Sort by importance
    risk_factors.sort(key=lambda x: x['importance'], reverse=True)
    
    # Take top 3
    top_factors = risk_factors[:3]
    
    # Generate protective factors if low fraud probability
    protective_factors = []
    if fraud_probability < 30:
        if amount < 500:
            protective_factors.append({
                'factor': 'Low Transaction Amount',
                'value': f'${amount:,.2f}',
                'importance': feature_importance['amount']
            })
        
        if is_night == 0:
            protective_factors.append({
                'factor': 'Normal Business Hours',
                'value': f'{hour}:00',
                'importance': feature_importance['is_night']
            })
        
        if country in ['US', 'UK', 'FR', 'DE']:
            protective_factors.append({
                'factor': 'Low-Risk Country',
                'value': country,
                'importance': feature_importance['country_enc']
            })
        
        protective_factors.sort(key=lambda x: x['importance'], reverse=True)
        top_factors = protective_factors[:3]
    
    return top_factors

@app.route('/')
def home():
    """Render the main page with dynamic options"""
    return render_template('index.html',
                         transaction_types=TRANSACTION_TYPES,
                         merchant_categories=MERCHANT_CATEGORIES,
                         countries=COUNTRIES)

@app.route('/api/options')
def get_options():
    """API endpoint to get available options"""
    return jsonify({
        'transaction_types': TRANSACTION_TYPES,
        'merchant_categories': MERCHANT_CATEGORIES,
        'countries': COUNTRIES
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Extract fields
        amount = float(data.get('amount'))
        transaction_type = data.get('transaction_type')
        merchant_category = data.get('merchant_category')
        country = data.get('country')
        hour = int(data.get('hour'))
        
        # Validate inputs
        if not transaction_type or not merchant_category or not country:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Amount must be greater than 0'
            }), 400
        
        if hour < 0 or hour > 23:
            return jsonify({
                'success': False,
                'message': 'Hour must be between 0 and 23'
            }), 400
        
        # Make prediction
        result = predict_fraud(amount, transaction_type, merchant_category, country, hour)
        
        # Add timestamp
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if result['success']:
            is_night = 1 if (hour <= 5 or hour >= 22) else 0
            is_high = 1 if amount > 1000 else 0
            
            # Get explanation
            explanation = get_fraud_explanation(
                amount, transaction_type, merchant_category, country, hour,
                is_night, is_high, result['fraud_probability']
            )
            result['explanation'] = explanation
            # save to database
            save_prediction(
                amount=amount,
                transaction_type=transaction_type,
                merchant_category=merchant_category,
                country=country,
                hour=hour,
                is_fraud=result['is_fraud'],
                fraud_probability=result['fraud_probability'],
                risk_level=result['risk_level']
            )
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = get_prediction_stats()
    return jsonify(stats)

@app.route('/history')
def history():
    """Show prediction history page"""
    predictions = get_recent_predictions(limit=20)
    stats = get_prediction_stats()
    
    return render_template('history.html', 
                         predictions=predictions,
                         stats=stats)

@app.route('/metrics')
def metrics():
    """Show model performance metrics page"""
    import json
    
    # Load metrics from JSON file
    try:
        with open('model_metrics.json', 'r') as f:
            metrics_data = json.load(f)
    except FileNotFoundError:
        # Fallback if file doesn't exist
        metrics_data = {
            'models': [],
            'selected_model': 'Random Forest',
            'dataset_info': {},
            'feature_importance': {}
        }
    
    return render_template('metrics.html', metrics=metrics_data)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'options_loaded': {
            'transaction_types': len(TRANSACTION_TYPES),
            'merchant_categories': len(MERCHANT_CATEGORIES),
            'countries': len(COUNTRIES)
        }
    })

@app.route('/api/model/version')
def model_version():
    """Get current model version info"""
    from model_version import get_current_version
    
    version = get_current_version()
    if version:
        return jsonify({
            'success': True,
            'version': version
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No version information available'
        })


@app.route('/monitoring')
def monitoring_dashboard():
    """Monitoring dashboard page"""
    from monitoring import get_model_health, get_performance_metrics
    
    health = get_model_health()
    performance = get_performance_metrics()
    
    return render_template('monitoring.html', 
                         health=health,
                         performance=performance)

@app.route('/api/monitoring/health')
def api_health():
    """API endpoint for health check"""
    from monitoring import get_model_health
    
    health = get_model_health()
    return jsonify(health)

@app.route('/api/monitoring/performance')
def api_performance():
    """API endpoint for performance metrics"""
    from monitoring import get_performance_metrics
    
    performance = get_performance_metrics()
    return jsonify(performance)

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run app (production-ready settings for Docker)
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        debug=debug_mode,
        host='0.0.0.0',  # Important for Docker!
        port=5000,
        threaded=True
    )