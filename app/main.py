from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import credit
from app.schemas.credit import HealthResponse, RulesConfig
from app.config import settings
from app.services.model_service import model_service
import json
import os

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credit.router)

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        is_model_loaded=model_service.model_loaded
    )

@app.get("/api/v1/rules")
async def get_rules(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    if os.path.exists(settings.RULES_CONFIG_PATH):
        with open(settings.RULES_CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"error": "Rules config not found"}

@app.put("/api/v1/rules")
async def update_rules(config: RulesConfig, x_admin_api_key: str = Header(...)):
    if x_admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Admin API Key")
    
    with open(settings.RULES_CONFIG_PATH, 'w') as f:
        json.dump(config.dict(), f, indent=2)
    
    return {"message": "Rules updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
