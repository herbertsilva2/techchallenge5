---
name: automated-testing
description: Diretrizes e procedimentos para execução e criação de testes automatizados com pytest no Guardiã AI.
---

# Skill: Automated Testing & Quality Assurance

## Objetivo
Garantir que todas as alterações de código mantenham 100% de integridade nos módulos de ML, SHAP, RAG, Orquestração e Auditoria.

## Quando Utilizar
- Antes de qualquer commit ou pull request.
- Após retreinar modelos ou atualizar dados em `data/`.
- Ao modificar funções de cálculo de hash ou geração de laudos.

## Procedimento de Execução
1. **Executar a Suíte Completa:**
   ```powershell
   .venv\Scripts\pytest -v
   ```
2. **Executar Módulos Específicos:**
   - ML: `.venv\Scripts\pytest tests/test_ml.py -v`
   - SHAP: `.venv\Scripts\pytest tests/test_shap.py -v`
   - RAG: `.venv\Scripts\pytest tests/test_rag.py -v`
   - Orquestração: `.venv\Scripts\pytest tests/test_orchestration.py -v`
   - Auditoria: `.venv\Scripts\pytest tests/test_audit.py -v`

## Critérios de Aceitação
- Zero falhas ou erros de importação (`0 failed, 0 errors`).
- Novos endpoints ou fluxos de dados devem incluir testes unitários correspondentes.
