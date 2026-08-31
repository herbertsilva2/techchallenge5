"""
Módulo de Treinamento Comparativo de Modelos de Machine Learning (Guardiã AI)
Treina múltiplos algoritmos (Random Forest, XGBoost, Regressão Logística),
aplica validação cruzada, salva os artefatos serializados e gera o sumário de métricas.
"""

import json
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False

from src.config import (
    MODEL_XGBOOST_PATH,
    MODEL_RF_PATH,
    MODEL_LR_PATH,
    METRICS_SUMMARY_PATH,
    RANDOM_STATE,
    DECISION_THRESHOLD_HIGH_RECALL,
)
from src.ml.dataset import get_train_test_data
from src.ml.evaluate import evaluate_model, compare_models


def train_and_evaluate_all():
    """
    Executa o ciclo completo de treinamento, avaliação comparativa e salvamento dos modelos.
    """
    print("Iniciando preparação dos dados de treino e teste...")
    data = get_train_test_data(fit_scaler=True)
    X_train = data["X_train"]
    X_test = data["X_test"]
    X_train_scaled = data["X_train_scaled"]
    X_test_scaled = data["X_test_scaled"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    print(f"Total amostras: {len(X_train) + len(X_test)} | Treino: {len(X_train)} | Teste: {len(X_test)}")
    print(f"Distribuição de classes no treino: {dict(zip(*np.unique(y_train, return_counts=True)))}")

    # 1. Modelo A: Random Forest Classifier
    print("\n--- Treinando Modelo 1: Random Forest Classifier ---")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    rf_model.fit(X_train, y_train)
    rf_metrics = evaluate_model(
        rf_model,
        X_test,
        y_test,
        threshold=DECISION_THRESHOLD_HIGH_RECALL,
        model_name="Random Forest",
    )
    joblib.dump(rf_model, MODEL_RF_PATH)
    print(f"Random Forest - Recall: {rf_metrics['recall']} | F1: {rf_metrics['f1_score']} | ROC-AUC: {rf_metrics['roc_auc']}")

    # 2. Modelo B: Gradient Boosting / XGBoost Classifier
    print("\n--- Treinando Modelo 2: Gradient Boosting / XGBoost Classifier ---")
    if HAS_XGBOOST:
        gb_model = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            scale_pos_weight=1.5,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
        )
        model_label = "XGBoost"
    else:
        gb_model = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.85,
            random_state=RANDOM_STATE,
        )
        model_label = "Gradient Boosting"

    gb_model.fit(X_train, y_train)
    gb_metrics = evaluate_model(
        gb_model,
        X_test,
        y_test,
        threshold=DECISION_THRESHOLD_HIGH_RECALL,
        model_name=model_label,
    )
    joblib.dump(gb_model, MODEL_XGBOOST_PATH)
    print(f"{model_label} - Recall: {gb_metrics['recall']} | F1: {gb_metrics['f1_score']} | ROC-AUC: {gb_metrics['roc_auc']}")

    # 3. Modelo C: Regressão Logística (Baseline Linear)
    print("\n--- Treinando Modelo 3: Regressão Logística (Baseline) ---")
    lr_model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
    )
    lr_model.fit(X_train_scaled, y_train)
    lr_metrics = evaluate_model(
        lr_model,
        X_test_scaled,
        y_test,
        threshold=DECISION_THRESHOLD_HIGH_RECALL,
        model_name="Logistic Regression",
    )
    joblib.dump(lr_model, MODEL_LR_PATH)
    print(f"Logistic Regression - Recall: {lr_metrics['recall']} | F1: {lr_metrics['f1_score']} | ROC-AUC: {lr_metrics['roc_auc']}")

    # Comparativo consolidado
    evaluations = {
        "Random Forest": rf_metrics,
        "XGBoost": gb_metrics,
        "Logistic Regression": lr_metrics,
    }

    comparison = compare_models(evaluations)

    # Salvar métricas consolidadas em JSON
    METRICS_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print(f"\nModelo Campeão Selecionado: {comparison['champion_model']}")
    print(f"Relatório de métricas salvo em: {METRICS_SUMMARY_PATH}")

    return comparison


if __name__ == "__main__":
    import numpy as np
    train_and_evaluate_all()
