# ADR 0002: Base de Conhecimento RAG com Busca Híbrida e Citações Explícitas

## Status
Aprovada

## Data
2026-09-10

## Contexto
Na área da saúde materna e obstetrícia, modelos de linguagem generativos puros sofrem do risco inaceitável de alucinação (inventar dosagens medicamentosas, limiares de glicemia ou condutas de emergência). O parecer assistencial gerado pela aplicação deve estar 100% ancorado nos protocolos oficiais do Ministério da Saúde, Sociedade Brasileira de Diabetes (SBD), FEBRASGO e Lei Maria da Penha.

## Decisão
Implementar uma arquitetura **RAG Híbrida com Citações Formais**:
1. **Corpus Oficial em Markdown:** Manter os 4 documentos de diretrizes em `data/protocols/` em formato padronizado;
2. **Chunking Semântico:** Fragmentação estruturada por títulos (`#` e `##`), preservando o contexto do capítulo e evitando quebra de parágrafos no meio de tabelas ou condutas;
3. **Índice Híbrido (`HybridVectorStore`):** Combinação de representação neural densa (`SentenceTransformers all-MiniLM-L6-v2`, peso 70%) com representação léxica esparsa (`TF-IDF`, peso 30%). Caso a rede ou biblioteca neural não esteja disponível, o sistema opera automaticamente com 100% TF-IDF;
4. **Citações Explícitas:** Cada fragmento recuperado possui um identificador unívoco (ex: `[REF-01]`, `[REF-02]`), que o prompt da LLM é forçado a referenciar no corpo do parecer.

## Consequências
- **Positivas:**
  - Redução drástica do risco de alucinação;
  - Rastreabilidade médica auditável: o profissional pode verificar exatamente em qual parágrafo da diretriz oficial a recomendação foi baseada;
  - Alta resiliência operacional (fallback gracioso para TF-IDF sem falhas de execução).
- **Negativas:**
  - O vocabulário das consultas clínicas deve conter termos médicos relevantes para garantir scores altos de similaridade.
