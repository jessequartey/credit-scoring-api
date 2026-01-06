import json
import os
from typing import Dict, List, Any, Optional

class RuleEngine:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # Return a default empty config if file doesn't exist
            return {"rules": {"auto_reject": [], "auto_approve": [], "require_guarantor": [], "require_collateral": []}, "thresholds": {}}
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def evaluate_condition(self, condition: str, features: Dict[str, Any]) -> bool:
        """
        Safety note: This uses eval() which is generally dangerous. 
        In a production environment, use a proper expression parser like simpleeval.
        For this demo, we'll use eval with a restricted global environment.
        """
        try:
            # Create a clean safe names dict from features
            safe_names = {k: v for k, v in features.items() if not k.startswith('__')}
            return eval(condition, {"__builtins__": None}, safe_names)
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
            
    def check_rules(self, features: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            "auto_reject": [],
            "auto_approve": [],
            "require_guarantor": [],
            "require_collateral": [],
            "flags": [],
            "recommendations": []
        }
        
        rules = self.config.get("rules", {})
        
        # 1. Check auto_reject
        for rule in rules.get("auto_reject", []):
            if self.evaluate_condition(rule["condition"], features):
                results["auto_reject"].append(rule)
                results["recommendations"].append(rule["message"])
        
        if results["auto_reject"]:
            return results # Return early for rejections
            
        # 2. Check require_guarantor
        for rule in rules.get("require_guarantor", []):
            if self.evaluate_condition(rule["condition"], features):
                if not features.get("has_guarantor", False):
                    results["require_guarantor"].append(rule)
                    results["flags"].append(f"Guarantor Required: {rule['message']}")
                    
        # 3. Check require_collateral
        for rule in rules.get("require_collateral", []):
            if self.evaluate_condition(rule["condition"], features):
                if not features.get("has_collateral", False):
                    results["require_collateral"].append(rule)
                    results["flags"].append(f"Collateral Required: {rule['message']}")
                    
        # 4. Check auto_approve
        for rule in rules.get("auto_approve", []):
            if self.evaluate_condition(rule["condition"], features):
                results["auto_approve"].append(rule)
                results["recommendations"].append(f"Auto-approval criteria met: {rule['message']}")
                
        return results

    def get_thresholds(self) -> Dict[str, float]:
        return self.config.get("thresholds", {
            "min_credit_score": 0.5,
            "high_confidence_threshold": 0.8,
            "low_confidence_threshold": 0.4
        })
