"""
Agente Depurador e Análise de Incidentes (Debugger Agent) — Guardiã AI
Responsável por analisar stacktraces, inspecionar logs de auditoria e diagnosticar causas-raiz.
"""

from typing import Dict, Any, List
from pathlib import Path
import json
from src.config import AUDIT_LOG_PATH
from src.audit.logger import verify_entry_integrity


class DebuggerAgent:
    """
    Agente especialista em diagnóstico de erros em tempo de execução e auditoria de integridade.
    """

    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        self.log_path = log_path

    def investigate(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Investiga o estado dos logs de auditoria e procura anomalias ou corrupções de hash.
        """
        payload = payload or {}
        records_analyzed = 0
        corrupted_records = []
        fallback_invocations = 0

        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        record = json.loads(line_str)
                        records_analyzed += 1
                        if not verify_entry_integrity(record):
                            corrupted_records.append({
                                "line": line_idx,
                                "encounter_id": record.get("encounter_id"),
                                "stored_hash": record.get("integrity_hash"),
                            })
                        if record.get("is_fallback", False):
                            fallback_invocations += 1
                    except Exception:
                        corrupted_records.append({"line": line_idx, "error": "JSON Parse Failure"})

        return {
            "agent": "DebuggerAgent",
            "log_path": str(self.log_path),
            "total_encounters_analyzed": records_analyzed,
            "corrupted_hashes_detected": len(corrupted_records),
            "fallback_engine_used_count": fallback_invocations,
            "integrity_status": "INTEGRO" if len(corrupted_records) == 0 else "COMPROMETIDO",
            "diagnostics": corrupted_records if corrupted_records else "Nenhuma corrupção criptográfica detectada.",
        }
