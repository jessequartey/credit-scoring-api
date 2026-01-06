import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates derived features for the credit worthiness model.
    """
    df = df.copy()
    
    # 1. Estimated monthly payment (with approx interest)
    # Average interest rate for S&L in Ghana can be high (e.g. 25-30% annual)
    interest_rate_monthly = 0.025 # 2.5% per month
    n = df['loan_tenure_months']
    df['estimated_monthly_payment'] = (df['requested_loan_amount'] * interest_rate_monthly * (1 + interest_rate_monthly)**n) / \
                                      ((1 + interest_rate_monthly)**n - 1)
    
    # 2. Debt to income ratio (existing + new)
    df['debt_to_income_ratio'] = (df['existing_loan_monthly_payment'] + df['estimated_monthly_payment']) / df['monthly_income']
    
    # 3. Loan to income ratio (annual)
    df['loan_to_income_ratio'] = df['requested_loan_amount'] / (df['monthly_income'] * 12)
    
    # 4. Savings to loan ratio
    df['savings_to_loan_ratio'] = df['total_savings'] / df['requested_loan_amount']
    
    # 5. Income stability score
    df['income_stability_score'] = df['years_at_current_job'] / df['age']
    
    # 6. Repayment history score
    df['repayment_history_score'] = df.apply(
        lambda x: x['previous_loans_repaid_on_time'] / max(x['num_previous_loans'], 1), axis=1
    )
    
    # 7. Total monthly income
    df['total_monthly_income'] = df['monthly_income'] + df['other_income_amount']
    
    # 8. Affordability ratio
    df['affordability_ratio'] = (df['total_monthly_income'] - df['existing_loan_monthly_payment'] - df['estimated_monthly_payment']) / df['total_monthly_income']
    
    # 9. Is new client
    df['is_new_client'] = (df['num_previous_loans'] == 0).astype(int)
    
    # 10. Age groups
    def get_age_group(age):
        if age <= 25: return 'young'
        if age <= 45: return 'adult'
        return 'senior'
    
    df['age_group'] = df['age'].apply(get_age_group)
    
    return df

def get_preprocessing_pipeline():
    """
    Returns the unified ColumnTransformer for the model.
    """
    numerical_features = [
        'age', 'years_at_current_job', 'monthly_income', 'other_income_amount',
        'total_savings', 'savings_account_age_months', 'average_monthly_deposit',
        'existing_loan_balance', 'existing_loan_monthly_payment',
        'requested_loan_amount', 'loan_tenure_months',
        'estimated_monthly_payment', 'debt_to_income_ratio', 'loan_to_income_ratio',
        'savings_to_loan_ratio', 'income_stability_score', 'repayment_history_score',
        'total_monthly_income', 'affordability_ratio'
    ]
    
    categorical_features = [
        'gender', 'marital_status', 'education_level',
        'employment_type', 'employment_sector', 'loan_purpose', 'age_group'
    ]
    
    binary_features = [
        'has_other_income', 'has_existing_loan', 'has_guarantor', 'has_collateral', 'is_new_client'
    ]
    
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    binary_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features),
            ('bin', binary_transformer, binary_features)
        ]
    )
    
    return preprocessor
