from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
from app.schemas.credit import CreditCheckRequest, CreditCheckResponse, CreditFactor, Decision, Confidence, RiskLevel, ModelInfo
from app.services.model_service import model_service
from app.services.rule_engine import RuleEngine
from app.config import settings
import uuid

router = APIRouter(prefix="/api/v1/credit", tags=["credit"])
rule_engine = RuleEngine(settings.RULES_CONFIG_PATH)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

def get_risk_level(score: float) -> RiskLevel:
    if score >= 0.8: return RiskLevel.low
    if score >= 0.6: return RiskLevel.medium
    if score >= 0.4: return RiskLevel.high
    return RiskLevel.very_high

@router.post("/check", response_model=CreditCheckResponse)
async def check_credit(request: CreditCheckRequest, api_key: str = Depends(verify_api_key)):
    try:
        # 1. Prepare input data for prediction
        input_data = request.client.model_dump()
        input_data.update(request.loan.model_dump())
        
        # 2. Add client_id if missing (for processing)
        if 'client_id' not in input_data:
            input_data['client_id'] = str(uuid.uuid4())
            
        # 3. Predict with ML model and get engineered features
        prediction = model_service.predict(input_data)
        ml_score = prediction["score"]
        features = prediction["engineered_features"]

        # 4. Run rule engine
        rule_results = rule_engine.check_rules(features)
        thresholds = rule_engine.get_thresholds()
        
        # 5. Determine decision
        decision = Decision.manual_review
        recommendations = rule_results["recommendations"]
        flags = rule_results["flags"]
        rules_applied = [r["name"] for r in rule_results["auto_reject"] + rule_results["auto_approve"]]
        
        if rule_results["auto_reject"]:
            decision = Decision.rejected
        elif rule_results["auto_approve"]:
            decision = Decision.approved
        else:
            # Use ML threshold
            min_score = thresholds.get("min_credit_score", 0.5)
            if ml_score >= min_score:
                decision = Decision.approved
            else:
                decision = Decision.rejected
                
        # Confidence
        confidence = Confidence.medium
        if ml_score >= thresholds.get("high_confidence_threshold", 0.8) or ml_score <= thresholds.get("low_confidence_threshold", 0.3):
            confidence = Confidence.high
            
        # Risk Level
        risk_level = get_risk_level(ml_score)
        
        # 6. Format response
        # Create some factors for explainability (demo)
        factors = []
        top_importance = model_service.get_top_factors(3)
        for imp in top_importance:
            factor_name = imp["factor"]
            # Simple logic for impact direction (demo)
            impact = "positive"
            if "ratio" in factor_name or "debt" in factor_name:
                impact = "negative" if features.get(factor_name, 0) > 0.5 else "positive"
            
            factors.append(CreditFactor(
                factor=factor_name,
                impact=impact,
                description=f"Based on historical data for {factor_name}"
            ))
            
        response = CreditCheckResponse(
            decision=decision,
            credit_score=round(ml_score * 100, 2),
            confidence=confidence,
            risk_level=risk_level,
            monthly_payment_estimate=round(features.get("estimated_monthly_payment", 0), 2),
            debt_to_income_ratio=round(features.get("debt_to_income_ratio", 0), 4),
            factors=factors,
            recommendations=recommendations + flags,
            rules_applied=rules_applied
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/factors", response_model=ModelInfo)
async def get_factors(api_key: str = Depends(verify_api_key)):
    info = model_service.get_info()
    return ModelInfo(
        version="1.0.0",
        training_date=None, # Should track this eventually
        metrics=info["metrics"],
        top_factors=info["top_factors"]
    )
