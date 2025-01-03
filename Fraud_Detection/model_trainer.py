import pandas as pd
import numpy as np
import seaborn as sns
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

import matplotlib.pyplot as plt

from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)

def preprocess_data(data):
    """
    Preprocess the dataset by transforming dates and creating new features.
    """
    data['processed_at'] = pd.to_datetime(data['processed_at'])
    data['hour'] = data['processed_at'].dt.hour
    data['day_of_week'] = data['processed_at'].dt.dayofweek
    data['month'] = data['processed_at'].dt.month
    data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
    
    X = data.drop(['is_fraud', 'processed_at'], axis=1)
    y = data['is_fraud']
    
    return X, y

def create_pipeline(categorical_cols, numerical_cols):
    """
    Create a preprocessing and modeling pipeline.
    """
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    numerical_transformer = StandardScaler()
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_cols),
            ('num', numerical_transformer, numerical_cols)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', LogisticRegression(C=1e5, solver='liblinear'))
    ])
    
    return pipeline

def plot_roc_curve(y_test, y_proba):
    """
    Plot the ROC curve.
    """
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc_score_value = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc_score_value:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
             label='Random Guessing')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=14)
    plt.ylabel('True Positive Rate', fontsize=14)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=16)
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.show()

def plot_precision_recall_curve(y_test, y_proba):
    """
    Plot the Precision-Recall curve.
    """
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    average_precision = average_precision_score(y_test, y_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', 
             lw=2, label=f'PR curve (AP = {average_precision:.2f})')
    plt.xlabel('Recall', fontsize=14)
    plt.ylabel('Precision', fontsize=14)
    plt.title('Precision-Recall (PR) Curve', fontsize=16)
    plt.legend(loc="lower left")
    plt.grid(alpha=0.3)
    plt.show()

def plot_confusion_matrix(y_test, y_pred):
    """
    Plot the confusion matrix.
    """
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.xlabel('Predicted Label', fontsize=14)
    plt.ylabel('True Label', fontsize=14)
    plt.title('Confusion Matrix', fontsize=16)
    plt.show()

def main():
    # Load data
    data = pd.read_csv("zim_credit_card_fraud_dataset.csv")
    
    # Preprocess data
    X, y = preprocess_data(data)
    
    # Define column types
    categorical_cols = ['merchant', 'category', 'gender', 'city', 'province', 'job']
    numerical_cols = [col for col in X.columns if col not in categorical_cols]
    
    # Create and train pipeline
    pipeline = create_pipeline(categorical_cols, numerical_cols)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.35, random_state=42, stratify=y
    )
    
    pipeline.fit(X_train, y_train)
    
    # Make predictions
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    # Print metrics
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("\nROC-AUC Score:", roc_auc_score(y_test, y_proba))
    
    # Plot evaluation curves
    plot_roc_curve(y_test, y_proba)
    plot_precision_recall_curve(y_test, y_proba)
    plot_confusion_matrix(y_test, y_pred)
    
    # Save model
    joblib.dump(pipeline, 'zwg_credit_card_fraud_pipeline.pkl')
    print("\nModel saved to 'zwg_credit_card_fraud_pipeline.pkl'")

if __name__ == "__main__":
    main()
