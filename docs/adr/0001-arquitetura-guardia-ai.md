# ADR 0001: Arquitetura Modular do CDSS Guardiã AI

## Status
Aprovada

## Data
2026-09-10

## Contexto
O Tech Challenge Fase 5 exige a construção de uma solução integrada em IA que una as competências desenvolvidas ao longo de toda a especialização:
- Fase 1: Análise exploratória e dados clínicos;
- Fase 2: Otimização e priorização médica;
- Fase 3: Fine-tuning e processamento de linguagem natural clínico;
- Fase 4: Triagem multimodal e escores de risco;
- Fase 5: Unificação em um produto funcional com Machine Learning, XAI, RAG, Orquestração e Interface.

O desafio central é evitar um monolito desordenado e garantir que a aplicação funcione tanto em modo de demonstração quanto como base sustentável para evolução futura no SUS.

## Decisão
Adotar uma **Arquitetura Modular em Camadas Desacopladas** com padrão CDSS (*Clinical Decision Support System*):
1. **`src/ml/`**: Responsável exclusivo pela engenharia de dados, treinamento comparativo, inferência e explicabilidade SHAP;
2. **`src/rag/`**: Responsável pelo corpus documental oficial, chunking hierárquico e busca híbrida;
3. **`src/orchestration/`**: Responsável pelo fluxo de execução através de um grafo de estados LangGraph;
4. **`src/audit/`**: Responsável pela governança e cálculo determinístico de hashes SHA-256;
5. **`src/reports/`**: Responsável pela formatação e emissão de laudos em PDF;
6. **`src/ui/`**: Responsável pelo Design System e componentes visuais desacoplados.

## Consequências
- **Positivas:**
  - Facilidade de manutenção e testes unitários pontuais para cada módulo;
  - Possibilidade de trocar o algoritmo de ML ou a base vetorial sem alterar a interface do usuário;
  - Conformidade estrita com o princípio da Fase 5 de "Apoio ao Profissional" (*Human-in-the-Loop*).
- **Negativas:**
  - Maior quantidade de arquivos e interfaces intermediárias de dados (`TypedDict` em `GuardiaState`).
