---
name: incident-investigation
description: Procedimento operacional para depuração, investigação de causa raiz e auditoria criptográfica no Guardiã AI.
---

# Skill: Incident Investigation & Root-Cause Analysis

## Objetivo
Padronizar a investigação de falhas, erros de inferência ou discrepâncias na trilha de auditoria da Guardiã AI.

## Quando Utilizar
- Relatos de erro 500 no Streamlit ou exceções no CLI.
- Falhas na verificação do hash SHA-256 em `logs/audit_trail.jsonl`.
- Alertas de indisponibilidade da API de LLM.

## Processo de Investigação
1. **Inspeção de Sintomas:**
   - Obter os últimos registros do log de auditoria: `python main.py audit --limit 10`.
   - Identificar se houve acionamento do fallback offline (`is_fallback: true`).
2. **Verificação de Integridade:**
   - Executar `verify_entry_integrity(record)` em cada registro reportado.
   - Caso o hash não coincida, auditar se houve edição manual no arquivo `.jsonl`.
3. **Reprodução Local:**
   - Reproduzir o atendimento utilizando o CLI `python main.py triage` com os mesmos parâmetros clínicos da paciente.

## Formato de Resposta do Incidente
- **Sintoma:** Descrição do comportamento observado.
- **Evidências:** Linhas de log, payload de entrada e stacktrace.
- **Causa Raiz:** Razão técnica comprovada por evidências.
- **Correção:** Código ou parâmetro alterado.
- **Plano de Rollback:** Reversão segura se a correção falhar.
