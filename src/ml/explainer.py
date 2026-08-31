"""
Módulo de Interpretabilidade e Explicabilidade Clínica com SHAP (Guardiã AI)
Calcula valores de SHAP (TreeExplainer / LinearExplainer), decompõe o impacto de cada
variável clínica na predição e gera visualizações gráficas (Waterfall, Summary, Bar Plots).
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")  # Backend não interativo para servidor
import matplotlib.pyplot as plt

from src.config import FEATURE_COLUMNS
from src.ml.predictor import load_model_and_preprocessor, prepare_input_dataframe


def get_feature_translations() -> Dict[str, str]:
    """Mapeamento de nomes de features para termos médicos humanizados em pt-BR."""
    return {
        "Age": "Idade Materna",
        "Pregnancy_No": "Nº de Gestações Anteriores",
        "Weight": "Peso Corporal (kg)",
        "Height": "Altura (cm)",
        "BMI": "Índice de Massa Corporal (IMC)",
        "Heredity": "Histórico Familiar de Diabetes",
        "Fasting_Glucose": "Glicemia de Jejum (mg/dL)",
        "Systolic_BP": "Pressão Arterial Sistólica (mmHg)",
        "Gestational_Weeks": "Idade Gestacional (Semanas)",
    }


def explain_prediction_shap(
    patient_data: Dict[str, Any],
    model_type: str = "xgboost",
) -> Dict[str, Any]:
    """
    Gera a explicação SHAP para uma paciente específica, identificando os principais
    fatores que aumentaram ou diminuíram o risco estimado.
    """
    df_input = prepare_input_dataframe(patient_data)
    model, preprocessor, is_linear = load_model_and_preprocessor(model_type)
    translations = get_feature_translations()

    if is_linear:
        X_scaled = preprocessor.transform(df_input)
        explainer = shap.LinearExplainer(model, X_scaled)
        shap_values_obj = explainer(X_scaled)
        shap_vals = shap_values_obj.values[0]
        base_val = float(shap_values_obj.base_values[0])
    else:
        explainer = shap.TreeExplainer(model)
        shap_values_obj = explainer(df_input.values)
        if len(shap_values_obj.values.shape) == 3:
            # Caso multiclasse ou saída binária com duas classes
            shap_vals = shap_values_obj.values[0, :, 1]
            base_val = float(shap_values_obj.base_values[0, 1])
        else:
            shap_vals = shap_values_obj.values[0]
            base_val = float(shap_values_obj.base_values[0])

    feature_names = FEATURE_COLUMNS
    feature_values = df_input.iloc[0].to_dict()

    # Montar lista detalhada de contribuições
    contributions: List[Dict[str, Any]] = []
    for i, name in enumerate(feature_names):
        sv = float(shap_vals[i])
        raw_v = float(feature_values[name])
        contributions.append({
            "feature": name,
            "feature_label": translations.get(name, name),
            "value": raw_v,
            "shap_value": round(sv, 4),
            "impact_direction": "Aumenta Risco" if sv > 0 else "Diminui Risco",
            "abs_impact": abs(sv),
        })

    # Ordenar por magnitude absoluta de impacto
    contributions_sorted = sorted(contributions, key=lambda x: x["abs_impact"], reverse=True)

    # Separar Top fatores que aumentam e diminuem risco
    risk_factors = [c for c in contributions_sorted if c["shap_value"] > 0]
    protective_factors = [c for c in contributions_sorted if c["shap_value"] < 0]

    return {
        "base_value": round(base_val, 4),
        "total_shap_sum": round(float(np.sum(shap_vals)), 4),
        "contributions": contributions_sorted,
        "top_risk_factors": risk_factors[:3],
        "top_protective_factors": protective_factors[:3],
        "shap_raw_values": shap_vals.tolist(),
        "feature_values": feature_values,
        "feature_names": feature_names,
    }


def create_shap_waterfall_figure(
    patient_data: Dict[str, Any],
    model_type: str = "xgboost",
) -> plt.Figure:
    """
    Cria uma figura Matplotlib estilizada com o gráfico SHAP Waterfall para a paciente.
    """
    explanation = explain_prediction_shap(patient_data, model_type)
    contributions = explanation["contributions"]

    # Inverter ordem para que o mais importante fique no topo do gráfico de barras horizontais
    items = list(reversed(contributions))
    labels = [f"{item['feature_label']} ({item['value']})" for item in items]
    values = [item["shap_value"] for item in items]
    colors = ["#E63946" if v > 0 else "#2A9D8F" for v in values]

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=120)
    fig.patch.set_facecolor("#0F172A")  # Dark slate background
    ax.set_facecolor("#1E293B")

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=colors, height=0.6, edgecolor="none")

    # Linha zero de referência
    ax.axvline(0, color="#94A3B8", linestyle="--", linewidth=1.0, alpha=0.7)

    # Configuração dos eixos
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color="#F8FAFC", fontsize=9.5, fontweight="medium")
    ax.tick_params(axis="x", colors="#94A3B8")
    ax.set_xlabel("Impacto SHAP no Risco (Valor Positivo = Maior Risco)", color="#CBD5E1", fontsize=10, labelpad=8)
    ax.set_title(
        f"Interpretabilidade Clínica SHAP - Contribuição das Variáveis ({model_type.upper()})",
        color="#F8FAFC",
        fontsize=11.5,
        fontweight="bold",
        pad=12,
    )

    # Anotações dos valores ao lado das barras
    for bar, val in zip(bars, values):
        x_offset = 0.02 if val >= 0 else -0.02
        ha = "left" if val >= 0 else "right"
        text_color = "#FFAAA6" if val >= 0 else "#A8DADC"
        ax.text(
            val + x_offset,
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.3f}",
            va="center",
            ha=ha,
            color=text_color,
            fontsize=8.5,
            fontweight="bold",
        )

    # Grid sutil
    ax.grid(axis="x", color="#334155", linestyle=":", alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color("#334155")

    plt.tight_layout()
    return fig
