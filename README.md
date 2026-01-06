# Credit Worthiness Service

A lightweight ML-powered microservice for evaluating credit worthiness of savings and loans clients in Ghana.

## Overview
This service uses a Random Forest Classifier trained on synthetic data to predict the likelihood of a loan being repaid. It also includes a configurable rule engine for business logic overrides (e.g., auto-rejection for unemployed clients asking for large loans).

## Architecture
- **Framework:** FastAPI (Python)
- **ML Library:** Scikit-Learn (Random Forest)
- **Rules:** JSON-based configurable logic
- **Deployment:** Docker / VPS friendly (CPU only)

## Project Structure
- `app/`: FastAPI application code
- `ml/`: Model training and data generation scripts
- `config/`: Rules and thresholds configuration
- `scripts/`: Automation scripts
- `tests/`: API and model tests

## Quick Start

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd credit-ml
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set your API keys (generate secure keys for production!)
   ```

3. **Setup and Train:**
   ```bash
   ./scripts/setup_and_train.sh
   ```
   This will create a virtual environment, install dependencies, generate 10,000 synthetic records, train the model, and run tests.

4. **Run Locally:**
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

5. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

## API Documentation
Once the service is running, you can access the interactive Swagger documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication
All API endpoints require authentication using an API key passed in the `X-API-Key` header. Admin endpoints require the `X-Admin-API-Key` header.

Generate secure API keys for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Key Endpoints:
- `GET /api/v1/health`: Health check endpoint (no auth required)
- `POST /api/v1/credit/check`: Evaluate a client's credit worthiness (requires API key)
- `GET /api/v1/credit/factors`: Get feature importance and model metrics (requires API key)
- `GET /api/v1/rules`: View current business rules (requires API key)
- `PUT /api/v1/rules`: Update business rules (requires Admin API key)

## PHP Integration Example
```php
<?php
class CreditService {
    private $baseUrl;
    private $apiKey;
    
    public function __construct($baseUrl, $apiKey) {
        $this->baseUrl = $baseUrl;
        $this->apiKey = $apiKey;
    }
    
    public function checkCredit($clientData, $loanData) {
        $ch = curl_init($this->baseUrl . '/api/v1/credit/check');
        
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'X-API-Key: ' . $this->apiKey
            ],
            CURLOPT_POSTFIELDS => json_encode([
                'client' => $clientData,
                'loan' => $loanData
            ])
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        return json_decode($response, true);
    }
}
```

## Development

### Running Tests
```bash
source venv/bin/activate
pytest
```

### Retraining the Model
To add new features or retrain the model with real data:
1. Place your data in `data/training_data.csv`.
2. Update `app/utils/preprocessing.py` if new features are added.
3. Run `python ml/train_model.py`.
4. Run `pytest` to verify changes.

## Security Considerations

⚠️ **Important Security Notes:**

1. **API Keys**: Always use strong, randomly generated API keys in production. Never commit real API keys to version control.

2. **Rule Engine**: The current rule engine uses `eval()` for condition evaluation, which is acknowledged as a security risk in the code. For production environments, replace this with a proper expression parser like `simpleeval`.

3. **CORS**: The application currently allows all origins (`allow_origins=["*"]`). Restrict this to specific domains in production.

4. **Environment Variables**: Keep your `.env` file secure and never commit it to version control.

## Model Information

- **Algorithm**: Random Forest Classifier
- **Training Data**: Synthetic data generated for Ghanaian S&L context
- **Features**: 30+ features including demographic, financial, and loan-specific attributes
- **Performance**: ~79% accuracy, 85% AUC-ROC (on synthetic data)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for educational and commercial use.

## Contact

For questions or support, please open an issue on GitHub.
