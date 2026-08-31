"""
Módulo de Predição em Tempo Real (Guardiã AI)
Carrega os modelos treinados e realiza inferência clínica estruturada com estratificação de risco.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd
import joblib

from src.config import (
    MODEL_XGBOOST_PATH,
    MODEL_RF_PATH,
    MODEL_LR_PATH,
    PREPROCESSOR_PATH,
    FEATURE_COLUMNS,
    DECISION_THRESHOLD_HIGH_RECALL,
)


def load_model_and_preprocessor(model_type: str = "xgboost"):
    """
    Carrega o modelo solicitado e o scaler de pré-processamento.
    """
    model_type = model_type.lower()
    if "rf" in model_type or "random" in model_type:
        model = joblib.load(MODEL_RF_PATH)
        is_linear = False
    elif "logistic" in model_type or "lr" in model_type:
        model = joblib.load(MODEL_LR_PATH)
        is_linear = True
    else:
        model = joblib.load(MODEL_XGBOOST_PATH)
        is_linear = False

    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor, is_linear


def prepare_input_dataframe(patient_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Converte um dicionário de dados do paciente em um DataFrame padronizado com as colunas esperadas.
    """
    # Mapeamento e normalização de chaves
    data_normalized = {}
    key_mapping = {
        "age": "Age",
        "pregnancy_no": "Pregnancy_No",
        "pregnancy_count": "Pregnancy_No",
        "weight": "Weight",
        "height": "Height",
        "bmi": "BMI",
        "heredity": "Heredity",
        "fasting_glucose": "Fasting_Glucose",
        "glucose": "Fasting_Glucose",
        "systolic_bp": "Systolic_BP",
        "blood_pressure": "Systolic_BP",
        "gestational_weeks": "Gestational_Weeks",
        "weeks": "Gestational_Weeks",
    }

    for k, v in patient_data.items():
        k_clean = k.lower().strip()
        target_col = key_mapping.get(k_clean, k)
        data_normalized[target_col] = float(v)

    # Calcular BMI automaticamente se não fornecido
    if "BMI" not in data_normalized or data_normalized["BMI"] <= 0:
        weight = data_normalized.get("Weight", 65.0)
        height_cm = data_normalized.get("Height", 160.0)
        height_m = height_cm / 100.0 if height_cm > 3.0 else height_cm
        data_normalized["BMI"] = round(weight / (height_m ** 2), 1)

    # Preencher colunas faltantes com valores padrão clínicos
    defaults = {
        "Age": 28.0,
        "Pregnancy_No": 1.0,
        "Weight": 65.0,
        "Height": 160.0,
        "BMI": 25.4,
        "Heredity": 0.0,
        "Fasting_Glucose": 88.0,
        "Systolic_BP": 115.0,
        "Gestational_Weeks": 24.0,
    }

    for col in FEATURE_COLUMNS:
        if col not in data_normalized:
            data_normalized[col] = defaults[col]

    df = pd.DataFrame([data_normalized])[FEATURE_COLUMNS]
    return df


def predict_risk(
    patient_data: Union[Dict[str, Any], pd.DataFrame],
    model_type: str = "xgboost",
    threshold: float = DECISION_THRESHOLD_HIGH_RECALL,
) -> Dict[str, Any]:
    """
    Executa a predição de risco clínico, retornando probabilidade, nível de alerta e escore.
    """
    if isinstance(patient_data, dict):
        df_input = prepare_input_dataframe(patient_data)
    else:
        df_input = patient_data[FEATURE_COLUMNS].copy()

    model, preprocessor, is_linear = load_model_and_preprocessor(model_type)

    if is_linear:
        X_infer = preprocessor.transform(df_input)
    else:
        X_infer = df_input

    # Probabilidade
    if hasattr(model, "predict_proba"):
        prob_positive = float(model.predict_proba(X_infer)[0, 1])
    else:
        prob_positive = float(model.predict(X_infer)[0])

    is_high_risk = prob_positive >= threshold

    # Estratificação de Risco Clínico
    if prob_positive >= 0.70:
        risk_level = "Alto Risco Obstétrico"
        risk_color = "#E63946"  # Vermelho
        urgency = "Emergência / Muito Urgente"
    elif prob_positive >= threshold:
        risk_level = "Risco Moderado"
        risk_color = "#F4A261"  # Laranja/Amarelo
        urgency = "Urgente / Atenção Especial"
    else:
        risk_level = "Baixo Risco / Habitual"
        risk_color = "#2A9D8F"  # Verde
        urgency = "Rotina / Pré-natal Habitual"

    return {
        "model_used": model_type.upper(),
        "probability": round(prob_positive, 4),
        "probability_percentage": f"{prob_positive * 100:.1f}%",
        "is_high_risk": is_high_risk,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "urgency_classification": urgency,
        "decision_threshold_used": threshold,
        "patient_features": df_input.to_dict(orient="records")[0],
    }
