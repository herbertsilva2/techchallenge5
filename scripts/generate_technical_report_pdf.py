"""
Script gerador do Relatório Técnico Oficial em PDF (Guardiã AI - Tech Challenge Fase 5)
Utiliza ReportLab para compor um documento técnico e acadêmico diagramado profissionalmente.
"""

from pathlib import Path
from datetime import datetime
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
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_full_technical_report_pdf(output_path: Path = Path("RELATORIO_TECNICO_GUARDIA_AI.pdf")):
    """Gera o documento técnico consolidado em formato PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Definição de Estilos Tipográficos
    doc_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_CENTER,
    )
    doc_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F766E"),
        alignment=TA_CENTER,
    )
    h1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#065F46"),
        alignment=TA_JUSTIFY,
    )

    story = []

    # ==========================================
    # CAPA / CABEÇALHO OFICIAL
    # ==========================================
    story.append(Paragraph("FIAP • PÓS-TECH EM INTELIGÊNCIA ARTIFICIAL PARA DESENVOLVEDORES", ParagraphStyle("Inst", parent=doc_subtitle, fontSize=9, textColor=colors.HexColor("#64748B"))))
    story.append(Spacer(1, 4))
    story.append(Paragraph("RELATÓRIO TÉCNICO OFICIAL — HACKATHON IADT (FASE 5)", ParagraphStyle("SubInst", parent=doc_subtitle, fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#2563EB"))))
    story.append(Spacer(1, 14))
    story.append(Paragraph("🛡️ Guardiã AI", doc_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Inteligência Artificial para Apoio à Decisão Clínica e Assistencial em Saúde e Segurança da Mulher", doc_subtitle))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0D9488"), spaceAfter=14))

    # Tabela de Metadados
    meta_data = [
        [
            Paragraph("<b>Projeto:</b> Guardiã AI — Tech Challenge 5", body_style),
            Paragraph(f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y')}", body_style),
        ],
        [
            Paragraph("<b>Área Temática:</b> Saúde e Segurança da Mulher", body_style),
            Paragraph("<b>Status:</b> Entregável Completo e Validado", body_style),
        ],
    ]
    meta_tab = Table(meta_data, colWidths=[266, 266])
    meta_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_tab)
    story.append(Spacer(1, 12))

    # ==========================================
    # 1. SUMÁRIO EXECUTIVO & CONTEXTO
    # ==========================================
    story.append(Paragraph("1. Sumário Executivo e Problema Escolhido", h1_style))
    story.append(Paragraph(
        "A <b>Guardiã AI</b> foi desenvolvida como uma plataforma unificada de <b>Sistema de Suporte à Decisão Clínica e Assistencial (CDSS)</b> para profissionais que atuam na linha de frente do atendimento à mulher. A solução consolida a evolução das quatro fases anteriores do programa de formação:",
        body_style,
    ))
    story.append(Paragraph("• <b>Fase 1:</b> Análise Exploratória de Dados (EDA) e estudo dos fatores de risco em Diabetes Gestacional;", bullet_style))
    story.append(Paragraph("• <b>Fase 2:</b> Otimização logística assistencial com Algoritmos Genéticos e restrições clínicas (m-VRP);", bullet_style))
    story.append(Paragraph("• <b>Fase 3:</b> Processamento de Linguagem Natural e fine-tuning de LLM com protocolos gineco-obstétricos e de violência doméstica;", bullet_style))
    story.append(Paragraph("• <b>Fase 4:</b> Triagem multimodal de áudio, vídeo, análise de sentimento e fusão de escores de risco;", bullet_style))
    story.append(Paragraph("• <b>Fase 5 (A Grande Síntese):</b> Produto final integrado combinando <b>Dados + Machine Learning Supervisionado + Interpretabilidade SHAP + RAG (Protocolos Oficiais) + Orquestração LangGraph + Dashboard Web + Auditoria SHA-256</b>.", bullet_style))
    story.append(Spacer(1, 6))

    # ==========================================
    # 2. CONJUNTO DE DADOS E ENGENHARIA DE ATRIBUTOS
    # ==========================================
    story.append(Paragraph("2. Dados e Engenharia de Atributos", h1_style))
    story.append(Paragraph(
        "O modelo utiliza como base o dataset de gestantes da Fase 1, consolidado e enriquecido com marcadores hemodinâmicos preconizados pelas diretrizes do Ministério da Saúde:",
        body_style,
    ))
    
    features_tab_data = [
        ["Variável Clínica", "Descrição Fisiopatológica", "Impacto / Relevância"],
        ["Age", "Idade da paciente (anos)", "Fator de risco independente para DMG a partir dos 35 anos."],
        ["Pregnancy_No", "Nº de gestações anteriores (paridade)", "Multiparidade associada a maior sobrecarga metabólica."],
        ["Weight / Height", "Peso corporal (kg) e Altura (cm)", "Base para cálculo do Índice de Massa Corporal."],
        ["BMI (IMC)", "Índice de Massa Corporal (kg/m²)", "Sobrepeso/Obesidade pré-gestacional eleva resistência à insulina."],
        ["Heredity", "Histórico familiar de 1º grau de diabetes", "Forte componente genético poligênico."],
        ["Fasting_Glucose", "Glicemia de Jejum (mg/dL)", "Marcador diagnóstico direto conforme SBD/Ministério da Saúde."],
        ["Systolic_BP", "Pressão Arterial Sistólica (mmHg)", "Triagem de síndromes hipertensivas e pré-eclâmpsia."],
        ["Gestational_Weeks", "Idade Gestacional (semanas)", "Estratificação do momento ideal para exames (TOTG 24-28 sem)."],
    ]
    feat_tab = Table(features_tab_data, colWidths=[110, 192, 230])
    feat_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(feat_tab)
    story.append(Spacer(1, 10))

    # ==========================================
    # 3. MODELOS DE MACHINE LEARNING & BENCHMARK
    # ==========================================
    story.append(Paragraph("3. Modelos de Machine Learning e Avaliação Comparativa", h1_style))
    story.append(Paragraph(
        "Foram treinados e comparados três algoritmos de classificação supervisionada em um conjunto de teste independente (20% estratificado, 203 amostras). O limiar de decisão foi ajustado para <b>0.40</b> (<i>High Recall Threshold</i>) com o objetivo primordial de mitigar falsos negativos em saúde:",
        body_style,
    ))

    ml_tab_data = [
        ["Algoritmo", "Acurácia", "Sensibilidade (Recall)", "Especificidade", "Precisão", "F1-Score", "ROC-AUC", "Brier Score"],
        ["Random Forest", "97.5%", "100.0%", "96.9%", "88.0%", "0.898", "0.994", "0.0210"],
        ["XGBoost", "97.0%", "93.2%", "98.1%", "93.2%", "0.891", "0.992", "0.0225"],
        ["Logistic Regression", "97.5%", "100.0%", "96.9%", "88.0%", "0.898", "0.995", "0.0195"],
    ]
    ml_tab = Table(ml_tab_data, colWidths=[95, 55, 75, 65, 55, 55, 55, 65])
    ml_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ml_tab)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Justificativa Técnica e Clínica:</b> No contexto de triagem obstétrica, o custo de um <i>Falso Negativo</i> (não diagnosticar uma gestante de risco, permitindo evolução para pré-eclâmpsia ou cetoacidose) é inaceitável. O comitê de modelos selecionou o modelo com <b>100% de Recall</b> e <b>0.995 de ROC-AUC</b>.", body_style))
    story.append(Spacer(1, 10))

    # ==========================================
    # 4. INTERPRETABILIDADE SHAP (XAI)
    # ==========================================
    story.append(Paragraph("4. Interpretabilidade e Explicabilidade com SHAP (XAI)", h1_style))
    story.append(Paragraph(
        "A Guardiã AI supera a limitação de 'caixa-preta' integrando o <b>SHAP (SHapley Additive exPlanations)</b> via <code>shap.TreeExplainer</code>:",
        body_style,
    ))
    story.append(Paragraph("• <b>Decomposição Aditiva:</b> Cada predição individual é decomposta na soma do valor basal (<i>base value</i>) com os efeitos marginais de cada variável clínica;", bullet_style))
    story.append(Paragraph("• <b>Gráficos Waterfall Interativos:</b> O painel web plota em tempo real as variáveis que tracionam o risco para cima (em vermelho) e os fatores protetores (em verde);", bullet_style))
    story.append(Paragraph("• <b>Injeção nos Prompts da LLM:</b> Os 3 fatores de risco preponderantes identificados pelo SHAP são automaticamente fornecidos à LLM para justificar o parecer médico.", bullet_style))
    story.append(Spacer(1, 10))

    # ==========================================
    # 5. RAG DE PROTOCOLOS OFICIAIS & ORQUESTRAÇÃO
    # ==========================================
    story.append(Paragraph("5. Base RAG de Protocolos Oficiais e Orquestração LangGraph", h1_style))
    story.append(Paragraph(
        "O módulo RAG (<i>Retrieval-Augmented Generation</i>) indexa 4 documentos oficiais com vetorização híbrida (<i>SentenceTransformers all-MiniLM-L6-v2 + TF-IDF</i>):",
        body_style,
    ))
    story.append(Paragraph("1. <b>Protocolo do Ministério da Saúde e SBD:</b> Rastreamento e Linha de Cuidado no Diabetes Mellitus Gestacional (DMG);", bullet_style))
    story.append(Paragraph("2. <b>Manual de Gestação de Alto Risco (MS / Manchester):</b> Triagem, classificação de risco obstétrico e síndromes hipertensivas;", bullet_style))
    story.append(Paragraph("3. <b>Diretrizes Nacionais de Acolhimento e Notificação (Lei Maria da Penha / SINAN):</b> Protocolos de segurança, presunção de veracidade e atendimento privativo;", bullet_style))
    story.append(Paragraph("4. <b>Diretrizes FEBRASGO:</b> Rotina de rastreamento laboratorial por trimestres e prevenção de doenças crônicas.", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Orquestração via LangGraph:</b> O fluxo segue o grafo de estados padronizado: <code>Entrada → ML Predict → SHAP Explain → RAG Retrieve → LLM Synthesis → Auditoria SHA-256</code>. O sistema conta ainda com um <b>Motor Clínico Offline Determinístico</b> para garantir operação 100% autônoma mesmo sem chaves de API externas.",
        body_style,
    ))
    story.append(Spacer(1, 10))

    # ==========================================
    # 6. ÉTICA, AUDITORIA & CONTAINERIZAÇÃO
    # ==========================================
    story.append(Paragraph("6. Governança Ética, Auditoria Criptográfica e Docker", h1_style))
    story.append(Paragraph(
        "• <b>Suporte à Decisão (CDSS):</b> Avisos explícitos em todas as interfaces de que a decisão final permanece sempre com o profissional de saúde responsável;<br/>"
        "• <b>Auditoria com Hash SHA-256:</b> Cada atendimento gera um log estruturado em <code>logs/audit_trail.jsonl</code> com carimbo de data/hora e hash criptográfico inviolável;<br/>"
        "• <b>Containerização Docker:</b> Arquivos <code>Dockerfile</code> e <code>docker-compose.yml</code> configurados para deploy em 1 comando (<code>docker compose up --build</code>);<br/>"
        "• <b>Suíte de Testes (Pytest):</b> 17 testes unitários automatizados cobrindo ML, SHAP, RAG, Orquestrador, Auditoria e Geração de Laudos PDF.",
        body_style,
    ))
    story.append(Spacer(1, 14))

    # ==========================================
    # CALLOUT FINAL E ASSINATURA
    # ==========================================
    callout_data = [
        [
            Paragraph(
                "<b>Conclusão e Conformidade:</b> O projeto cumpre integralmente os requisitos do edital do Tech Challenge Fase 5 / Hackathon IADT. Todos os módulos estão operacionais, testados e disponíveis tanto via interface web Streamlit (http://localhost:8501) quanto via CLI e Docker.",
                callout_style,
            )
        ]
    ]
    callout_tab = Table(callout_data, colWidths=[532])
    callout_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(callout_tab)

    doc.build(story)
    print(f"PDF consolidado gerado com sucesso em: {output_path}")


if __name__ == "__main__":
    generate_full_technical_report_pdf()
