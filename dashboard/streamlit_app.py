import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

st.set_page_config(page_title="Churn Prediction Dashboard", layout="wide")

@st.cache_resource
def load_model():
    candidates = [os.path.join("models", "best_model_pipeline.pkl"), "best_model_pipeline.pkl"]
    for p in candidates:
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return pickle.load(f)
    return None

model = load_model()

st.title("🔄 Customer Churn Prediction")

if model is None:
    st.warning("Model not found. First run: python -m src.train")

with st.form("customer_form"):
    st.subheader("Customer Information")
    c1, c2, c3 = st.columns(3)

    with c1:
        gender = st.selectbox("Gender", ["Male", "Female"])  # categorical
        SeniorCitizen = st.selectbox("Senior Citizen", [0, 1])
        Partner = st.selectbox("Partner", ["Yes", "No"])  # categorical
        Dependents = st.selectbox("Dependents", ["Yes", "No"])  # categorical
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0, value=65.0)
        TotalCharges = st.number_input("Total Charges", min_value=0.0, value=1500.0)

    with c2:
        PhoneService = st.selectbox("Phone Service", ["Yes", "No"])  # categorical
        MultipleLines = st.selectbox("Multiple Lines", ["No", "Yes"])  # categorical
        InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])  # categorical
        OnlineSecurity = st.selectbox("Online Security", ["No", "Yes"])  # categorical
        OnlineBackup = st.selectbox("Online Backup", ["No", "Yes"])  # categorical
        DeviceProtection = st.selectbox("Device Protection", ["No", "Yes"])  # categorical

    with c3:
        TechSupport = st.selectbox("Tech Support", ["No", "Yes"])  # categorical
        StreamingTV = st.selectbox("Streaming TV", ["No", "Yes"])  # categorical
        StreamingMovies = st.selectbox("Streaming Movies", ["No", "Yes"])  # categorical
        Contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])  # categorical
        PaperlessBilling = st.selectbox("Paperless Billing", ["Yes", "No"])  # categorical
        PaymentMethod = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
        ])  # categorical

    submitted = st.form_submit_button("Predict")

if submitted:
    input_df = pd.DataFrame([{ 
        'gender': gender,
        'SeniorCitizen': SeniorCitizen,
        'Partner': Partner,
        'Dependents': Dependents,
        'tenure': tenure,
        'PhoneService': PhoneService,
        'MultipleLines': MultipleLines,
        'InternetService': InternetService,
        'OnlineSecurity': OnlineSecurity,
        'OnlineBackup': OnlineBackup,
        'DeviceProtection': DeviceProtection,
        'TechSupport': TechSupport,
        'StreamingTV': StreamingTV,
        'StreamingMovies': StreamingMovies,
        'Contract': Contract,
        'PaperlessBilling': PaperlessBilling,
        'PaymentMethod': PaymentMethod,
        'MonthlyCharges': MonthlyCharges,
        'TotalCharges': TotalCharges,
    }])

    if model is None:
        st.error("Model not loaded.")
    else:
        try:
            pred = int(model.predict(input_df)[0])
            proba = float(model.predict_proba(input_df)[0][1])
            st.subheader("Prediction Result")
            colA, colB, colC = st.columns(3)
            with colA:
                st.metric("Churn", "Yes" if pred == 1 else "No")
            with colB:
                st.metric("Probability", f"{proba:.1%}")
            with colC:
                risk = "High" if proba > 0.7 else "Medium" if proba > 0.3 else "Low"
                st.metric("Risk Level", risk)
        except Exception as e:
            st.error(f"Prediction failed: {e}")
