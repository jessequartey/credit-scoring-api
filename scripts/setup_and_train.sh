#!/bin/bash
set -e

echo "=== Credit Worthiness Service Setup & Training ==="

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Generate training data
echo "Generating synthetic training data..."
export PYTHONPATH=$PYTHONPATH:.
python3 ml/generate_training_data.py

# 4. Train model
echo "Training model..."
python3 ml/train_model.py

# 5. Run tests
echo "Running tests..."
python3 -m pytest tests/

echo ""
echo "=== Success! ==="
echo "The model is trained and the service is ready."
echo "You can start the service with:"
echo "source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Or using Docker:"
echo "docker-compose up --build"
echo "================"
