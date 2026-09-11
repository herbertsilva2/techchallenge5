---
name: ml-evaluation-explainability
description: Procedimento operacional para avaliação clínica de modelos de ML e explicabilidade SHAP no Guardiã AI.
---

# Skill: Machine Learning Evaluation & SHAP Explainability

## Objetivo
Orientar a avaliação estatística e clínica dos modelos preditivos de risco obstétrico e diabetes gestacional.

## Princípios Clínicos de Avaliação
1. **Prioridade Absoluta ao Recall (Sensibilidade):**
   - Em triagem obstétrica, o custo de um falso negativo (uma paciente de alto risco não detectada) é crítico.
   - O limiar padrão de corte é mantido em **0.40** para assegurar que 100% dos casos de risco do conjunto de teste sejam capturados.
2. **Avaliação Além da Acurácia:**
   - Sempre analisar a matriz de confusão, Especificidade, F1-Score, ROC-AUC e Brier Score (calibração probabilística).

## Explicabilidade com SHAP
- Para cada inferência, calcular contribuições locais via `explain_prediction_shap`.
- Verificar se os top 3 fatores de risco apontados têm consistência fisiológica (ex: Glicemia elevada, IMC elevado, idade gestacional avançada).
- Injetar os fatores explicativos no prompt da LLM para que o parecer técnico faça menção direta às razões da estratificação.
