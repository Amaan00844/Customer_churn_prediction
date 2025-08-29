import os
import sys
import argparse
import warnings
import pickle
from typing import List, Optional

import numpy as np
import pandas as pd

from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt


warnings.filterwarnings("ignore", category=ConvergenceWarning)


def ensure_dirs(paths: List[str]) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def resolve_ohe() -> OneHotEncoder:
    """Create a OneHotEncoder compatible with multiple scikit-learn versions."""
    try:
        # scikit-learn >= 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        # scikit-learn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def find_data_file(user_path: Optional[str] = None) -> str:
    """Try common locations to find the Telco dataset.

    Order of precedence:
      1) --data-path argument if provided
      2) ./data/Telco_Customer_Churn_Dataset.csv
      3) ./Telco_Customer_Churn_Dataset.csv
      4) Windows Downloads path observed in your environment
    """
    candidates: List[str] = []
    if user_path:
        candidates.append(user_path)

    candidates.extend([
        os.path.join("data", "Telco_Customer_Churn_Dataset.csv"),
        "Telco_Customer_Churn_Dataset.csv",
        # Observed in environment_details (mind the double spaces before (1))
        r"C:\\Users\\user\\Downloads\\Telco_Customer_Churn_Dataset  (1).csv",
    ])

    for c in candidates:
        if os.path.isfile(c):
            return c

    raise FileNotFoundError(
        "Could not locate dataset. Pass --data-path or place the CSV at ./data/Telco_Customer_Churn_Dataset.csv"
    )


def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Standard fixes for Telco dataset
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = (
            df["TotalCharges"].replace(" ", np.nan).apply(pd.to_numeric, errors="coerce")
        )

    # Drop ID column if present
    for id_col in ["customerID", "CustomerID", "customer_id"]:
        if id_col in df.columns:
            df = df.drop(columns=[id_col])
            break

    # Ensure Churn exists and is numeric 0/1
    if "Churn" not in df.columns:
        raise ValueError("No 'Churn' column found in dataset.")

    if df["Churn"].dtype == object:
        # Common mapping Yes/No -> 1/0
        df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # If still non-numeric, try to coerce
    if not np.issubdtype(df["Churn"].dtype, np.number):
        df["Churn"] = pd.to_numeric(df["Churn"], errors="coerce")

    # Final sanity drop NA rows in target
    df = df.dropna(subset=["Churn"])  # just in case
    df["Churn"] = df["Churn"].astype(int)

    return df


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", resolve_ohe()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    return preprocessor


def train_and_eval_models(X_train_sel, X_test_sel, y_train, y_test):
    models = [
        (LogisticRegression(max_iter=1000, random_state=42), "LogisticRegression"),
        (RandomForestClassifier(n_estimators=200, random_state=42), "RandomForest"),
        (GradientBoostingClassifier(n_estimators=200, random_state=42), "GradientBoosting"),
    ]

    results = []
    for mdl, name in models:
        print(f"\nTraining {name} ...")
        mdl.fit(X_train_sel, y_train)
        preds = mdl.predict(X_test_sel)
        if hasattr(mdl, "predict_proba"):
            probs = mdl.predict_proba(X_test_sel)[:, 1]
        else:
            # fallback using decision function if available
            if hasattr(mdl, "decision_function"):
                # scale to [0,1]
                scores = mdl.decision_function(X_test_sel)
                probs = (scores - scores.min()) / (scores.max() - scores.min() + 1e-12)
            else:
                # worst-case fallback
                probs = preds.astype(float)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        roc = roc_auc_score(y_test, probs)
        res = {"model": name, "acc": acc, "prec": prec, "rec": rec, "f1": f1, "roc_auc": roc, "estimator": mdl}
        results.append(res)
        print(f"{name} - acc: {acc:.4f}, prec: {prec:.4f}, rec: {rec:.4f}, f1: {f1:.4f}, roc_auc: {roc:.4f}")

    best = max(results, key=lambda r: r["roc_auc"])
    print("\nBest model by ROC AUC:", best["model"], "ROC AUC:", f"{best['roc_auc']:.4f}")
    return results, best


def main(args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Train churn prediction models and persist best pipeline.")
    parser.add_argument("--data-path", type=str, default=None, help="Path to Telco CSV file.")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test size split fraction.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducibility.")
    ns = parser.parse_args(args=args)

    # Prepare output dirs
    models_dir = os.path.join("models")
    reports_dir = os.path.join("reports")
    figures_dir = os.path.join(reports_dir, "figures")
    ensure_dirs([models_dir, reports_dir, figures_dir])

    # Locate and load data
    csv_path = find_data_file(ns.data_path)
    print(f"Dataset: {csv_path}")
    df = load_and_clean_data(csv_path)
    print("Dataset loaded. Shape:", df.shape)

    # Split
    if "Churn" not in df.columns:
        raise ValueError("Dataset must contain 'Churn' column after loading.")

    X = df.drop(columns=["Churn"])
    y = df["Churn"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ns.test_size, stratify=y, random_state=ns.random_state
    )
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    # Build preprocessing
    preprocessor = build_preprocessor(X)

    # Fit and transform train/test
    print("Fitting preprocessor and transforming data ...")
    X_train_p = preprocessor.fit_transform(X_train)
    X_test_p = preprocessor.transform(X_test)

    # Feature selection
    k = min(20, X_train_p.shape[1])
    selector = SelectKBest(score_func=f_classif, k=k)
    selector.fit(X_train_p, y_train)
    X_train_sel = selector.transform(X_train_p)
    X_test_sel = selector.transform(X_test_p)
    print("Feature selection complete. Selected features:", X_train_sel.shape[1])

    # Train and evaluate candidate models
    results, best = train_and_eval_models(X_train_sel, X_test_sel, y_train, y_test)

    # Build final pipeline and fit on train set
    final_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("selector", selector),
        ("estimator", best["estimator"]),
    ])

    print("\nFitting final pipeline on training data ...")
    final_pipeline.fit(X_train, y_train)

    # Persist model and reports
    model_path = os.path.join(models_dir, "best_model_pipeline.pkl")
    report_path = os.path.join(reports_dir, "model_evaluation_report.csv")
    fig_path = os.path.join(figures_dir, "roc_curve.png")

    with open(model_path, "wb") as f:
        pickle.dump(final_pipeline, f)

    report_df = pd.DataFrame([
        {
            "model": r["model"],
            "accuracy": r["acc"],
            "precision": r["prec"],
            "recall": r["rec"],
            "f1": r["f1"],
            "roc_auc": r["roc_auc"],
        }
        for r in results
    ])
    report_df.to_csv(report_path, index=False)

    # ROC curve using final pipeline on raw X_test for consistency
    print("Generating ROC curve ...")
    y_proba = final_pipeline.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"{best['model']} (AUC={roc_auc_score(y_test, y_proba):.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.title("ROC Curve - Best Model")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()

    print("\nFiles saved:")
    print(" -", model_path)
    print(" -", report_path)
    print(" -", fig_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
