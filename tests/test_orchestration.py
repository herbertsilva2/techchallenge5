"""
Testes unitários para o módulo de Orquestração LangGraph / LLM (Guardiã AI).
"""

from src.orchestration.chains import generate_fallback_clinical_synthesis, call_llm_synthesis
from src.orchestration.graph import run_guardia_pipeline


def test_fallback_clinical_synthesis():
    """Verifica a geração do parecer determinístico em modo offline."""
    patient_data = {"Age": 32, "BMI": 31.0, "Fasting_Glucose": 108.0, "Systolic_BP": 138.0}
    prediction = {"risk_level": "Alto Risco Obstétrico", "probability_percentage": "88.5%", "model_used": "XGBOOST"}
    shap_data = {
        "top_risk_factors": [
            {"feature_label": "Glicemia de Jejum", "value": 108.0, "shap_value": 1.45},
            {"feature_label": "IMC", "value": 31.0, "shap_value": 0.82},
        ]
    }
    rag_data = {
        "sources": [
            {"citation_id": "REF-01", "doc_title": "Protocolo Diabetes Gestacional", "section_title": "Conduta"}
        ]
    }

    text = generate_fallback_clinical_synthesis(
        patient_data=patient_data,
        prediction_result=prediction,
        shap_result=shap_data,
        rag_result=rag_data,
        clinical_notes="Paciente com queixas metabólicas.",
    )

    assert "Parecer de Suporte à Decisão Clínica" in text
    assert "Alto Risco Obstétrico" in text
    assert "Glicemia de Jejum" in text
    assert "REF-01" in text


def test_full_pipeline_execution():
    """Testa a execução do pipeline ponta a ponta (LangGraph / StateGraph)."""
    patient = {
        "Age": 29,
        "Pregnancy_No": 1,
        "Weight": 64.0,
        "Height": 162.0,
        "BMI": 24.4,
        "Heredity": 0,
        "Fasting_Glucose": 86.0,
        "Systolic_BP": 112.0,
        "Gestational_Weeks": 22,
    }
    state = run_guardia_pipeline(
        patient_data=patient,
        clinical_notes="Consulta de rotina assintomática.",
        model_type="random_forest",
    )

    assert state["status"] == "CONCLUIDO"
    assert state["prediction"] is not None
    assert state["shap_explanation"] is not None
    assert state["rag_protocols"] is not None
    assert state["llm_synthesis"] is not None
    assert len(state["llm_synthesis"]["synthesis_text"]) > 0
