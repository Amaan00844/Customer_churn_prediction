from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import pickle
import pandas as pd

APP_TITLE = "Churn Prediction API"
APP_VERSION = "1.0.0"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

MODEL_PATH_CANDIDATES = [
    os.path.join("models", "best_model_pipeline.pkl"),
    "best_model_pipeline.pkl",
]

model = None
for p in MODEL_PATH_CANDIDATES:
    if os.path.isfile(p):
        with open(p, "rb") as f:
            model = pickle.load(f)
        print(f"Loaded model from {p}")
        break


class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(customer: CustomerData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")

    df = pd.DataFrame([customer.dict()])
    try:
        pred = model.predict(df)[0]
        proba = float(model.predict_proba(df)[0][1])
        risk = "High" if proba > 0.7 else "Medium" if proba > 0.3 else "Low"
        return {
            "churn_prediction": bool(pred),
            "churn_probability": proba,
            "risk_level": risk,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
