"""
Ponto de Entrada CLI - Guardiã AI (Tech Challenge Fase 5)
Permite executar triagens clínicas em lote, verificar integridade do sistema e gerar relatórios via terminal.
"""

import argparse
import json
import sys
from pprint import pprint

from src.orchestration.graph import run_guardia_pipeline
from src.audit.logger import log_encounter, get_audit_history
from src.ml.train import train_and_evaluate_all


def cmd_evaluate(args):
    """Executa a avaliação de um caso clínico via CLI."""
    patient_data = {
        "Age": args.age,
        "Pregnancy_No": args.pregnancy,
        "Weight": args.weight,
        "Height": args.height,
        "BMI": args.bmi if args.bmi > 0 else round(args.weight / ((args.height / 100) ** 2), 1),
        "Heredity": 1 if args.heredity else 0,
        "Fasting_Glucose": args.glucose,
        "Systolic_BP": args.bp,
        "Gestational_Weeks": args.weeks,
    }

    print("\n========================================================")
    print("🛡️ GUARDIÃ AI — EXECUÇÃO DE TRIAGEM CLÍNICA CLI")
    print("========================================================")
    print("Dados de Entrada:", patient_data)
    print("Queixa / Relato:", args.notes or "(Nenhum relato adicional)")
    print(f"Modelo Escolhido: {args.model.upper()}\n")

    result = run_guardia_pipeline(
        patient_data=patient_data,
        clinical_notes=args.notes or "",
        model_type=args.model,
    )

    pred = result["prediction"]
    shap_data = result["shap_explanation"]
    llm_data = result["llm_synthesis"]

    print("--------------------------------------------------------")
    print(f"🎯 PREDICÃO: {pred['risk_level'].upper()} ({pred['probability_percentage']})")
    print(f"Prioridade: {pred['urgency_classification']}")
    print("--------------------------------------------------------")

    print("\n🔍 TOP FATORES DE RISCO (SHAP):")
    for f in shap_data.get("top_risk_factors", []):
        print(f"  • {f['feature_label']} ({f['value']}): SHAP +{f['shap_value']:.3f}")

    print("\n📚 PROTOCOLOS RAG RECUPERADOS:")
    for s in result["rag_protocols"].get("sources", []):
        print(f"  • [{s['citation_id']}] {s['doc_title']} — {s['section_title']} (Score: {s['relevance_score']*100:.1f}%)")

    print("\n📝 PARECER CLÍNICO DA LLM:")
    print(llm_data.get("synthesis_text", ""))

    # Registrar auditoria
    record = log_encounter(result)
    print(f"\n🔒 Registro de Auditoria: {record['encounter_id']} | Hash: {record['integrity_hash']}")
    print("========================================================\n")


def cmd_train(args):
    """Executa o retreinamento dos modelos de Machine Learning."""
    print("🚀 Iniciando retreinamento e benchmarking dos modelos...")
    train_and_evaluate_all()


def cmd_audit(args):
    """Exibe o histórico recente de auditoria."""
    records = get_audit_history(limit=args.limit)
    print(f"\n--- HISTÓRICO DE AUDITORIA ({len(records)} registros) ---")
    for r in records:
        print(f"[{r['created_at'][:19]}] {r['encounter_id']} | {r['risk_level']} ({r['probability']*100:.1f}%) | Hash: {r['integrity_hash'][:16]}...")


def main():
    parser = argparse.ArgumentParser(description="Guardiã AI - Sistema de Apoio à Decisão em Saúde da Mulher")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: triage
    p_triage = subparsers.add_parser("triage", help="Executa triagem para uma paciente")
    p_triage.add_argument("--age", type=float, default=32.0, help="Idade da paciente")
    p_triage.add_argument("--pregnancy", type=float, default=2.0, help="Nº de gestações")
    p_triage.add_argument("--weight", type=float, default=78.0, help="Peso em kg")
    p_triage.add_argument("--height", type=float, default=162.0, help="Altura em cm")
    p_triage.add_argument("--bmi", type=float, default=0.0, help="IMC (0 para calcular)")
    p_triage.add_argument("--glucose", type=float, default=105.0, help="Glicemia de jejum mg/dL")
    p_triage.add_argument("--bp", type=float, default=135.0, help="Pressão arterial sistólica mmHg")
    p_triage.add_argument("--weeks", type=float, default=26.0, help="Idade gestacional em semanas")
    p_triage.add_argument("--heredity", action="store_true", help="Histórico familiar de diabetes")
    p_triage.add_argument("--notes", type=str, default="", help="Relato clínico ou queixa")
    p_triage.add_argument("--model", type=str, default="xgboost", choices=["xgboost", "random_forest", "logistic_regression"])
    p_triage.set_defaults(func=cmd_evaluate)

    # Comando: train
    p_train = subparsers.add_parser("train", help="Treina e avalia os modelos de Machine Learning")
    p_train.set_defaults(func=cmd_train)

    # Comando: audit
    p_audit = subparsers.add_parser("audit", help="Exibe trilha de auditoria recente")
    p_audit.add_argument("--limit", type=int, default=10, help="Número de registros")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
