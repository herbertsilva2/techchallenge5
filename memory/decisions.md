# 📋 Registro Geral de Decisões Arquiteturais (ADRs) — Guardiã AI

Este documento sintetiza as principais decisões arquiteturais tomadas para a plataforma **Guardiã AI**, garantindo rastreabilidade e justificativa técnica alinhada aos requisitos da Fase 5 do Tech Challenge.

---

## Índice de Decisões

| ID | Título | Status | Data | Impacto Principal |
|---|---|:---:|:---:|---|
| **ADR-0001** | Arquitetura Modular de Apoio à Decisão Clínica (CDSS) | Aprovada | 2026-09-10 | Desacoplamento em ML, XAI, RAG, Orquestração e UI |
| **ADR-0002** | RAG com Busca Híbrida e Citações Explícitas | Aprovada | 2026-09-10 | Prevenção de alucinações e transparência com `[REF-XX]` |
| **ADR-0003** | Orquestração LangGraph com Motor Clínico Offline | Aprovada | 2026-09-10 | Resiliência e garantia de 100% de disponibilidade no SUS |
| **ADR-0004** | Calibração de Limiar Clínico (Threshold = 0.40) | Aprovada | 2026-09-10 | Minimização de Falsos Negativos (Foco em Sensibilidade/Recall) |
| **ADR-0005** | Trilha de Auditoria com Hash Criptográfico SHA-256 | Aprovada | 2026-09-10 | Governança imutável e conformidade médica |

---

## Detalhes das Decisões Principais

### ADR-0001: Arquitetura Modular em Camadas
- **Contexto:** Necessidade de integrar aprendizados de 4 fases anteriores em uma aplicação coesa para a Fase 5.
- **Decisão:** Separar rigorosamente as responsabilidades em `src/ml/`, `src/rag/`, `src/orchestration/`, `src/audit/`, `src/reports/` e `src/ui/`.
- **Consequência:** Baixo acoplamento, facilidade de substituição de componentes e testabilidade isolada.

### ADR-0002: RAG Híbrido com Citações Explícitas
- **Contexto:** Em ambientes clínicos, respostas genéricas ou alucinações de LLM colocam vidas em risco.
- **Decisão:** Indexação hierárquica por seções (`#`, `##`) e combinação de busca neural com TF-IDF, exigindo injeção de marcadores formais `[REF-01]` no texto.
- **Consequência:** Alta rastreabilidade das orientações médicas geradas.

### ADR-0003: LangGraph com Fallback Determinístico
- **Contexto:** Dependência exclusiva de APIs de LLM externas (OpenAI / Gemini) pode causar interrupções em postos de saúde ou falhas por indisponibilidade de rede.
- **Decisão:** Implementar um motor determinístico offline completo (`generate_fallback_clinical_synthesis`) acionado caso as APIs falhem ou não tenham chaves configuradas.
- **Consequência:** Zero dependência obrigatória de serviços de nuvem pagos para funcionamento de base.
