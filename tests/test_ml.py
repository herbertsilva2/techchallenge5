"""
Testes unitários para o módulo de Machine Learning (Guardiã AI).
"""

import pytest
import numpy as np
import pandas as pd

from src.config import FEATURE_COLUMNS
from src.ml.dataset import load_and_enrich_dataset, get_train_test_data
from src.ml.predictor import predict_risk, prepare_input_dataframe
from src.ml.evaluate import evaluate_model, compare_models


def test_dataset_loading_and_enrichment():
    """Verifica se o dataset é carregado e enriquecido com todas as colunas necessárias."""
    df = load_and_enrich_dataset(save_processed=False)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in FEATURE_COLUMNS:
        assert col in df.columns, f"Coluna {col} ausente no dataset enriquecido."
    assert "Target" in df.columns
    assert df["Target"].isin([0, 1]).all()


def test_train_test_split_shapes():
    """Verifica as dimensões dos splits de treino e teste."""
    data = get_train_test_data()
    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    assert len(X_train) + len(X_test) > 0
    assert len(X_train) == len(y_train)
    assert len(X_test) == len(y_test)
    assert data["X_train_scaled"].shape == X_train.shape


def test_prepare_input_dataframe():
    """Verifica a normalização de dicionários de entrada e cálculo de IMC."""
    raw_input = {
        "age": 30,
        "weight": 70.0,
        "height": 160.0,
        "glucose": 95.0,
        "blood_pressure": 120.0,
        "weeks": 22,
    }
    df = prepare_input_dataframe(raw_input)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == FEATURE_COLUMNS
    assert df["Age"].iloc[0] == 30.0
    # IMC: 70 / (1.6^2) = 27.34 -> 27.3
    assert abs(df["BMI"].iloc[0] - 27.3) < 0.2


@pytest.mark.parametrize("model_type", ["xgboost", "random_forest", "logistic_regression"])
def test_predict_risk_models(model_type):
    """Testa a inferência para os diferentes algoritmos."""
    sample_patient = {
        "Age": 33,
        "Pregnancy_No": 2,
        "Weight": 72.0,
        "Height": 162.0,
        "BMI": 27.4,
        "Heredity": 1,
        "Fasting_Glucose": 105.0,
        "Systolic_BP": 130.0,
        "Gestational_Weeks": 24,
    }
    res = predict_risk(sample_patient, model_type=model_type)
    assert "probability" in res
    assert 0.0 <= res["probability"] <= 1.0
    assert "risk_level" in res
    assert "urgency_classification" in res
    assert isinstance(res["is_high_risk"], bool)


def test_evaluate_model_metrics():
    """Verifica o cálculo de métricas estatísticas e clínicas."""
    class DummyModel:
        def predict_proba(self, X):
            # Retorna probabilidade alta para classe 1
            return np.array([[0.1, 0.9] if x[0] > 0.5 else [0.8, 0.2] for x in X])

    X_dummy = np.array([[0.8], [0.2], [0.9], [0.1]])
    y_dummy = np.array([1, 0, 1, 0])

    metrics = evaluate_model(DummyModel(), X_dummy, y_dummy, threshold=0.5, model_name="Dummy")
    assert metrics["accuracy"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert "confusion_matrix" in metrics
