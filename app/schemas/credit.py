from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
import uuid

class Gender(str, Enum):
    M = "M"
    F = "F"

class MaritalStatus(str, Enum):
    single = "single"
    married = "married"
    divorced = "divorced"
    widowed = "widowed"

class EducationLevel(str, Enum):
    none = "none"
    basic = "basic"
    secondary = "secondary"
    tertiary = "tertiary"

class EmploymentType(str, Enum):
    formal = "formal"
    informal = "informal"
    self_employed = "self_employed"
    unemployed = "unemployed"

class EmploymentSector(str, Enum):
    government = "government"
    private = "private"
    agriculture = "agriculture"
    trading = "trading"
    other = "other"

class LoanPurpose(str, Enum):
    business = "business"
    education = "education"
    medical = "medical"
    housing = "housing"
    personal = "personal"
    agriculture = "agriculture"

class Decision(str, Enum):
    approved = "approved"
    rejected = "rejected"
    manual_review = "manual_review"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"

class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class ClientProfile(BaseModel):
    age: int = Field(..., ge=18, le=65)
    gender: Gender
    marital_status: MaritalStatus
    number_of_dependents: int = Field(..., ge=0, le=10)
    education_level: EducationLevel
    employment_type: EmploymentType
    employment_sector: EmploymentSector
    years_at_current_job: float = Field(..., ge=0, le=40)
    monthly_income: float = Field(..., ge=500)
    has_other_income: bool
    other_income_amount: float = Field(0.0, ge=0)
    total_savings: float = Field(..., ge=0)
    savings_account_age_months: int = Field(..., ge=0)
    average_monthly_deposit: float = Field(..., ge=0)
    num_previous_loans: int = Field(..., ge=0)
    previous_loans_repaid_on_time: int = Field(..., ge=0)
    has_existing_loan: bool
    existing_loan_balance: float = Field(0.0, ge=0)
    existing_loan_monthly_payment: float = Field(0.0, ge=0)

    @field_validator('previous_loans_repaid_on_time')
    def validate_repaid_count(cls, v, values):
        if 'num_previous_loans' in values.data and v > values.data['num_previous_loans']:
            raise ValueError('repaid loans cannot exceed total previous loans')
        return v

class LoanRequest(BaseModel):
    requested_loan_amount: float = Field(..., ge=500, le=500000)
    loan_purpose: LoanPurpose
    loan_tenure_months: int = Field(..., ge=3, le=60)
    has_guarantor: bool
    has_collateral: bool

class CreditCheckRequest(BaseModel):
    client: ClientProfile
    loan: LoanRequest

class CreditFactor(BaseModel):
    factor: str
    impact: str # positive, negative, neutral
    description: str

class CreditCheckResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    decision: Decision
    credit_score: float # 0-100 scale
    confidence: Confidence
    risk_level: RiskLevel
    monthly_payment_estimate: float
    debt_to_income_ratio: float
    factors: List[CreditFactor] = []
    recommendations: List[str] = []
    rules_applied: List[str] = []
    valid_for_hours: int = 24

class HealthResponse(BaseModel):
    status: str
    is_model_loaded: bool
    version: str = "1.0.0"

class RulesConfig(BaseModel):
    version: str
    rules: Dict[str, List[Dict[str, Any]]]
    thresholds: Dict[str, float]

class ModelFactor(BaseModel):
    factor: str
    importance: float

class ModelInfo(BaseModel):
    name: str = "Random Forest Classifier"
    version: str
    training_date: Optional[str]
    metrics: Dict[str, float]
    top_factors: List[ModelFactor]
