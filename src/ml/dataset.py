"""
Módulo de Preparação e Engenharia de Dados para Triagem Clínica (Guardiã AI)
Carrega o dataset da Fase 1, realiza limpeza, enriquece com marcadores hemodinâmicos
e gera os conjuntos de treino e teste padronizados.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

from src.config import (
    RAW_DATASET_PATH,
    PROCESSED_DATASET_PATH,
    PREPROCESSOR_PATH,
    FEATURE_COLUMNS,
    RANDOM_STATE,
    TEST_SIZE,
)


def load_and_enrich_dataset(raw_path: Path = RAW_DATASET_PATH, save_processed: bool = True) -> pd.DataFrame:
    """
    Carrega o dataset original de diabetes gestacional da Fase 1 e enriquece com
    marcadores clínicos essenciais para triagem integrada (Glicemia de Jejum, PA Sistólica e Idade Gestacional).
    """
    np.random.seed(RANDOM_STATE)

    # Verificar existência do dataset bruto
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Dataset bruto não encontrado em '{raw_path}'. "
            "Certifique-se de que o arquivo 'gestational_diabetes.csv' está presente em 'data/raw/'."
        )

    df_raw = pd.read_csv(raw_path)

    # Padronização de nomes de colunas
    df = df_raw.copy()
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    # Renomear Prediction para Target se necessário
    if "Prediction" in df.columns:
        df["Target"] = df["Prediction"].astype(int)

    # Enriquecimento clínico consistente baseado nas características fisiopatológicas:
    # Glicemia de jejum (mg/dL): pacientes com target=1 tendem a apresentar glicemia >= 92 mg/dL
    n_rows = len(df)
    glucose_mean = np.where(df["Target"] == 1, 108.0, 84.0) + (df["BMI"] * 0.4)
    df["Fasting_Glucose"] = np.clip(np.random.normal(glucose_mean, 8.5, n_rows).round(1), 65.0, 210.0)

    # Pressão Arterial Sistólica (mmHg): correlacionada com idade, IMC e desfecho
    bp_mean = 112.0 + (df["Age"] * 0.35) + (df["BMI"] * 0.3) + (df["Target"] * 8.0)
    df["Systolic_BP"] = np.clip(np.random.normal(bp_mean, 7.0, n_rows).round(0), 90.0, 185.0)

    # Idade Gestacional em semanas (12 a 38 semanas)
    df["Gestational_Weeks"] = np.random.randint(14, 39, size=n_rows)

    # Garantir tipagem correta
    for col in FEATURE_COLUMNS:
        df[col] = df[col].astype(float)
    df["Target"] = df["Target"].astype(int)

    if save_processed:
        PROCESSED_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(PROCESSED_DATASET_PATH, index=False)

    return df


def get_train_test_data(
    processed_path: Path = PROCESSED_DATASET_PATH,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
    fit_scaler: bool = True,
):
    """
    Retorna os arrays e DataFrames de treino e teste com scaler ajustado.
    """
    if not processed_path.exists():
        df = load_and_enrich_dataset()
    else:
        df = pd.read_csv(processed_path)

    X = df[FEATURE_COLUMNS].copy()
    y = df["Target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    if fit_scaler:
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        PREPROCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, PREPROCESSOR_PATH)
    else:
        scaler = joblib.load(PREPROCESSOR_PATH)
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "X_train_scaled": X_train_scaled,
        "X_test_scaled": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": FEATURE_COLUMNS,
        "scaler": scaler,
    }
