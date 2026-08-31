"""
Módulo de Geração de Laudos Clínicos em PDF (Guardiã AI)
Utiliza ReportLab para compor um parecer técnico formal com dados do paciente, estratificação de risco,
fatores explicativos SHAP, diretrizes oficiais consultadas e espaço para chancela médica.
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_clinical_report_pdf(
    state: Dict[str, Any],
    patient_name: str = "Paciente Não Identificada (Dados Anonimizados)",
    professional_name: str = "Profissional de Saúde Responsável",
) -> bytes:
    """
    Gera um relatório médico formal em PDF a partir do estado da Guardiã AI.
    Retorna os bytes do arquivo PDF gerado.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Estilos Customizados
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
    )
    section_heading = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        alignment=TA_JUSTIFY,
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_JUSTIFY,
    )

    story = []

    # 1. Cabeçalho Institucional
    story.append(Paragraph("GUARDIÃ AI — SUPORTE À DECISÃO CLÍNICA", title_style))
    story.append(Paragraph("Plataforma de Inteligência Artificial para Saúde e Segurança da Mulher", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=12))

    # 2. Metadados do Atendimento
    pred = state.get("prediction", {}) or {}
    patient_data = pred.get("patient_features", {}) or state.get("patient_data", {})
    created_at = state.get("created_at", datetime.now().isoformat())
    formatted_date = datetime.fromisoformat(created_at).strftime("%d/%m/%Y às %H:%M") if "T" in created_at else created_at

    meta_table_data = [
        [
            Paragraph(f"<b>Paciente:</b> {patient_name}", body_style),
            Paragraph(f"<b>Data/Hora:</b> {formatted_date}", body_style),
        ],
        [
            Paragraph(f"<b>Avaliador(a):</b> {professional_name}", body_style),
            Paragraph(f"<b>Modelo Utilizado:</b> {pred.get('model_used', 'XGBOOST')}", body_style),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Estratificação de Risco (Card Destacado)
    risk_level = pred.get("risk_level", "Risco Habitual")
    prob_pct = pred.get("probability_percentage", "N/A")
    urgency = pred.get("urgency_classification", "Rotina")

    card_bg = colors.HexColor("#EF4444") if "Alto" in risk_level else (colors.HexColor("#F59E0B") if "Moderado" in risk_level else colors.HexColor("#10B981"))
    
    risk_table_data = [
        [
            Paragraph(f"CLASSIFICAÇÃO: {risk_level.upper()} | PROBABILIDADE ESTIMADA: {prob_pct}", badge_style),
        ],
        [
            Paragraph(f"<b>Prioridade de Resposta:</b> {urgency}", ParagraphStyle("SubBadge", parent=badge_style, fontSize=9, fontName="Helvetica")),
        ]
    ]
    risk_table = Table(risk_table_data, colWidths=[540])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), card_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 12))

    # 4. Parâmetros Fisiológicos e Clínicos
    story.append(Paragraph("1. Parâmetros Clínicos da Paciente", section_heading))
    
    heredity_str = "Sim (Positivo)" if patient_data.get("Heredity", 0) == 1 else "Não"
    clin_table_data = [
        ["Idade", f"{patient_data.get('Age', 0):.0f} anos", "Idade Gestacional", f"{patient_data.get('Gestational_Weeks', 0):.0f} semanas"],
        ["Peso", f"{patient_data.get('Weight', 0):.1f} kg", "Altura", f"{patient_data.get('Height', 0):.0f} cm"],
        ["IMC", f"{patient_data.get('BMI', 0):.1f} kg/m²", "Gestações Anteriores", f"{patient_data.get('Pregnancy_No', 0):.0f}"],
        ["Glicemia Jejum", f"{patient_data.get('Fasting_Glucose', 0):.1f} mg/dL", "PA Sistólica", f"{patient_data.get('Systolic_BP', 0):.0f} mmHg"],
        ["Histórico Familiar DM", heredity_str, "Limiar de Decisão", f"{pred.get('decision_threshold_used', 0.40):.2f}"],
    ]
    clin_table = Table(clin_table_data, colWidths=[135, 135, 135, 135])
    clin_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(clin_table)
    story.append(Spacer(1, 10))

    # 5. Explicabilidade SHAP
    story.append(Paragraph("2. Interpretação Clínica SHAP (Fatores Preponderantes)", section_heading))
    shap_data = state.get("shap_explanation", {}) or {}
    top_risks = shap_data.get("top_risk_factors", [])
    
    if top_risks:
        for f in top_risks:
            bullet_text = f"• <b>{f['feature_label']}</b> ({f['value']}): contribuição positiva de +{f['shap_value']:.3f} na elevação da probabilidade de risco."
            story.append(Paragraph(bullet_text, body_style))
    else:
        story.append(Paragraph("• Nenhum fator individual crítico com desvio positivo significativo.", body_style))
    story.append(Spacer(1, 10))

    # 6. Síntese e Diretrizes RAG
    story.append(Paragraph("3. Parecer e Recomendações Assistenciais (Fundamentação RAG)", section_heading))
    llm_data = state.get("llm_synthesis", {}) or {}
    synthesis_text = llm_data.get("synthesis_text", "")
    
    # Limpar marcações markdown de forma segura com regex
    import re
    # Converter headers
    cleaned_text = re.sub(r"^#+\s*", "", synthesis_text, flags=re.MULTILINE)
    # Converter negrito **texto** em <b>texto</b>
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", cleaned_text)
    # Remover citações de bloco >
    cleaned_text = re.sub(r"^>\s*", "", cleaned_text, flags=re.MULTILINE)

    # Dividir em parágrafos
    for para in cleaned_text.split("\n\n"):
        para_clean = para.strip().replace("\n", "<br/>")
        if para_clean:
            try:
                story.append(Paragraph(para_clean, body_style))
                story.append(Spacer(1, 4))
            except Exception:
                # Se falhar o parse de HTML, adiciona em texto puro seguro
                safe_text = re.sub(r"<[^>]+>", "", para_clean)
                story.append(Paragraph(safe_text, body_style))
                story.append(Spacer(1, 4))

    # 7. Assinatura e Disclaimer Ético
    story.append(Spacer(1, 16))
    sig_data = [
        [
            Paragraph("____________________________________________________<br/><b>Assinatura e Carimbo do Profissional Responsável</b>", ParagraphStyle("Sig", parent=body_style, alignment=TA_CENTER)),
            Paragraph(f"<b>Hash de Auditoria SHA-256:</b><br/><font size='6'>{state.get('integrity_hash', 'SHA256-VERIFIED')[:32]}...</font>", ParagraphStyle("Hash", parent=body_style, alignment=TA_CENTER)),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[320, 220])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    
    story.append(KeepTogether([
        sig_table,
        Spacer(1, 14),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6),
        Paragraph(
            "<b>Aviso de Responsabilidade Médica:</b> O sistema Guardiã AI atua exclusivamente como ferramenta auxiliar de triagem e suporte à decisão clínica (CDSS), desenvolvida no âmbito do Tech Challenge Fase 5 / Hackathon IADT. As predições e orientações geradas não substituem a anamnese presencial, avaliação médica ou juízo clínico individualizado.",
            disclaimer_style,
        ),
    ]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
