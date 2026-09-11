---
name: architecture-analysis
description: Procedimento operacional para análise de arquitetura, contratos de dados e dependências no Guardiã AI.
---

# Skill: Architecture Analysis & Impact Assessment

## Objetivo
Orientar a equipe de sustentação a verificar o impacto arquitetural de qualquer modificação nos módulos de ML, RAG, Orquestração e UI da Guardiã AI.

## Quando Utilizar
- Antes de adicionar novas dependências ao `requirements.txt`.
- Ao alterar estruturas de dados compartilhadas (`GuardiaState`, `FEATURE_COLUMNS`).
- Ao adicionar novos modelos de ML ou novos documentos à base de conhecimento.

## Entradas
- Dicionário de alterações pretendidas.
- Arquivos alvo e novos fluxos de dependência.

## Processo de Análise
1. **Verificar Limites dos Módulos:**
   - O módulo `src/ml/` não deve importar diretamente componentes de `src/ui/` ou `src/reports/`.
   - O módulo `src/orchestration/` atua como o integrador único de ML e RAG.
2. **Avaliar Backward Compatibility:**
   - Garantir que a ordem e nomenclatura de `FEATURE_COLUMNS` em `src/config.py` não sejam quebradas.
   - Preservar o fallback determinístico caso novos nós sejam adicionados ao LangGraph.
3. **Formalizar ADR:**
   - Para qualquer alteração que altere protocolos de rede ou adicione novos serviços, criar um registro em `docs/adr/`.

## Critérios de Sucesso
- Diagrama de arquitetura permanece coerente.
- Nenhum acoplamento circular introduzido.
- ADR devidamente documentada.
