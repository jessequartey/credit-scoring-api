from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "CreditWorthinessService"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    API_KEY: str = "your-secret-api-key-here"
    ADMIN_API_KEY: str = "your-admin-api-key-here"
    
    MODEL_PATH: str = "ml/models/credit_model.joblib"
    RULES_CONFIG_PATH: str = "config/rules.json"
    
    LOG_LEVEL: str = "INFO"
    MAX_BATCH_SIZE: int = 100
    REQUEST_TIMEOUT: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
