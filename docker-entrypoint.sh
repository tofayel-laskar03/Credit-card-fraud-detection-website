#!/bin/bash
set -e

echo "🚀 Starting Fraud Detection System..."

# Initialize database if it doesn't exist
if [ ! -f "fraud_predictions.db" ]; then
    echo "📊 Initializing database..."
    python -c "from database import init_database; init_database()"
fi

# Initialize model versioning if needed
if [ ! -f "model_versions.json" ]; then
    echo "📝 Initializing model versioning..."
    python model_version.py
fi

# Create metrics file if needed
if [ ! -f "model_metrics.json" ]; then
    echo "📈 Generating model metrics..."
    python model_metrics.py
fi

echo "✅ Initialization complete!"
echo "🌐 Starting Flask application on port 5000..."

# Start the application
exec python app.py