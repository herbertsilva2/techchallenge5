# 🧠 Memória Arquitetural do Sistema — Guardiã AI

Este documento mantém o contexto arquitetural persistente da plataforma **Guardiã AI**, consolidado durante a Fase 5 do Tech Challenge (Pós-Tech FIAP / Hackathon IADT).

---

## 1. Visão Geral do Produto
- **Nome do Sistema:** Guardiã AI (*Clinical Decision Support System* para Saúde e Segurança da Mulher)
- **Domínio:** Atenção Primária e Obstetrícia no SUS, acolhimento humanizado e triagem integrada.
- **Público-Alvo:** Médicos obstetras, enfermeiros, assistentes sociais e equipes multidisciplinares da Atenção Primária.
- **Princípio Ético Maior:** Apoio à Decisão Médica (*Human-in-the-Loop*). A IA nunca prescreve ou diagnostica de forma autônoma; o profissional de saúde é o titular da conduta clínica.

---

## 2. Stack Tecnológica Mapeada
- **Linguagem:** Python 3.11+
- **Framework Web / UI:** Streamlit 1.30+
- **Machine Learning:** Scikit-Learn 1.3+, XGBoost 2.0+
- **Explicabilidade (XAI):** SHAP 0.44+ (`TreeExplainer` e `LinearExplainer`)
- **Orquestração & Grafo:** LangGraph 0.1+, LangChain Core 0.2+
- **LLM Providers:** Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o-mini`) + Motor Clínico Determinístico Offline
- **RAG & Busca Semântica:** `HybridVectorStore` (SentenceTransformers `all-MiniLM-L6-v2` + `TF-IDF`)
- **Auditoria & Integridade:** SHA-256 criptográfico em `logs/audit_trail.jsonl`
- **Geração de Laudos:** ReportLab 4.0+ (PDF formal com chancela médica)
- **Containerização:** Docker (multi-stage com build-training) + Docker Compose

---

## 3. Módulos e Responsabilidades em `src/`

| Módulo | Localização | Responsabilidade Central |
|---|---|---|
| `config` | `src/config.py` | Centralização de variáveis, paths, hiperparâmetros e chaves de API. |
| `ml` | `src/ml/` | Pipeline de dados, treino de 3 modelos (RF, XGB, LR), avaliação de métricas com foco em Recall clínico, inferência e explicabilidade SHAP. |
| `rag` | `src/rag/` | Leitura de protocolos oficiais, chunking semântico, indexação vetorial e recuperação com citações explícitas (`[REF-01]`, etc.). |
| `orchestration` | `src/orchestration/` | LangGraph `StateGraph`, prompts clínicos de guardrails e chamadas com fallback determinístico offline. |
| `audit` | `src/audit/` | Gravação imutável de atendimentos com hash SHA-256 e método de verificação de integridade. |
| `reports` | `src/reports/` | Emissão de laudo técnico formal em PDF via ReportLab. |
| `ui` | `src/ui/` | Design system customizado (CSS escuro/slate), cards de risco e 4 casos clínicos pré-configurados. |

---

## 4. Fluxo de Dados Ponta a Ponta
```text
Entrada (Streamlit / CLI)
  ↓
GuardiaState (LangGraph)
  ↓
Nó 1: predict_ml (Inferência com High-Recall Threshold = 0.40)
  ↓
Nó 2: explain_shap (Cálculo TreeExplainer + Top 3 fatores positivos e protetores)
  ↓
Nó 3: retrieve_rag (Busca híbrida de protocolos oficiais pertinentes)
  ↓
Nó 4: generate_synthesis (LLM Gemini/OpenAI ou Motor Clínico Determinístico)
  ↓
Auditoria Criptográfica (Hash SHA-256 gravado em logs/audit_trail.jsonl)
  ↓
Apresentação (Cards visuais, gráficos Waterfall SHAP e download de laudo PDF)
```

---

## 5. Regras Clínicas e Guardrails
1. **Limiar de Decisão:** 0.40 para priorizar **Sensibilidade (*Recall*)**; em saúde materna, falsos negativos têm custo inaceitável.
2. **Alertas de Violência:** Detecção de sinais no relato clínico aciona automaticamente o protocolo reservado e orientações do Disque 180 / Lei Maria da Penha / SINAN.
3. **Disponibilidade 100% (Offline Fallback):** Mesmo sem internet ou chaves de API externas, o sistema opera de forma determinística com qualidade técnica total.
