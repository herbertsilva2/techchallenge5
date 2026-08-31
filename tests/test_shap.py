"""
Testes unitários para o módulo de Interpretabilidade SHAP (Guardiã AI).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ml.explainer import explain_prediction_shap, create_shap_waterfall_figure


def test_shap_explanation_structure():
    """Verifica a estrutura dos valores SHAP e top fatores retornados."""
    sample_patient = {
        "Age": 35,
        "Pregnancy_No": 3,
        "Weight": 85.0,
        "Height": 156.0,
        "BMI": 34.9,
        "Heredity": 1,
        "Fasting_Glucose": 115.0,
        "Systolic_BP": 145.0,
        "Gestational_Weeks": 28,
    }

    res = explain_prediction_shap(sample_patient, model_type="xgboost")
    assert "base_value" in res
    assert "contributions" in res
    assert "top_risk_factors" in res
    assert "top_protective_factors" in res

    # Deve ter 9 contribuições (1 para cada feature)
    assert len(res["contributions"]) == 9

    # Verificar chaves das contribuições
    first_contrib = res["contributions"][0]
    assert "feature" in first_contrib
    assert "feature_label" in first_contrib
    assert "shap_value" in first_contrib
    assert "impact_direction" in first_contrib


def test_shap_waterfall_figure_generation():
    """Verifica se a figura do gráfico waterfall é gerada corretamente."""
    sample_patient = {
        "Age": 28,
        "Pregnancy_No": 1,
        "Weight": 62.0,
        "Height": 165.0,
        "BMI": 22.8,
        "Heredity": 0,
        "Fasting_Glucose": 85.0,
        "Systolic_BP": 115.0,
        "Gestational_Weeks": 20,
    }

    fig = create_shap_waterfall_figure(sample_patient, model_type="xgboost")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
