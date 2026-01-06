import pytest
import pandas as pd
from app.services.model_service import model_service
from app.utils.preprocessing import create_derived_features

def test_model_loaded():
    assert model_service.model_loaded is True
    assert model_service.model is not None

def test_preprocessing():
    df = pd.DataFrame([{
        'age': 30,
        'years_at_current_job': 5,
        'monthly_income': 5000,
        'requested_loan_amount': 10000,
        'loan_tenure_months': 12,
        'existing_loan_monthly_payment': 500,
        'other_income_amount': 0,
        'total_savings': 2000,
        'num_previous_loans': 1,
        'previous_loans_repaid_on_time': 1
    }])
    
    df_transformed = create_derived_features(df)
    
    assert 'estimated_monthly_payment' in df_transformed.columns
    assert 'debt_to_income_ratio' in df_transformed.columns
    assert df_transformed['debt_to_income_ratio'].iloc[0] > 0

def test_model_prediction():
    input_data = {
        'age': 35,
        'gender': 'M',
        'marital_status': 'married',
        'number_of_dependents': 2,
        'education_level': 'tertiary',
        'employment_type': 'formal',
        'employment_sector': 'private',
        'years_at_current_job': 10.0,
        'monthly_income': 10000.0,
        'has_other_income': False,
        'other_income_amount': 0.0,
        'total_savings': 50000.0,
        'savings_account_age_months': 48,
        'average_monthly_deposit': 2000.0,
        'num_previous_loans': 2,
        'previous_loans_repaid_on_time': 2,
        'has_existing_loan': False,
        'existing_loan_balance': 0.0,
        'existing_loan_monthly_payment': 0.0,
        'requested_loan_amount': 5000.0,
        'loan_purpose': 'business',
        'loan_tenure_months': 12,
        'has_guarantor': True,
        'has_collateral': False
    }
    
    result = model_service.predict(input_data)
    assert 'score' in result
    assert 0 <= result['score'] <= 1
    assert 'engineered_features' in result

def test_feature_importance():
    factors = model_service.get_top_factors(5)
    assert len(factors) == 5
    for f in factors:
        assert 'factor' in f
        assert 'importance' in f
        assert f['importance'] >= 0
