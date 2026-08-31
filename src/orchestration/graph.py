"""
Módulo de Orquestração com LangGraph / LCEL (Guardiã AI)
Define o grafo de estados que conecta entrada de dados, predição de ML, cálculo de SHAP,
recuperação semântica de protocolos RAG e síntese clínica por LLM.
"""

from typing import Dict, Any, TypedDict, Optional
from datetime import datetime

from src.ml.predictor import predict_risk
from src.ml.explainer import explain_prediction_shap
from src.rag.retriever import retrieve_relevant_protocols
from src.orchestration.chains import call_llm_synthesis


class GuardiaState(TypedDict):
    """Estado unificado do pipeline da Guardiã AI."""
    patient_data: Dict[str, Any]
    clinical_notes: str
    model_type: str
    prediction: Optional[Dict[str, Any]]
    shap_explanation: Optional[Dict[str, Any]]
    rag_protocols: Optional[Dict[str, Any]]
    llm_synthesis: Optional[Dict[str, Any]]
    created_at: str
    status: str


def node_predict_ml(state: GuardiaState) -> Dict[str, Any]:
    """Nó 1: Executa a inferência pelo modelo de Machine Learning selecionado."""
    patient_data = state["patient_data"]
    model_type = state.get("model_type", "xgboost")
    pred = predict_risk(patient_data, model_type=model_type)
    return {"prediction": pred}


def node_explain_shap(state: GuardiaState) -> Dict[str, Any]:
    """Nó 2: Calcula a interpretabilidade local com valores de SHAP."""
    patient_data = state["patient_data"]
    model_type = state.get("model_type", "xgboost")
    shap_res = explain_prediction_shap(patient_data, model_type=model_type)
    return {"shap_explanation": shap_res}


def node_retrieve_rag(state: GuardiaState) -> Dict[str, Any]:
    """Nó 3: Busca no RAG os protocolos oficiais pertinentes ao quadro e queixa."""
    patient_data = state["patient_data"]
    clinical_notes = state.get("clinical_notes", "")
    pred = state.get("prediction", {})
    risk_level = pred.get("risk_level", "")

    # Construir query semântica rica
    query_parts = []
    if clinical_notes:
        query_parts.append(clinical_notes)
    if risk_level:
        query_parts.append(f"Protocolo de conduta para {risk_level}")
    if patient_data.get("Fasting_Glucose", 0) >= 92:
        query_parts.append("Diabetes gestacional DMG glicemia de jejum alterada rastreamento")
    if patient_data.get("Systolic_BP", 0) >= 140:
        query_parts.append("Hipertensão gestacional pré-eclâmpsia sulfato de magnésio")
    if patient_data.get("BMI", 0) >= 30:
        query_parts.append("Obesidade e sobrepeso gestacional fatores de risco")

    search_query = " ".join(query_parts) if query_parts else "protocolo de triagem e risco obstetrico saude da mulher"
    rag_res = retrieve_relevant_protocols(search_query, top_k=3)
    return {"rag_protocols": rag_res}


def node_generate_synthesis(state: GuardiaState) -> Dict[str, Any]:
    """Nó 4: LLM gera o parecer técnico consolidado orientando a equipe de saúde."""
    patient_data = state["patient_data"]
    clinical_notes = state.get("clinical_notes", "")
    prediction = state.get("prediction", {})
    shap_res = state.get("shap_explanation", {})
    rag_res = state.get("rag_protocols", {})

    synthesis_res = call_llm_synthesis(
        patient_data=patient_data,
        prediction_result=prediction,
        shap_result=shap_res,
        rag_result=rag_res,
        clinical_notes=clinical_notes,
    )
    return {"llm_synthesis": synthesis_res, "status": "CONCLUIDO"}


def build_guardia_graph():
    """
    Constrói e compila o StateGraph do LangGraph para execução do fluxo de atendimento.
    """
    try:
        from langgraph.graph import StateGraph, START, END

        builder = StateGraph(GuardiaState)
        builder.add_node("predict_ml", node_predict_ml)
        builder.add_node("explain_shap", node_explain_shap)
        builder.add_node("retrieve_rag", node_retrieve_rag)
        builder.add_node("generate_synthesis", node_generate_synthesis)

        builder.add_edge(START, "predict_ml")
        builder.add_edge("predict_ml", "explain_shap")
        builder.add_edge("explain_shap", "retrieve_rag")
        builder.add_edge("retrieve_rag", "generate_synthesis")
        builder.add_edge("generate_synthesis", END)

        return builder.compile()
    except Exception as e:
        print(f"[Orchestrator] Aviso: LangGraph compilation fallback ({e}). Usando executor sequencial nativo.")
        return None


# Compilar o grafo singleton
_COMPILED_GRAPH = None


def run_guardia_pipeline(
    patient_data: Dict[str, Any],
    clinical_notes: str = "",
    model_type: str = "xgboost",
) -> GuardiaState:
    """
    Ponto de entrada principal para executar o fluxo completo da Guardiã AI.
    """
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_guardia_graph()

    initial_state: GuardiaState = {
        "patient_data": patient_data,
        "clinical_notes": clinical_notes,
        "model_type": model_type,
        "prediction": None,
        "shap_explanation": None,
        "rag_protocols": None,
        "llm_synthesis": None,
        "created_at": datetime.now().isoformat(),
        "status": "PROCESSANDO",
    }

    if _COMPILED_GRAPH is not None:
        try:
            final_state = _COMPILED_GRAPH.invoke(initial_state)
            return final_state
        except Exception as e:
            print(f"[Orchestrator] Falha na invocação do grafo LangGraph ({e}). Executando nós sequencialmente.")

    # Execução sequencial resiliente
    state = dict(initial_state)
    state.update(node_predict_ml(state))
    state.update(node_explain_shap(state))
    state.update(node_retrieve_rag(state))
    state.update(node_generate_synthesis(state))
    return state
