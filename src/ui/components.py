"""
Módulo de Componentes Visuais Reutilizáveis (Guardiã AI)
Fornece blocos visuais estilizados para Streamlit: Cards de Risco, SHAP, Citações RAG e Tabela de Auditoria.
"""

from typing import Dict, Any, List
import streamlit as st

from src.ml.explainer import create_shap_waterfall_figure


CLINICAL_PRESETS = {
    "Caso 1: Gestante Baixo Risco (Rotina)": {
        "Age": 26,
        "Pregnancy_No": 1,
        "Weight": 60.0,
        "Height": 165.0,
        "BMI": 22.0,
        "Heredity": 0,
        "Fasting_Glucose": 82.0,
        "Systolic_BP": 110.0,
        "Gestational_Weeks": 20,
        "notes": "Paciente primigesta comparece para consulta de pré-natal de rotina do 2º trimestre. Assintomática, nega cefaleia, queixas urinárias ou sangramentos. Movimentação fetal ativa percebida.",
    },
    "Caso 2: Risco de Diabetes Gestacional (Sobrepeso + Glicemia Limítrofe)": {
        "Age": 36,
        "Pregnancy_No": 3,
        "Weight": 84.0,
        "Height": 158.0,
        "BMI": 33.6,
        "Heredity": 1,
        "Fasting_Glucose": 104.0,
        "Systolic_BP": 128.0,
        "Gestational_Weeks": 26,
        "notes": "Paciente de 36 anos, multípara, com histórico materno de diabetes tipo 2. Relata ganho de peso acentuado nas últimas semanas e polidipsia discreta. Glicemia de jejum recente de 104 mg/dL.",
    },
    "Caso 3: Emergência Obstétrica / Suspeita Pré-Eclâmpsia": {
        "Age": 31,
        "Pregnancy_No": 2,
        "Weight": 79.0,
        "Height": 160.0,
        "BMI": 30.9,
        "Heredity": 0,
        "Fasting_Glucose": 94.0,
        "Systolic_BP": 165.0,
        "Gestational_Weeks": 34,
        "notes": "Gestante com 34 semanas chega ao pronto-atendimento referindo cefaleia holocraniana intensa refratária a analgésicos comuns, turvação visual (escotomas cintilantes) e edema significativo em membros inferiores (+++/4+). PA aferida no acolhimento: 165x110 mmHg.",
    },
    "Caso 4: Acolhimento & Vulnerabilidade / Violência Doméstica": {
        "Age": 24,
        "Pregnancy_No": 1,
        "Weight": 57.0,
        "Height": 162.0,
        "BMI": 21.7,
        "Heredity": 0,
        "Fasting_Glucose": 85.0,
        "Systolic_BP": 118.0,
        "Gestational_Weeks": 16,
        "notes": "Paciente comparece à consulta visivelmente ansiosa e com esquiva de contato visual. Companheiro insistiu em permanecer na sala, mas foi convidado a aguardar na recepção para exame físico. Paciente relata que ele retém seu celular e documentos, grita frequentemente perto do seu rosto e fez ameaças de agressão física caso ela relate algo à equipe de saúde.",
    },
}


def render_header():
    """Renderiza o topo institucional da Guardiã AI."""
    st.markdown(
        """
        <div class="guardia-header">
            <h1 class="guardia-title">🛡️ Guardiã AI</h1>
            <p class="guardia-subtitle">
                Sistema Inteligente de Suporte à Decisão Clínica e Assistencial para Saúde e Segurança da Mulher
            </p>
        </div>
        <div style="background-color: #F0FDFA !important; border: 1px solid #A7F3D0 !important; border-left: 6px solid #0D9488 !important; border-radius: 14px !important; padding: 14px 20px !important; margin-bottom: 22px !important; box-shadow: 0 2px 8px rgba(13, 148, 136, 0.08) !important;">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 22px; line-height: 1.2;">⚖️</span>
                <div style="color: #0F172A !important; font-size: 13.5px; line-height: 1.55;">
                    <strong style="color: #0F766E !important; font-size: 14px; font-weight: 700; display: inline-block; margin-bottom: 3px;">
                        Lembrete Ético & Apoio à Decisão Clínica (Human-in-the-Loop):
                    </strong>
                    <span style="color: #0F172A !important; font-weight: 450; display: inline;">
                        A <b style="color: #0F172A !important;">Guardiã AI</b> atua exclusivamente como ferramenta auxiliar de triagem e cálculo preditivo para profissionais de saúde e assistência social. As predições e diretrizes geradas <b style="color: #B91C1C !important;">não substituem</b> a avaliação clínica individualizada, diagnósticos médicos ou decisões de segurança conduzidas por humanos.
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_summary(prediction: Dict[str, Any]):
    """Renderiza o card estilizado com nível de risco e probabilidade."""
    risk_level = prediction.get("risk_level", "Risco Habitual")
    prob_pct = prediction.get("probability_percentage", "0.0%")
    prob_val = prediction.get("probability", 0.0)
    urgency = prediction.get("urgency_classification", "Rotina")
    model_used = prediction.get("model_used", "ML")

    card_class = "risk-card-high" if "Alto" in risk_level else ("risk-card-moderate" if "Moderado" in risk_level else "risk-card-low")
    icon = "🚨" if "Alto" in risk_level else ("⚠️" if "Moderado" in risk_level else "✅")

    st.markdown(
        f"""
        <div class="risk-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Estratificação Preditiva</span>
                    <h2 style="margin: 4px 0 8px 0; font-size: 24px; font-weight: 800;">{icon} {risk_level.upper()}</h2>
                    <p style="margin: 0; font-size: 14px; opacity: 0.95;"><b>Resposta Prioritária:</b> {urgency} | <b>Modelo:</b> {model_used}</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 12px; opacity: 0.85;">Probabilidade de Risco</span>
                    <div style="font-size: 36px; font-weight: 900; line-height: 1;">{prob_pct}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(max(prob_val, 0.0), 1.0))


def render_shap_details(shap_data: Dict[str, Any], model_type: str, patient_data: Dict[str, Any]):
    """Renderiza a seção de explicabilidade SHAP."""
    st.subheader("🧠 Interpretabilidade Clínica com SHAP (XAI)")
    st.markdown(
        "O SHAP (*SHapley Additive exPlanations*) decompõe o impacto de cada variável fisiológica na decisão do modelo, fornecendo transparência total para a tomada de decisão médica:"
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = create_shap_waterfall_figure(patient_data, model_type=model_type)
        st.pyplot(fig)

    with col2:
        st.markdown("#### 🔍 Fatores Preponderantes de Risco")
        top_risks = shap_data.get("top_risk_factors", [])
        if top_risks:
            for f in top_risks:
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #EF4444; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
                        <b style="color: #F87171;">{f['feature_label']}</b> = <code>{f['value']}</code><br>
                        <span style="font-size: 12px; color: #CBD5E1;">Impacto SHAP: <b>+{f['shap_value']:.3f}</b> na probabilidade de risco</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum fator isolado aumentou significativamente o risco.")

        st.markdown("#### 🛡️ Fatores Protetores / Redutores")
        top_protect = shap_data.get("top_protective_factors", [])
        if top_protect:
            for f in top_protect:
                st.markdown(
                    f"""
                    <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10B981; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
                        <b style="color: #34D399;">{f['feature_label']}</b> = <code>{f['value']}</code><br>
                        <span style="font-size: 12px; color: #CBD5E1;">Impacto SHAP: <b>{f['shap_value']:.3f}</b> na redução do risco</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_rag_sources(rag_data: Dict[str, Any]):
    """Renderiza os protocolos oficiais recuperados com citação."""
    st.subheader("📚 Protocolos Oficiais e Diretrizes Consultadas (RAG)")
    sources = rag_data.get("sources", [])

    if not sources:
        st.info("Nenhum protocolo específico recuperado para este perfil.")
        return

    for s in sources:
        with st.expander(f"📖 [{s['citation_id']}] {s['doc_title']} — Seção: {s['section_title']} (Relevância: {s['relevance_score']*100:.1f}%)"):
            st.markdown(
                f"""
                <span class="citation-badge">{s['citation_id']}</span> <b>Fonte Oficial:</b> {s['source_file']}<br><br>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(s["content"])
