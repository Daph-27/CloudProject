# train_model.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import joblib

# Azure ML Placeholder: You can use azureml-core to track parameters, logs, and models here.

def train():
    # 1. Load Data
    # Azure Blob Storage Placeholder: You can read from a Blob URL instead of a local file
    print("Loading data...")
    df = pd.read_csv('electricity_data.csv')
    
    # 2. Extract Features and Target
    X = df[['Units']]
    y = df['BillAmount']
    
    # 3. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train Model
    print("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    print(f"Model R2 Score: {r2:.4f}")
    
    # 6. Save Model
    joblib.dump(model, 'model.pkl')
    print("Model saved to model.pkl")
    
if __name__ == '__main__':
    train()
