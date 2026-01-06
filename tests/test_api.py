import pytest
from httpx import AsyncClient
from app.main import app
from app.config import settings
import json

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["is_model_loaded"] is True

@pytest.mark.asyncio
async def test_credit_check_approved():
    payload = {
        "client": {
            "age": 35,
            "gender": "M",
            "marital_status": "married",
            "number_of_dependents": 2,
            "education_level": "tertiary",
            "employment_type": "formal",
            "employment_sector": "private",
            "years_at_current_job": 10.0,
            "monthly_income": 10000.0,
            "has_other_income": False,
            "other_income_amount": 0.0,
            "total_savings": 50000.0,
            "savings_account_age_months": 48,
            "average_monthly_deposit": 2000.0,
            "num_previous_loans": 2,
            "previous_loans_repaid_on_time": 2,
            "has_existing_loan": False,
            "existing_loan_balance": 0.0,
            "existing_loan_monthly_payment": 0.0
        },
        "loan": {
            "requested_loan_amount": 5000.0,
            "loan_purpose": "business",
            "loan_tenure_months": 12,
            "has_guarantor": True,
            "has_collateral": False
        }
    }
    
    headers = {"X-API-Key": settings.API_KEY}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/credit/check", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] in ["approved", "manual_review"]
    assert "credit_score" in data
    assert "risk_level" in data

@pytest.mark.asyncio
async def test_credit_check_rejected_by_rule():
    # Unemployed asking for large loan should be auto-rejected by rule
    payload = {
        "client": {
            "age": 20,
            "gender": "F",
            "marital_status": "single",
            "number_of_dependents": 0,
            "education_level": "basic",
            "employment_type": "unemployed",
            "employment_sector": "other",
            "years_at_current_job": 0.0,
            "monthly_income": 800.0,
            "has_other_income": False,
            "other_income_amount": 0.0,
            "total_savings": 100.0,
            "savings_account_age_months": 1,
            "average_monthly_deposit": 50.0,
            "num_previous_loans": 0,
            "previous_loans_repaid_on_time": 0,
            "has_existing_loan": False,
            "existing_loan_balance": 0.0,
            "existing_loan_monthly_payment": 0.0
        },
        "loan": {
            "requested_loan_amount": 20000.0,
            "loan_purpose": "personal",
            "loan_tenure_months": 24,
            "has_guarantor": False,
            "has_collateral": False
        }
    }
    
    headers = {"X-API-Key": settings.API_KEY}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/credit/check", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "rejected"
    assert "Unemployed clients cannot request loans above GHS 5,000" in data["recommendations"]

@pytest.mark.asyncio
async def test_authentication_error():
    payload = {}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/credit/check", json=payload, headers={"X-API-Key": "wrong"})
    assert response.status_code == 403
