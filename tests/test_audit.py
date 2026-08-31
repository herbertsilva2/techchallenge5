"""
Testes unitários para auditoria, integridade criptográfica e emissão de laudos em PDF.
"""

from pathlib import Path
from src.audit.logger import calculate_integrity_hash, log_encounter, verify_entry_integrity, get_audit_history
from src.reports.pdf_generator import generate_clinical_report_pdf
from src.orchestration.graph import run_guardia_pipeline


def test_audit_integrity_hash():
    """Verifica se o hash SHA-256 é calculado e validado corretamente."""
    sample_entry = {
        "created_at": "2026-08-31T10:00:00",
        "patient_features": {"Age": 28, "BMI": 23.5},
        "probability": 0.15,
        "risk_level": "Baixo Risco",
        "model_used": "XGBOOST",
        "top_risk_factors": [],
        "sources_used": [],
    }
    hash_val = calculate_integrity_hash(sample_entry)
    sample_entry["integrity_hash"] = hash_val

    assert verify_entry_integrity(sample_entry) is True

    # Alterar um dado para verificar que o hash falha
    tampered_entry = dict(sample_entry)
    tampered_entry["probability"] = 0.99
    assert verify_entry_integrity(tampered_entry) is False


def test_log_encounter_and_history(tmp_path: Path):
    """Verifica gravação e recuperação no arquivo de auditoria."""
    test_log_file = tmp_path / "test_audit.jsonl"
    state = {
        "created_at": "2026-08-31T12:00:00",
        "patient_data": {"Age": 30},
        "prediction": {"probability": 0.25, "risk_level": "Baixo", "model_used": "XGBOOST"},
        "shap_explanation": {"top_risk_factors": []},
        "rag_protocols": {"sources": []},
        "llm_synthesis": {"provider_used": "Offline", "is_fallback": True},
    }

    record = log_encounter(state, log_path=test_log_file)
    assert record["encounter_id"].startswith("ENC-")
    assert test_log_file.exists()

    history = get_audit_history(limit=10, log_path=test_log_file)
    assert len(history) == 1
    assert history[0]["encounter_id"] == record["encounter_id"]


def test_generate_clinical_report_pdf():
    """Verifica se o gerador de PDF constrói o binário sem erros."""
    patient = {
        "Age": 30,
        "Pregnancy_No": 2,
        "Weight": 70.0,
        "Height": 160.0,
        "BMI": 27.3,
        "Heredity": 0,
        "Fasting_Glucose": 92.0,
        "Systolic_BP": 120.0,
        "Gestational_Weeks": 24,
    }
    state = run_guardia_pipeline(patient_data=patient, clinical_notes="Rotina pré-natal")
    pdf_bytes = generate_clinical_report_pdf(state, patient_name="Maria da Silva", professional_name="Dra. Ana Santos")

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
