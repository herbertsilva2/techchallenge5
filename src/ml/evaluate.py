"""
Módulo de Avaliação de Modelos de Machine Learning (Guardiã AI)
Calcula métricas estatísticas e clínicas (Accuracy, Precision, Recall, F1, ROC-AUC, Specificity, Brier Score),
gerando relatórios comparativos e salvando métricas consolidadas em JSON.
"""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    brier_score_loss,
)


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    threshold: float = 0.50,
    model_name: str = "Model",
) -> Dict[str, Any]:
    """
    Avalia um modelo de classificação gerando métricas completas com foco clínico.
    """
    # Obter probabilidades para a classe positiva
    if hasattr(model, "predict_proba"):
        y_probs = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        decision = model.decision_function(X_test)
        y_probs = 1 / (1 + np.exp(-decision))
    else:
        y_probs = model.predict(X_test).astype(float)

    # Classificação com limiar configurável
    y_pred = (y_probs >= threshold).astype(int)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    try:
        auc = float(roc_auc_score(y_test, y_probs))
    except Exception:
        auc = 0.5

    brier = float(brier_score_loss(y_test, y_probs))
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    return {
        "model_name": model_name,
        "decision_threshold": threshold,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "clinical_impact_note": (
            f"Sensibilidade (Recall) de {rec*100:.1f}% com {fn} falsos negativos. "
            "Na triagem obstétrica/materna, minimizar falsos negativos é vital para "
            "garantir encaminhamento precoce e acompanhamento oportuno."
        ),
    }


def compare_models(evaluations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compara múltiplos modelos e seleciona o campeão com base em critério clínico (priorizando Recall e F1-Score).
    """
    best_model_name = None
    best_score = -1.0

    for name, metrics in evaluations.items():
        # Score ponderado clínico: 50% Recall + 30% ROC-AUC + 20% F1-Score
        clinical_score = (
            0.50 * metrics.get("recall", 0)
            + 0.30 * metrics.get("roc_auc", 0)
            + 0.20 * metrics.get("f1_score", 0)
        )
        if clinical_score > best_score:
            best_score = clinical_score
            best_model_name = name

    return {
        "models": evaluations,
        "champion_model": best_model_name,
        "selection_criteria": "Score clínico ponderado (50% Recall + 30% ROC-AUC + 20% F1-Score)",
    }
