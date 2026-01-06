import pandas as pd
import numpy as np
import uuid
import os

# Set seed for reproducibility
np.random.seed(42)

def generate_synthetic_data(num_records=10000):
    print(f"Generating {num_records} synthetic records...")
    
    data = []
    for _ in range(num_records):
        # Basic Info
        client_id = str(uuid.uuid4())
        age = np.random.randint(18, 66)
        gender = np.random.choice(['M', 'F'], p=[0.55, 0.45])
        marital_status = np.random.choice(['single', 'married', 'divorced', 'widowed'], p=[0.4, 0.5, 0.08, 0.02])
        num_dependents = np.random.randint(0, 11)
        education_level = np.random.choice(['none', 'basic', 'secondary', 'tertiary'], p=[0.1, 0.3, 0.4, 0.2])
        
        # Employment
        employment_type = np.random.choice(['formal', 'informal', 'self_employed', 'unemployed'], p=[0.3, 0.4, 0.25, 0.05])
        employment_sector = np.random.choice(['government', 'private', 'agriculture', 'trading', 'other'], p=[0.15, 0.25, 0.3, 0.2, 0.1])
        years_at_current_job = round(float(np.random.uniform(0, min(age - 18, 40))), 1) if age > 18 else 0
        
        # Income
        monthly_income = float(np.random.lognormal(mean=7.5, sigma=0.8)) # Median ~1800 GHS
        monthly_income = np.clip(monthly_income, 500, 50000)
        
        has_other_income = np.random.choice([True, False], p=[0.3, 0.7])
        other_income_amount = round(float(np.random.uniform(0, 20000)), 2) if has_other_income else 0.0
        
        # Savings
        total_savings = float(np.random.lognormal(mean=8.0, sigma=1.2)) # Median ~3000 GHS
        total_savings = np.clip(total_savings, 0, 500000)
        savings_account_age_months = np.random.randint(0, 241)
        average_monthly_deposit = round(float(np.random.uniform(0, 20000)), 2)
        
        # Loan History
        num_previous_loans = np.random.randint(0, 11)
        if num_previous_loans > 0:
            previous_loans_repaid_on_time = np.random.randint(0, num_previous_loans + 1)
        else:
            previous_loans_repaid_on_time = 0
            
        has_existing_loan = np.random.choice([True, False], p=[0.4, 0.6])
        if has_existing_loan:
            existing_loan_balance = round(float(np.random.uniform(0, 200000)), 2)
            existing_loan_monthly_payment = round(float(np.random.uniform(0, 10000)), 2)
        else:
            existing_loan_balance = 0.0
            existing_loan_monthly_payment = 0.0
            
        # Requested Loan
        requested_loan_amount = float(np.random.lognormal(mean=9.0, sigma=1.0)) # Median ~8000 GHS
        requested_loan_amount = np.clip(requested_loan_amount, 500, 200000)
        loan_purpose = np.random.choice(['business', 'education', 'medical', 'housing', 'personal', 'agriculture'])
        loan_tenure_months = np.random.randint(3, 61)
        
        has_guarantor = np.random.choice([True, False], p=[0.6, 0.4])
        has_collateral = np.random.choice([True, False], p=[0.3, 0.7])
        
        # Credit Worthiness Logic (Target)
        score = 0
        
        # Income vs Loan
        if requested_loan_amount < monthly_income * 6: score += 20
        elif requested_loan_amount < monthly_income * 12: score += 10
        else: score -= 20
        
        # Tenure
        if years_at_current_job > 2: score += 15
        
        # Savings
        if total_savings > monthly_income * 3: score += 15
        if savings_account_age_months > 12: score += 10
        
        # History
        if num_previous_loans > 0:
            repayment_ratio = previous_loans_repaid_on_time / num_previous_loans
            if repayment_ratio == 1.0: score += 25
            elif repayment_ratio > 0.8: score += 15
            elif repayment_ratio < 0.5: score -= 30
        
        # Employment
        if employment_type == 'formal': score += 15
        elif employment_type == 'unemployed': score -= 40
        
        # Debt-to-income (simplified)
        est_new_payment = requested_loan_amount / loan_tenure_months
        dti = (existing_loan_monthly_payment + est_new_payment) / monthly_income
        if dti < 0.4: score += 20
        elif dti > 0.6: score -= 30
        
        # Guarantor/Collateral
        if has_guarantor: score += 10
        if has_collateral: score += 15
        
        # Age
        if 21 <= age <= 60: score += 5
        else: score -= 10
        
        # Base threshold for approval is around 50 points
        if score > 50:
            credit_worthy = 1
        elif score < 30:
            credit_worthy = 0
        else:
            # Randomness for middle scores
            credit_worthy = np.random.choice([0, 1], p=[0.4, 0.6])
            
        # Add realistic noise (flip 10% of labels)
        if np.random.random() < 0.10:
            credit_worthy = 1 - credit_worthy
            
        record = {
            'client_id': client_id,
            'age': age,
            'gender': gender,
            'marital_status': marital_status,
            'number_of_dependents': num_dependents,
            'education_level': education_level,
            'employment_type': employment_type,
            'employment_sector': employment_sector,
            'years_at_current_job': years_at_current_job,
            'monthly_income': round(monthly_income, 2),
            'has_other_income': has_other_income,
            'other_income_amount': other_income_amount,
            'total_savings': round(total_savings, 2),
            'savings_account_age_months': savings_account_age_months,
            'average_monthly_deposit': average_monthly_deposit,
            'num_previous_loans': num_previous_loans,
            'previous_loans_repaid_on_time': previous_loans_repaid_on_time,
            'has_existing_loan': has_existing_loan,
            'existing_loan_balance': existing_loan_balance,
            'existing_loan_monthly_payment': existing_loan_monthly_payment,
            'requested_loan_amount': round(requested_loan_amount, 2),
            'loan_purpose': loan_purpose,
            'loan_tenure_months': loan_tenure_months,
            'has_guarantor': has_guarantor,
            'has_collateral': has_collateral,
            'credit_worthy': credit_worthy
        }
        data.append(record)
        
    df = pd.DataFrame(data)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/training_data.csv', index=False)
    print(f"Data saved to data/training_data.csv. Shape: {df.shape}")
    print(f"Class distribution:\n{df['credit_worthy'].value_counts(normalize=True)}")
    
    return df

if __name__ == "__main__":
    generate_synthetic_data()
