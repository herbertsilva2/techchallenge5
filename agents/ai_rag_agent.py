"""
Agente Especialista em IA e RAG (AI & RAG Agent) — Guardiã AI
Responsável por auditar modelos de Machine Learning, explicar predições com SHAP,
validar a base de conhecimento RAG e verificar guardrails de prompts.
"""

from typing import Dict, Any, List
from pathlib import Path
import json
from src.config import METRICS_SUMMARY_PATH, PROJECT_ROOT
from src.rag.retriever import retrieve_relevant_protocols


class AIRAGAgent:
    """
    Agente responsável por auditar o desempenho de Machine Learning e a precisão do RAG.
    """

    def __init__(self, root_dir: Path = PROJECT_ROOT):
        self.root_dir = root_dir

    def audit(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Avalia o sumário de métricas dos modelos e executa uma consulta de teste no RAG.
        """
        # 1. Auditoria de ML
        ml_status = {}
        if METRICS_SUMMARY_PATH.exists():
            with open(METRICS_SUMMARY_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
            champ = metrics_data.get("champion_model", "XGBoost")
            models_info = metrics_data.get("models", {})
            champ_metrics = models_info.get(champ, {})

            ml_status = {
                "champion_model": champ,
                "recall": champ_metrics.get("recall"),
                "roc_auc": champ_metrics.get("roc_auc"),
                "f1_score": champ_metrics.get("f1_score"),
                "high_recall_guaranteed": (champ_metrics.get("recall", 0) >= 0.90),
            }

        # 2. Auditoria do RAG
        test_query = "protocolo diabetes gestacional glicemia jejum"
        rag_res = retrieve_relevant_protocols(test_query, top_k=2)
        rag_sources = rag_res.get("sources", [])

        rag_status = {
            "query_tested": test_query,
            "chunks_retrieved": len(rag_sources),
            "top_source": rag_sources[0]["doc_title"] if rag_sources else "Nenhum",
            "top_score": round(rag_sources[0]["relevance_score"], 3) if rag_sources else 0.0,
            "has_citations": all("citation_id" in s for s in rag_sources),
        }

        return {
            "agent": "AIRAGAgent",
            "machine_learning_audit": ml_status,
            "rag_audit": rag_status,
            "status": "CONFORME" if (ml_status.get("high_recall_guaranteed") and rag_status.get("chunks_retrieved") > 0) else "REVISÃO_NECESSÁRIA",
        }
