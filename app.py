"""
Aplicação Web Principal - Guardiã AI (Tech Challenge Fase 5)
Dashboard Interativo de Apoio à Decisão Clínica e Assistencial em Saúde e Segurança da Mulher.
"""

import json
from datetime import datetime
import streamlit as st
import pandas as pd

from src.config import (
    FEATURE_COLUMNS,
    METRICS_SUMMARY_PATH,
    LLM_PROVIDER,
    DECISION_THRESHOLD_HIGH_RECALL,
)
from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    CLINICAL_PRESETS,
    render_header,
    render_risk_summary,
    render_shap_details,
    render_rag_sources,
)
from src.orchestration.graph import run_guardia_pipeline
from src.audit.logger import log_encounter, get_audit_history, verify_entry_integrity
from src.reports.pdf_generator import generate_clinical_report_pdf
from src.rag.retriever import retrieve_relevant_protocols

# Configuração da Página Streamlit
st.set_page_config(
    page_title="Guardiã AI — Saúde e Segurança da Mulher",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injeção de Estilos CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Inicializa variáveis de estado do Streamlit."""
    if "current_pipeline_result" not in st.session_state:
        st.session_state.current_pipeline_result = None
    if "selected_preset" not in st.session_state:
        st.session_state.selected_preset = "Caso 2: Risco de Diabetes Gestacional (Sobrepeso + Glicemia Limítrofe)"
    if "preset_data" not in st.session_state:
        st.session_state.preset_data = CLINICAL_PRESETS[st.session_state.selected_preset]


init_session_state()

# Barra Lateral (Sidebar)
with st.sidebar:
    st.image("https://img.shields.io/badge/Guardiã%20AI-teal?style=for-the-badge&logo=shield", use_container_width=True)
    st.markdown("### ⚙️ Painel Operacional")
    st.info(f"**Provedor LLM:** `{LLM_PROVIDER.upper()}`\n\n**Limiar de Decisão:** `{DECISION_THRESHOLD_HIGH_RECALL:.2f}` (High Recall)")

    # Carregar métricas dos modelos
    if METRICS_SUMMARY_PATH.exists():
        with open(METRICS_SUMMARY_PATH, "r", encoding="utf-8") as f:
            metrics_summary = json.load(f)
        champ = metrics_summary.get("champion_model", "XGBoost")
        st.success(f"🏆 **Modelo Campeão:** {champ}")
        
        models_data = metrics_summary.get("models", {})
        if champ in models_data:
            c_metrics = models_data[champ]
            st.metric("Sensibilidade (Recall)", f"{c_metrics['recall']*100:.1f}%")
            st.metric("ROC-AUC", f"{c_metrics['roc_auc']:.3f}")
            st.metric("F1-Score", f"{c_metrics['f1_score']:.3f}")

    st.markdown("---")
    st.markdown("### 📞 Contatos de Emergência (SUS)")
    st.markdown(
        """
        - **Central da Mulher:** Disque `180`
        - **Polícia Militar:** `190`
        - **SAMU:** `192`
        - **Disque Direitos Humanos:** `100`
        """
    )
    st.caption("Guardiã AI • 2026")

# Cabeçalho Principal
render_header()

# Abas de Navegação
tab_main, tab_shap, tab_rag, tab_audit, tab_metrics = st.tabs([
    "🩺 Novo Atendimento & Triagem",
    "🧠 Interpretabilidade SHAP",
    "📚 Explorador de Protocolos (RAG)",
    "📜 Trilha de Auditoria & Compliance",
    "📊 Benchmarking de Modelos ML",
])

# ==========================================================
# ABA 1: NOVO ATENDIMENTO E TRIAGEM
# ==========================================================
with tab_main:
    st.markdown("### 📋 Formulário de Acolhimento e Parâmetros Clínicos")
    
    # Seletor de Casos Pré-Configurados
    preset_col, btn_col = st.columns([3, 1])
    with preset_col:
        selected_case = st.selectbox(
            "Carregar Caso Clínico Pré-Configurado para Demonstração:",
            options=list(CLINICAL_PRESETS.keys()),
            index=1,
        )
    with btn_col:
        st.write("")
        st.write("")
        if st.button("🔄 Aplicar Caso", use_container_width=True):
            st.session_state.preset_data = CLINICAL_PRESETS[selected_case]
            st.rerun()

    current_data = st.session_state.preset_data

    # Formulário de Parâmetros Clínicos
    with st.form("clinical_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Idade da Paciente (anos):", min_value=12, max_value=60, value=int(current_data["Age"]))
            pregnancy_no = st.number_input("Nº de Gestações (G):", min_value=1, max_value=15, value=int(current_data["Pregnancy_No"]))
            gestational_weeks = st.slider("Idade Gestacional (semanas):", min_value=4, max_value=42, value=int(current_data["Gestational_Weeks"]))

        with col2:
            weight = st.number_input("Peso Atual (kg):", min_value=35.0, max_value=180.0, value=float(current_data["Weight"]), step=0.5)
            height = st.number_input("Altura (cm):", min_value=120.0, max_value=210.0, value=float(current_data["Height"]), step=1.0)
            calculated_bmi = round(weight / ((height / 100.0) ** 2), 1)
            st.metric("IMC Calculado:", f"{calculated_bmi} kg/m²")

        with col3:
            fasting_glucose = st.number_input("Glicemia de Jejum (mg/dL):", min_value=40.0, max_value=300.0, value=float(current_data["Fasting_Glucose"]), step=1.0)
            systolic_bp = st.number_input("Pressão Arterial Sistólica (mmHg):", min_value=70.0, max_value=240.0, value=float(current_data["Systolic_BP"]), step=1.0)
            heredity_val = st.checkbox("Histórico Familiar de 1º Grau com Diabetes", value=(current_data["Heredity"] == 1))

        clinical_notes = st.text_area(
            "Relato do Atendimento / Queixa Principal / Observações de Segurança:",
            value=current_data.get("notes", ""),
            height=110,
            help="Descreva os sintomas, relatos da paciente ou transcrição de áudio do atendimento.",
        )

        sub_col1, sub_col2 = st.columns([2, 2])
        with sub_col1:
            model_choice = st.selectbox("Algoritmo de Machine Learning:", ["XGBoost", "Random Forest", "Logistic Regression"], index=0)
        with sub_col2:
            patient_name_input = st.text_input("Identificação / Código da Paciente (Anonimizado):", value="PAC-2026-0842")

        submit_btn = st.form_submit_button("🚀 Executar Análise Completa Guardiã AI", use_container_width=True)

    if submit_btn:
        patient_payload = {
            "Age": age,
            "Pregnancy_No": pregnancy_no,
            "Weight": weight,
            "Height": height,
            "BMI": calculated_bmi,
            "Heredity": 1 if heredity_val else 0,
            "Fasting_Glucose": fasting_glucose,
            "Systolic_BP": systolic_bp,
            "Gestational_Weeks": gestational_weeks,
        }

        with st.spinner("Executando pipeline Guardiã AI (ML -> SHAP -> RAG -> LangGraph -> LLM)..."):
            pipeline_result = run_guardia_pipeline(
                patient_data=patient_payload,
                clinical_notes=clinical_notes,
                model_type=model_choice,
            )
            # Registrar auditoria
            audit_record = log_encounter(pipeline_result, session_id=patient_name_input)
            pipeline_result["integrity_hash"] = audit_record["integrity_hash"]
            pipeline_result["encounter_id"] = audit_record["encounter_id"]
            st.session_state.current_pipeline_result = pipeline_result

    # Exibição dos Resultados da Análise
    if st.session_state.current_pipeline_result:
        res = st.session_state.current_pipeline_result
        st.markdown("---")
        st.markdown("### 📊 Resultado da Avaliação Clínica Integrada")

        # Card de Risco
        render_risk_summary(res["prediction"])

        # Parecer da LLM / Motor Clínico
        st.markdown("### 📝 Parecer Técnico Consolidado (LLM & Diretrizes Oficiais)")
        llm_info = res.get("llm_synthesis", {})
        provider_badge = llm_info.get("provider_used", "Guardiã Engine")
        st.caption(f"🤖 **Motor de Síntese Utilizado:** `{provider_badge}`")
        st.markdown(llm_info.get("synthesis_text", ""))

        # Explicabilidade SHAP
        render_shap_details(res["shap_explanation"], model_type=res["model_type"], patient_data=res["patient_data"])

        # Protocolos RAG
        render_rag_sources(res["rag_protocols"])

        # Bloco de Emissão de Laudo PDF
        st.markdown("---")
        st.markdown("### 📄 Emissão de Laudo e Exportação")
        pdf_col1, pdf_col2 = st.columns([3, 1])
        with pdf_col1:
            st.markdown(
                f"""
                <span class="hash-badge">HASH DE AUDITORIA: {res.get('integrity_hash', '')[:40]}...</span>
                <br><small style="color: #94A3B8;">Registro imutável gerado para conformidade médica e ética.</small>
                """,
                unsafe_allow_html=True,
            )
        with pdf_col2:
            pdf_bytes = generate_clinical_report_pdf(res, patient_name=patient_name_input)
            st.download_button(
                label="📥 Baixar Laudo Clínico (PDF)",
                data=pdf_bytes,
                file_name=f"laudo_guardia_ai_{res.get('encounter_id', 'enc')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ==========================================================
# ABA 2: INTERPRETABILIDADE SHAP
# ==========================================================
with tab_shap:
    st.markdown("### 🧠 Central de Interpretabilidade e Explicabilidade (XAI)")
    st.markdown(
        """
        A transparência dos modelos preditivos é um requisito essencial na área médica para prevenir viéses,
        compreender anomalias e fundamentar decisões clínicas. A Guardiã AI utiliza a teoria dos jogos cooperativos (SHAP)
        para calcular o peso relativo de cada variável na probabilidade final.
        """
    )
    if st.session_state.current_pipeline_result:
        res = st.session_state.current_pipeline_result
        shap_res = res["shap_explanation"]
        
        st.markdown("#### Tabela de Contribuições SHAP do Atendimento Atual")
        df_shap = pd.DataFrame(shap_res["contributions"])
        st.dataframe(
            df_shap[["feature_label", "value", "shap_value", "impact_direction"]].rename(
                columns={
                    "feature_label": "Variável Clínica",
                    "value": "Valor da Paciente",
                    "shap_value": "Impacto SHAP",
                    "impact_direction": "Direção do Impacto",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info("Execute uma análise na aba 'Novo Atendimento' para visualizar os detalhes SHAP.")

# ==========================================================
# ABA 3: EXPLORADOR DE PROTOCOLOS (RAG)
# ==========================================================
with tab_rag:
    st.markdown("### 📚 Base de Conhecimento e Diretrizes Oficiais (RAG)")
    st.markdown(
        """
        Consulte diretamente o corpus documental oficial integrado à Guardiã AI, compreendendo os protocolos do
        **Ministério da Saúde**, **Sociedade Brasileira de Diabetes (SBD)**, **FEBRASGO** e **Diretrizes da Lei Maria da Penha**.
        """
    )
    
    rag_query = st.text_input(
        "🔎 Pesquisar Diretriz ou Protocolo Clínico:",
        value="critérios de diagnóstico e manejo de diabetes gestacional",
    )
    
    if st.button("Buscar Diretrizes"):
        with st.spinner("Buscando no índice vetorial..."):
            search_res = retrieve_relevant_protocols(rag_query, top_k=5)
            st.success(f"Encontrados {search_res['total_retrieved']} fragmentos relevantes.")
            for s in search_res["sources"]:
                with st.expander(f"📖 [{s['citation_id']}] {s['doc_title']} — {s['section_title']} (Score: {s['relevance_score']*100:.1f}%)"):
                    st.caption(f"Arquivo Fonte: `{s['source_file']}`")
                    st.markdown(s["content"])

# ==========================================================
# ABA 4: TRILHA DE AUDITORIA & COMPLIANCE
# ==========================================================
with tab_audit:
    st.markdown("### 📜 Trilha de Auditoria Criptográfica e Governança Ética")
    st.markdown(
        """
        Todos os atendimentos geram um registro imutável com carimbo de data/hora, identificador da sessão, parâmetros clínicos,
        predição de ML, fatores SHAP, fontes RAG e um **Hash SHA-256 de integridade**.
        """
    )
    
    history = get_audit_history(limit=50)
    if history:
        st.metric("Total de Atendimentos Auditados:", len(history))
        audit_rows = []
        for h in history:
            is_valid = verify_entry_integrity(h)
            audit_rows.append({
                "Encounter ID": h.get("encounter_id"),
                "Data/Hora": h.get("created_at")[:19].replace("T", " "),
                "Classificação": h.get("risk_level"),
                "Probabilidade": f"{h.get('probability', 0)*100:.1f}%",
                "Modelo": h.get("model_used"),
                "Integridade SHA-256": "✅ VÁLIDO" if is_valid else "❌ CORROMPIDO",
                "Hash": f"{h.get('integrity_hash', '')[:16]}...",
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)
    else:
        st.info("Nenhum atendimento auditado registrado até o momento.")

# ==========================================================
# ABA 5: BENCHMARKING DE MODELOS ML
# ==========================================================
with tab_metrics:
    st.markdown("### 📊 Comparativo e Avaliação de Desempenho dos Modelos")
    st.markdown(
        """
        Conforme preconizado nas diretrizes do Tech Challenge e de inteligência artificial em saúde, avaliamos e comparamos
        pelo menos dois modelos de Machine Learning utilizando métricas estatísticas e clínicas com foco em **Recall**
        (minimização de falsos negativos em pacientes de risco):
        """
    )
    if METRICS_SUMMARY_PATH.exists():
        with open(METRICS_SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
        
        models_dict = summary_data.get("models", {})
        comp_rows = []
        for m_name, m_metrics in models_dict.items():
            comp_rows.append({
                "Algoritmo": m_name,
                "Acurácia": f"{m_metrics['accuracy']*100:.1f}%",
                "Sensibilidade (Recall)": f"{m_metrics['recall']*100:.1f}%",
                "Especificidade": f"{m_metrics['specificity']*100:.1f}%",
                "Precisão": f"{m_metrics['precision']*100:.1f}%",
                "F1-Score": f"{m_metrics['f1_score']:.3f}",
                "ROC-AUC": f"{m_metrics['roc_auc']:.3f}",
                "Brier Score (Calibração)": f"{m_metrics['brier_score']:.4f}",
            })
        
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True)
        st.markdown(f"**Critério de Seleção:** `{summary_data.get('selection_criteria')}`")
        st.success(f"🏆 **Algoritmo Campeão:** `{summary_data.get('champion_model')}`")
