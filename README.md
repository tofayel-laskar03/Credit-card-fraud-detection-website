# Credit Card Fraud Detection System

A production-ready machine learning solution for detecting fraudulent credit card transactions with real-time web interface, comprehensive MLOps pipeline, and explainable AI capabilities.

## Overview

This project provides an end-to-end credit card fraud detection system that combines advanced machine learning techniques with modern web technologies. The system is designed to analyze transaction patterns, identify potential fraud risks, and provide actionable insights through an intuitive web interface.

### Key Features

- **Real-time Fraud Detection**: Instant transaction analysis with risk assessment (<200ms inference time)
- **Multi-Model Evaluation**: Comparison of Logistic Regression, Decision Tree, Random Forest, and SVM algorithms
- **Advanced Preprocessing**: SMOTE technique for handling class imbalance without data leakage
- **Risk Categorization**: Low/Medium/High risk classification with confidence scores
- **Interactive Dashboard**: Professional UI with dynamic visualizations and fraud probability meters
- **RESTful API**: Easy integration with existing payment systems
- **Explainable AI**: Feature importance analysis for transparent predictions

### MLOps Capabilities

- **Docker Containerization**: Consistent deployment across environments
- **Model Versioning**: Track model versions with complete metadata
- **Real-time Monitoring**: Health checks and performance tracking
- **CI/CD Ready**: Automated testing and deployment pipelines
- **Database Integration**: SQLite for prediction history and analytics

## Technology Stack

### Machine Learning
- Python 3.8+
- scikit-learn 1.6.1
- pandas, numpy
- imbalanced-learn (SMOTE)
- Random Forest Classifier (primary model)

### Web Application
- Flask 2.3.3
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5
- Chart.js for visualizations

### Infrastructure
- Docker & Docker Compose
- SQLite database
- REST API architecture
- Gunicorn production server

## Model Performance

The Random Forest model achieved the following performance metrics:

| Metric | Score |
|--------|-------|
| Accuracy | 99.89% |
| Precision | 87.10% |
| Recall | 88.10% |
| F1-Score | 87.60% |
| ROC-AUC | 0.95 |

### Feature Importance

1. Transaction Amount (35%)
2. Merchant Category (22%)
3. Country/Location (18%)
4. High-Amount Flag (12%)
5. Night Transaction (8%)
6. Hour of Day (3%)
7. Transaction Type (2%)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Docker (optional, for containerized deployment)

### Option 1: Local Development

```bash
# Navigate to project directory
cd Credit-Card-Fraud-Detection-Website-main

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Access the application at `http://localhost:5000`

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access application
open http://localhost:5000
```

## Project Structure

```
credit-card-fraud-detection/
├── app.py                      # Flask web application
├── database.py                 # SQLite database operations
├── monitoring.py               # System health monitoring
├── model_version.py            # Model versioning system
├── model_metrics.py            # Performance metrics calculation
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose orchestration
├── requirements.txt            # Python dependencies
├── model/                      # Trained ML models
│   └── fraud_detection_complete.pkl
├── templates/                  # HTML templates
│   ├── index.html             # Main prediction interface
│   ├── history.html           # Prediction history
│   ├── metrics.html           # Model performance dashboard
│   └── monitoring.html        # System monitoring
├── static/                     # Frontend assets
│   ├── css/style.css
│   └── js/script.js
├── model_metrics.json          # Cached model metrics
└── model_versions.json         # Model version history
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main application page |
| POST | `/predict` | Submit transaction for fraud prediction |
| GET | `/history` | View prediction history |
| GET | `/metrics` | Model performance metrics |
| GET | `/monitoring` | System monitoring dashboard |
| GET | `/health` | Health check endpoint |
| GET | `/api/options` | Retrieve dropdown options from model |

### API Example

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 4500,
    "transaction_type": "Online",
    "merchant_category": "Electronics",
    "country": "US",
    "hour": 23
  }'
```

Response:
```json
{
  "success": true,
  "is_fraud": 1,
  "fraud_probability": 100.0,
  "risk_level": "HIGH",
  "risk_color": "#e74c3c",
  "explanation": [
    {
      "factor": "Very High Amount",
      "value": "$4,500.00",
      "importance": 0.35,
      "risk_level": "high"
    }
  ],
  "timestamp": "2026-04-21 02:44:41"
}
```

## Using the Web Interface

1. Navigate to `http://localhost:5000`
2. Enter transaction details:
   - Transaction amount
   - Transaction type (ATM, Online, POS, QR)
   - Merchant category (Electronics, Travel, Clothing, Food, Grocery)
   - Country (US, UK, DE, FR, NG, TR)
   - Transaction hour (0-23)
3. Click "Check Transaction" to analyze
4. View results including:
   - Fraud probability gauge
   - Risk level (Low/Medium/High)
   - Risk factors explanation
   - Recommended actions
5. Access historical predictions via the History tab

## Dataset Information

The model was trained on a synthetic credit card transaction dataset with the following characteristics:

- **Total Transactions**: 100,000
- **Genuine Transactions**: 99,000 (99.0%)
- **Fraudulent Transactions**: 1,000 (1.0%)
- **Imbalance Ratio**: 99:1
- **Amount Range**: $29 - $5,000
- **Geographic Coverage**: 6 countries

The 1% fraud rate mirrors real-world credit card fraud statistics (0.5-2%), ensuring realistic model training.

## Feature Engineering

### Temporal Features
- `Hour`: Transaction hour (0-23)
- `IsNightTime`: Boolean flag for 22:00-06:00 window
- `IsWeekend`: Boolean flag for weekend transactions

### Transaction Features
- `HighAmount`: Boolean flag for transactions > $1,000
- `MerchantRisk`: Calculated fraud rate per merchant
- Encoded categorical variables for transaction type, merchant category, and country

## Model Training

The system uses Random Forest as the primary model due to its:
- High accuracy and robustness
- Ability to handle overfitting
- Feature importance extraction
- Excellent performance on imbalanced data

SMOTE (Synthetic Minority Over-sampling Technique) is applied only to training data to balance classes from 99:1 to 1:1, preventing data leakage and improving recall from 68% to 92%.

## Monitoring and Maintenance

### Health Checks
- Model loading verification
- Database connectivity
- API endpoint availability
- Performance metrics tracking

### Model Versioning
- Automatic version tracking
- Performance comparison between versions
- Rollback capabilities

## License

MIT License - See LICENSE file for details

## Contributing

This is a production-ready system designed for deployment. For customization or enhancement:
1. Review the model training notebook in the `bin/model notebook/` directory
2. Modify feature engineering in `app.py` as needed
3. Update model metrics in `model_metrics.json`
4. Test thoroughly before deployment

## Security Considerations

- Input validation on all API endpoints
- SQL injection prevention through parameterized queries
- Model file security (pickle format)
- Rate limiting recommended for production deployment
- HTTPS encryption recommended for production
