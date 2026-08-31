"""
Módulo de Conexão com Modelos de Linguagem (LLM) e Mecanismo de Fallback Clínico (Guardiã AI)
Gerencia chamadas para Google Gemini, OpenAI e fornece gerador clínico determinístico offline.
"""

import os
from typing import Dict, Any
from src.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GEMINI_MODEL,
    OPENAI_MODEL,
)
from src.orchestration.prompts import SYSTEM_PROMPT_GUARDIA, USER_PROMPT_TEMPLATE


def generate_fallback_clinical_synthesis(
    patient_data: Dict[str, Any],
    prediction_result: Dict[str, Any],
    shap_result: Dict[str, Any],
    rag_result: Dict[str, Any],
    clinical_notes: str,
) -> str:
    """
    Gera síntese clínica estruturada de alta qualidade de forma determinística,
    garantindo funcionamento autônomo offline em conformidade com as diretrizes do SUS.
    """
    risk_level = prediction_result.get("risk_level", "Risco Não Avaliado")
    prob_pct = prediction_result.get("probability_percentage", "N/A")
    model_name = prediction_result.get("model_used", "ML")
    urgency = prediction_result.get("urgency_classification", "Rotina")

    # Fatores SHAP
    top_risks = shap_result.get("top_risk_factors", [])
    top_risk_text = ", ".join(
        [f"{f['feature_label']} ({f['value']}, impacto SHAP +{f['shap_value']:.2f})" for f in top_risks]
    ) if top_risks else "Nenhum fator preponderante de risco elevado identificado."

    # Fontes RAG
    sources = rag_result.get("sources", [])
    sources_text = ""
    for s in sources:
        sources_text += f"- **[{s['citation_id']}] {s['doc_title']}** (Seção: {s['section_title']})\n"

    # Verificar se há menção a violência ou sinais de vulnerabilidade nos relatos
    notes_lower = clinical_notes.lower()
    has_violence_signals = any(
        w in notes_lower for w in ["violência", "agressão", "ameaça", "medo", "marido", "companheiro", "socorro", "celular", "trancada", "bateu"]
    )

    synthesis = f"""### 🩺 Parecer de Suporte à Decisão Clínica - Guardiã AI

#### 1. Síntese do Atendimento e Estratificação de Risco
- **Classificação**: **{risk_level}** ({urgency})
- **Probabilidade Estimada ({model_name})**: **{prob_pct}**
- **Justificativa Clínica**: Paciente de {patient_data.get('Age', 28):.0f} anos, IG de {patient_data.get('Gestational_Weeks', 24):.0f} semanas, IMC {patient_data.get('BMI', 24.0):.1f} kg/m² e Glicemia de Jejum de {patient_data.get('Fasting_Glucose', 90):.1f} mg/dL. A estratificação reflete a combinação de marcadores hemodinâmicos e histórico clínico analisados pelo modelo preditivo.

#### 2. Interpretação dos Fatores Críticos (Machine Learning & SHAP)
- **Principais Fatores que Elevam o Risco**: {top_risk_text}
- **Impacto Fisiopatológico**: Os valores observados exercem tração positiva na probabilidade de intercorrências gestacionais e metabólicas, demandando investigação confirmatória conforme os protocolos de pré-natal de alto risco.

#### 3. Diretrizes e Protocolos Oficiais Aplicáveis (RAG)
{sources_text if sources_text else "- *Diretrizes Básicas do Ministério da Saúde e FEBRASGO para Atenção Integral à Saúde da Mulher.*"}

#### 4. Recomendações e Conduta Sugerida para a Equipe
1. **Investigação Complementar**:
   - Solicitar TOTG-75g (entre 24-28 semanas) se glicemia de jejum limítrofe, além de perfil de pré-eclâmpsia (Proteinúria, Plaquetas, Enzimas Hepáticas, Creatinina) se houver elevação pressórica.
2. **Monitoramento Clínico**:
   - Controle glicêmico semanal e verificação seriada da pressão arterial;
   - Monitorar vitalidade fetal por ausculta de BCF e ultrassonografia obstétrica periódica.
3. **Manejo Não Farmacológico**:
   - Orientação nutricional especializada com plano alimentar fracionado e incentivo a atividade física supervisionada.
"""

    if has_violence_signals:
        synthesis += """
#### ⚠️ Alerta de Segurança e Acolhimento Humanizado (Protocolo de Violência / Lei Maria da Penha)
- **Acolhimento Reservado**: Realizar atendimento em sala privativa, garantindo sigilo e presunção de veracidade do relato.
- **Notificação e Encaminhamento**: Preencher Ficha de Notificação Compulsória (SINAN) e oferecer apoio do Serviço Social / Psicologia institucional.
- **Rede de Emergência**: Orientar canais de proteção (Disque 180 / Delegacia da Mulher / CREAS).
"""

    synthesis += """
---
> ⚠️ **Aviso Legal e Ético**: Este parecer foi gerado pela **Guardiã AI** como ferramenta de auxílio à triagem e suporte à decisão. A conduta terapêutica e diagnóstica final é de responsabilidade exclusiva do profissional de saúde assistente.
"""
    return synthesis.strip()


def call_llm_synthesis(
    patient_data: Dict[str, Any],
    prediction_result: Dict[str, Any],
    shap_result: Dict[str, Any],
    rag_result: Dict[str, Any],
    clinical_notes: str,
    provider: str = LLM_PROVIDER,
) -> Dict[str, Any]:
    """
    Executa a geração do parecer clínico utilizando Gemini / OpenAI com fallback automático para o motor offline.
    """
    # Formatação dos fatores SHAP
    top_risks = shap_result.get("top_risk_factors", [])
    top_risk_str = ", ".join([f"{f['feature_label']} (+{f['shap_value']:.2f})" for f in top_risks]) or "Nenhum"

    top_protect = shap_result.get("top_protective_factors", [])
    top_protect_str = ", ".join([f"{f['feature_label']} ({f['shap_value']:.2f})" for f in top_protect]) or "Nenhum"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        age=patient_data.get("Age", 28),
        pregnancy_no=patient_data.get("Pregnancy_No", 1),
        gestational_weeks=patient_data.get("Gestational_Weeks", 24),
        weight=patient_data.get("Weight", 65),
        height=patient_data.get("Height", 160),
        bmi=patient_data.get("BMI", 25.4),
        heredity="Sim (Histórico Positivo)" if patient_data.get("Heredity", 0) == 1 else "Não / Não informado",
        fasting_glucose=patient_data.get("Fasting_Glucose", 88),
        systolic_bp=patient_data.get("Systolic_BP", 115),
        model_used=prediction_result.get("model_used", "ML"),
        probability_percentage=prediction_result.get("probability_percentage", "N/A"),
        risk_level=prediction_result.get("risk_level", "Risco Habitual"),
        urgency_classification=prediction_result.get("urgency_classification", "Rotina"),
        top_risk_factors_str=top_risk_str,
        top_protective_factors_str=top_protect_str,
        clinical_notes=clinical_notes or "Nenhuma queixa adicional registrada pelo profissional.",
        rag_context=rag_result.get("context_text", "Diretrizes Gerais do SUS."),
    )

    # 1. Tentar Google Gemini se a chave estiver configurada
    api_key_gemini = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if (provider == "gemini" or not provider) and api_key_gemini and "sua_chave" not in api_key_gemini.lower():
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key_gemini)
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=SYSTEM_PROMPT_GUARDIA,
            )
            response = model.generate_content(user_prompt)
            if response and response.text:
                return {
                    "synthesis_text": response.text.strip(),
                    "provider_used": f"Google Gemini ({GEMINI_MODEL})",
                    "is_fallback": False,
                }
        except Exception as e:
            print(f"[LLM] Erro ao consultar Gemini ({e}). Acionando Fallback Clínico.")

    # 2. Tentar OpenAI se a chave estiver configurada
    api_key_openai = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
    if provider == "openai" and api_key_openai and "sua_chave" not in api_key_openai.lower():
        try:
            import openai
            client = openai.OpenAI(api_key=api_key_openai)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_GUARDIA},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            res_text = response.choices[0].message.content
            if res_text:
                return {
                    "synthesis_text": res_text.strip(),
                    "provider_used": f"OpenAI ({OPENAI_MODEL})",
                    "is_fallback": False,
                }
        except Exception as e:
            print(f"[LLM] Erro ao consultar OpenAI ({e}). Acionando Fallback Clínico.")

    # 3. Fallback Determinístico Clínico Especializado
    fallback_text = generate_fallback_clinical_synthesis(
        patient_data=patient_data,
        prediction_result=prediction_result,
        shap_result=shap_result,
        rag_result=rag_result,
        clinical_notes=clinical_notes,
    )

    return {
        "synthesis_text": fallback_text,
        "provider_used": "Guardiã AI Clinical Engine (Offline Mode)",
        "is_fallback": True,
    }
