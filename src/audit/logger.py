"""
Módulo de Registro de Auditoria Criptografada e Trilha de Conformidade (Guardiã AI)
Armazena histórico imutável das análises com hashes SHA-256 para auditoria ética e médica.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.config import AUDIT_LOG_PATH


def calculate_integrity_hash(entry_data: Dict[str, Any]) -> str:
    """
    Calcula um hash SHA-256 determinístico sobre os dados críticos da análise.
    """
    canonical_str = json.dumps(
        {
            "created_at": entry_data.get("created_at"),
            "patient_features": entry_data.get("patient_features"),
            "probability": entry_data.get("probability"),
            "risk_level": entry_data.get("risk_level"),
            "model_used": entry_data.get("model_used"),
            "top_risk_factors": entry_data.get("top_risk_factors"),
            "sources_used": entry_data.get("sources_used"),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


def log_encounter(
    state: Dict[str, Any],
    log_path: Path = AUDIT_LOG_PATH,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Grava um registro de auditoria completo para o atendimento realizado.
    """
    pred = state.get("prediction", {}) or {}
    shap_data = state.get("shap_explanation", {}) or {}
    rag_data = state.get("rag_protocols", {}) or {}
    llm_data = state.get("llm_synthesis", {}) or {}

    sources = [
        {"doc_title": s.get("doc_title"), "section": s.get("section_title"), "citation_id": s.get("citation_id")}
        for s in rag_data.get("sources", [])
    ]

    top_risks = [
        {"feature": f.get("feature"), "shap_value": f.get("shap_value")}
        for f in shap_data.get("top_risk_factors", [])
    ]

    record = {
        "encounter_id": f"ENC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{int(datetime.now().microsecond / 1000):03d}",
        "session_id": session_id or "default_session",
        "created_at": state.get("created_at", datetime.now().isoformat()),
        "patient_features": pred.get("patient_features", {}),
        "clinical_notes": state.get("clinical_notes", ""),
        "model_used": pred.get("model_used", "N/A"),
        "probability": pred.get("probability", 0.0),
        "risk_level": pred.get("risk_level", "N/A"),
        "urgency_classification": pred.get("urgency_classification", "N/A"),
        "top_risk_factors": top_risks,
        "sources_used": sources,
        "llm_provider": llm_data.get("provider_used", "N/A"),
        "is_fallback": llm_data.get("is_fallback", False),
    }

    # Adicionar hash de integridade
    record["integrity_hash"] = calculate_integrity_hash(record)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def get_audit_history(limit: int = 50, log_path: Path = AUDIT_LOG_PATH) -> List[Dict[str, Any]]:
    """
    Retorna os últimos registros de auditoria em ordem cronológica reversa.
    """
    if not log_path.exists():
        return []

    records = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                try:
                    records.append(json.loads(line_str))
                except Exception:
                    continue

    return list(reversed(records))[:limit]


def verify_entry_integrity(entry: Dict[str, Any]) -> bool:
    """
    Verifica se o hash de integridade de um registro de auditoria é válido.
    """
    stored_hash = entry.get("integrity_hash", "")
    computed_hash = calculate_integrity_hash(entry)
    return stored_hash == computed_hash
