---
name: generative-ai-guardrails
description: Diretrizes operacionais para auditoria de prompts, recuperação semântica RAG e controle de alucinação no Guardiã AI.
---

# Skill: Generative AI Guardrails & RAG Verification

## Objetivo
Garantir que a camada de IA Generativa da Guardiã AI gere pareceres seguros, auditáveis, fundamentados em protocolos oficiais e isentos de alucinações.

## Regras Obrigatórias para Prompts e LLMs
1. **Papel de Apoio à Decisão:**
   - Todo parecer gerado deve reiterar explicitamente que a decisão diagnóstica e terapêutica final cabe ao profissional de saúde.
2. **Citações Explícitas:**
   - O parecer deve conter marcadores formais `[REF-01]`, `[REF-02]` vinculados às fontes retornadas pelo `retriever.py`.
3. **Controle de Alucinação:**
   - Se o contexto RAG não contiver informações suficientes para a queixa relatada, a LLM deve explicitar a ausência e recomendar investigação complementar em vez de inventar condutas.
4. **Verificação de Fallback:**
   - Garantir que o motor determinístico offline (`generate_fallback_clinical_synthesis`) continue refletindo fielmente as diretrizes do Ministério da Saúde.
