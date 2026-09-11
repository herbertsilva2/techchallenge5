# ADR 0003: Orquestração LangGraph com Motor Clínico Determinístico Offline

## Status
Aprovada

## Data
2026-09-10

## Contexto
O ecossistema do Sistema Único de Saúde (SUS), especialmente em Unidades Básicas de Saúde (UBS) fluviais ou remotas, enfrenta oscilações frequentes de conectividade à internet. Além disso, a dependência rígida de chaves de API externas pagas (como OpenAI ou Google Gemini) geraria uma fragilidade crítica que impediria a demonstração ou a homologação do sistema em ambientes controlados.

## Decisão
1. **LangGraph StateGraph:** Implementar o fluxo unificado através de nós sequenciais (`predict_ml -> explain_shap -> retrieve_rag -> generate_synthesis -> END`), mantendo o estado tipado em `GuardiaState`.
2. **Fallback Sequencial Nativo:** Caso o compilador do LangGraph apresente incompatibilidade no runtime, o pipeline executa os mesmos nós em função pura sequencial sem interromper a aplicação.
3. **Motor Clínico Determinístico Offline (100% SLA):** Se nenhuma chave de API for fornecida ou se a requisição externa falhar (timeout, rate limit, rede inoperante), a função `generate_fallback_clinical_synthesis` entra em ação instantaneamente, gerando o parecer técnico completo conforme as regras do Ministério da Saúde com os dados reais da predição, SHAP e RAG.

## Consequências
- **Positivas:**
  - Garantia de 100% de disponibilidade em qualquer cenário (demonstração, banca acadêmica ou ambiente hospitalar sem internet);
  - Custo zero obrigatório para execução básica da plataforma;
  - Rastreabilidade transparente através da tag `provider_used` e booleano `is_fallback`.
- **Negativas:**
  - O parecer offline utiliza regras estruturadas em templates avançados, perdendo um pouco da flexibilidade estilística de uma LLM de grande porte.
