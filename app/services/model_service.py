import joblib
import json
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from app.config import settings
from app.utils.preprocessing import create_derived_features

class ModelService:
    def __init__(self):
        self.model = None
        self.metrics = {}
        self.feature_importance = {}
        self.model_loaded = False
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = joblib.load(settings.MODEL_PATH)
                self.model_loaded = True
                print(f"Model loaded from {settings.MODEL_PATH}")
            else:
                print(f"Warning: Model file not found at {settings.MODEL_PATH}")

            metrics_path = os.path.join(os.path.dirname(settings.MODEL_PATH), 'model_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)

            importance_path = os.path.join(os.path.dirname(settings.MODEL_PATH), 'feature_importance.json')
            if os.path.exists(importance_path):
                with open(importance_path, 'r') as f:
                    self.feature_importance = json.load(f)
        except Exception as e:
            print(f"Error loading model artifacts: {e}")

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.model_loaded:
            raise Exception("Model is not loaded")

        # Convert input dict to DataFrame
        df = pd.DataFrame([input_data])
        
        # Apply feature engineering
        df_engineered = create_derived_features(df)
        
        # We need to ensure we drop the same columns as during training
        # Usually client_id and credit_worthy (target)
        cols_to_drop = ['client_id'] if 'client_id' in df_engineered.columns else []
        X = df_engineered.drop(columns=cols_to_drop)
        
        # Predict probability
        prob = self.model.predict_proba(X)[0, 1]
        
        # Also get intermediate engineered features for rule engine
        engineered_features = df_engineered.iloc[0].to_dict()
        
        return {
            "score": float(prob),
            "engineered_features": engineered_features
        }

    def get_top_factors(self, n: int = 5) -> List[Dict[str, float]]:
        sorted_importance = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        return [{"factor": k, "importance": v} for k, v in sorted_importance[:n]]

    def get_info(self) -> Dict[str, Any]:
        return {
            "loaded": self.model_loaded,
            "metrics": self.metrics,
            "top_factors": self.get_top_factors(10)
        }

model_service = ModelService()
