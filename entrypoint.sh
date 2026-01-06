#!/bin/bash
set -e

echo "Starting Credit ML Service..."

# Check if model exists, if not train it
if [ ! -f "ml/models/credit_model.joblib" ]; then
    echo "Model not found. Training model..."
    python ml/generate_training_data.py
    python ml/train_model.py
    echo "Model training complete!"
else
    echo "Model found at ml/models/credit_model.joblib"
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
