import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from app.utils.preprocessing import create_derived_features, get_preprocessing_pipeline

def train_model():
    print("Loading data...")
    if not os.path.exists('data/training_data.csv'):
        print("Error: data/training_data.csv not found. Run generate_training_data.py first.")
        return
    
    df = pd.read_csv('data/training_data.csv')
    
    print("Engineering features...")
    df = create_derived_features(df)
    
    # Define features and target
    X = df.drop(columns=['client_id', 'credit_worthy'])
    y = df['credit_worthy']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Creating preprocessing pipeline...")
    preprocessor = get_preprocessing_pipeline()
    
    print("Training Random Forest model...")
    # Model parameters optimized for VPS
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    
    # Create full pipeline
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])
    
    # Fit model
    clf.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'f1_score': float(f1_score(y_test, y_pred)),
        'auc_roc': float(roc_auc_score(y_test, y_prob))
    }
    
    print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    # Save artifacts
    os.makedirs('ml/models', exist_ok=True)
    
    # Save the full pipeline (preprocessor + classifier)
    joblib.dump(clf, 'ml/models/credit_model.joblib')
    
    # Save metrics
    with open('ml/models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
        
    # Get feature importance
    # We need to get feature names after one-hot encoding
    cat_features = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out()
    num_features = preprocessor.transformers_[0][2]
    bin_features = preprocessor.transformers_[2][2]
    
    feature_names = list(num_features) + list(cat_features) + list(bin_features)
    importances = model.feature_importances_
    
    feature_importance_dict = dict(zip(feature_names, [float(i) for i in importances]))
    # Sort by importance
    feature_importance_dict = {k: v for k, v in sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True)}
    
    with open('ml/models/feature_importance.json', 'w') as f:
        json.dump(feature_importance_dict, f, indent=2)
        
    print("Model and artifacts saved to ml/models/")

if __name__ == "__main__":
    from sklearn.pipeline import Pipeline # Need to import here for main block
    train_model()
