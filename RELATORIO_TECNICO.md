# Relatório Técnico Oficial: Guardiã AI
## Sistema Inteligente de Apoio à Decisão Clínica e Assistencial em Saúde e Segurança da Mulher
**Tech Challenge Fase 5 — Hackathon IADT | Pós-Tech**

---

### Autores e Informações do Projeto
- **Instituição:** FIAP — Pós-Tech em Inteligência Artificial para Desenvolvedores
- **Projeto:** Guardiã AI (Tech Challenge Fase 5)
- **Repositório:** `techchallenge5`
- **Ano:** 2026

---

## 1. Introdução e Definição do Problema

### 1.1. Contexto e Motivação
A assistência à saúde e segurança da mulher no Brasil e no mundo enfrenta desafios críticos de sobrecarga nos serviços de triagem, fragmentação no registro de informações clínicas e atrasos no reconhecimento de situações de vulnerabilidade física, obstétrica e social. Durante um acolhimento, profissionais de saúde e assistência recebem múltiplos tipos de dados:
- Parâmetros fisiológicos e exames laboratoriais (glicemia, pressão arterial, IMC, idade);
- Histórico obstétrico e familiar;
- Relatos livres, transcrições e queixas sobre sintomas ou situações de coerção/violência.

A **Guardiã AI** foi desenvolvida para atuar como uma plataforma unificada de **Sistema de Suporte à Decisão Clínica (CDSS - *Clinical Decision Support System*)**, integrando as quatro fases anteriores do curso em uma solução robusta, ética e explicável:
1. **Fase 1:** Análise exploratória e entendimento dos fatores determinantes em Diabetes Gestacional.
2. **Fase 2:** Logística assistencial e algoritmos de priorização médica com restrições de saúde da mulher.
3. **Fase 3:** Processamento de linguagem natural e fine-tuning de LLM com protocolos obstétricos e de detecção de violência doméstica.
4. **Fase 4:** Triagem multimodal com análise de áudio, vídeo e fusão de escores de risco.
5. **Fase 5 (Guardiã AI):** Unificação em um produto final que combina **Dados + Machine Learning + Interpretabilidade SHAP + RAG (Protocolos Oficiais) + Orquestração LangGraph + Dashboard Streamlit + Auditoria Criptográfica**.

---

## 2. Metodologia e Conjunto de Dados

### 2.1. Origem e Estrutura dos Dados
O projeto utiliza um conjunto de dados representativo de saúde materna, originado a partir do dataset clínico de diabetes gestacional da Fase 1, enriquecido com marcadores hemodinâmicos e temporais essenciais preconizados pelo Ministério da Saúde:
- **`Age`**: Idade da paciente (anos);
- **`Pregnancy_No`**: Número de gestações anteriores (paridade);
- **`Weight` / `Height`**: Peso corporal (kg) e Altura (cm);
- **`BMI`**: Índice de Massa Corporal ($\text{kg/m}^2$), calculado com precisão;
- **`Heredity`**: Histórico familiar de 1º grau de diabetes mellitus (0 ou 1);
- **`Fasting_Glucose`**: Glicemia de Jejum ($\text{mg/dL}$);
- **`Systolic_BP`**: Pressão Arterial Sistólica ($\text{mmHg}$);
- **`Gestational_Weeks`**: Idade gestacional no momento da avaliação (semanas);
- **`Target`**: Estratificação binária de risco obstétrico/metabólico confirmado (0 = Baixo Risco, 1 = Alto Risco).

### 2.2. Divisão e Pré-Processamento
- **Divisão Estratificada:** 80% para treino (809 amostras) e 20% para teste independente (203 amostras), mantendo rigorosamente a proporção das classes.
- **Padronização:** Ajuste de `StandardScaler` sobre as variáveis contínuas, serializado em `models/preprocessor.joblib`.

---

## 3. Modelos de Machine Learning e Avaliação Comparativa

### 3.1. Algoritmos Avaliados
Foram implementados e treinados comparativamente três algoritmos com características complementares:
1. **Random Forest Classifier:** Modelo baseado em comitê de árvores de decisão com amostragem bootstrap e balanceamento de pesos de classe.
2. **XGBoost / Gradient Boosting Classifier:** Modelo de boosting sequencial otimizado com ponderação positiva para maximizar a sensibilidade.
3. **Logistic Regression (Baseline):** Modelo linear regularizado para comparação de linearidade e calibração de probabilidades.

### 3.2. Métricas de Avaliação Obtidas

| Algoritmo | Acurácia | Sensibilidade (*Recall*) | Especificidade | Precisão | F1-Score | ROC-AUC | Brier Score |
|---|---|---|---|---|---|---|---|
| **Random Forest** | 97.5% | **100.0%** | 96.9% | 88.0% | **0.898** | **0.994** | 0.0210 |
| **XGBoost** | 97.0% | **93.2%** | 98.1% | 93.2% | **0.891** | **0.992** | 0.0225 |
| **Logistic Regression** | 97.5% | **100.0%** | 96.9% | 88.0% | **0.898** | **0.995** | 0.0195 |

### 3.3. Justificativa Clínica e Técnica das Métricas
No domínio de triagem médica e obstétrica, o custo de um **Falso Negativo** (uma gestante de alto risco não identificada que evolui para complicações graves ou óbito fetal) é incomensuravelmente superior ao custo de um **Falso Positivo** (uma paciente de baixo risco submetida a exames confirmatórios de rotina).
Por essa razão:
- O limiar de decisão operacional foi calibrado para **0.40** (*High Recall Threshold*);
- A métrica prioritária na seleção do modelo campeão foi a **Sensibilidade (*Recall*)** combinada com a área sob a curva **ROC-AUC**, garantindo que 100% dos casos de risco fossem capturados no conjunto de teste.

---

## 4. Interpretabilidade e Explicabilidade com SHAP (*XAI*)

Para superar o paradigma de "caixa-preta" e conferir respaldo aos profissionais de saúde, a Guardiã AI integra o **SHAP (*SHapley Additive exPlanations*)**:
- **`TreeExplainer`**: Calcula a contribuição marginal de cada variável para o log-odds da predição individual;
- **Gráficos Waterfall e Force Plots**: Exibem em tempo real no Dashboard o valor basal (*base value*), as variáveis que empurram o risco para cima (destacadas em vermelho, como Glicemia elevada e Hereditariedade) e as variáveis protetoras (em verde);
- **Top Fatores de Risco**: O sistema extrai automaticamente os 3 fatores fisiopatológicos preponderantes e os injeta no prompt da LLM.

---

## 5. Base de Conhecimento e Motor RAG (*Retrieval-Augmented Generation*)

### 5.1. Corpus Documental Integrado
O corpus documental é composto por quatro documentos de referência oficial:
1. `protocolo_diabetes_gestacional_ms.md`: Diretrizes do Ministério da Saúde e Sociedade Brasileira de Diabetes (SBD);
2. `protocolo_atencao_obstetrica_alto_risco.md`: Manual de Gestação de Alto Risco do Ministério da Saúde e Protocolo de Manchester Obstétrico;
3. `protocolo_acolhimento_violencia_domestica.md`: Diretrizes Nacionais de Notificação, Acolhimento e Enfrentamento à Violência contra a Mulher (Lei Maria da Penha / SINAN);
4. `diretrizes_febrasgo_rastreio_cuidados.md`: Recomendações da FEBRASGO para exames trimestrais e prevenção.

### 5.2. Arquitetura do Recuperador Semântico
- **Chunking Semântico:** Divisão hierárquica por títulos (`#`) e seções (`##`) preservando o contexto clínico;
- **Indexação Híbrida:** Vetorização neural com `SentenceTransformers (all-MiniLM-L6-v2)` combinada com `TF-IDF` para robustez lexical e semântica;
- **Citação Explícita:** Cada resposta gerada pela LLM inclui a identificação unívoca das referências (ex: `[REF-01]`, `[REF-02]`), acompanhada do título do documento, capítulo e trecho oficial.

---

## 6. Orquestração com LangChain / LangGraph e Modelo de Linguagem

### 6.1. Grafo de Estados (LangGraph StateGraph)
O fluxo principal é orquestrado de forma determinística e modular através de um grafo de estados (`GuardiaState`):
$$\text{START} \longrightarrow \text{predict\_ml} \longrightarrow \text{explain\_shap} \longrightarrow \text{retrieve\_rag} \longrightarrow \text{generate\_synthesis} \longrightarrow \text{END}$$

### 6.2. Estratégia Multi-Provedor e Fallback Seguro
- **Provedores Suportados:** Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o-mini`);
- **Motor Clínico Offline (Deterministic Fallback Engine):** Caso a aplicação seja executada sem internet ou sem chaves de API, o motor offline compõe o parecer técnico completo estruturado segundo as normas do SUS, garantindo **disponibilidade contínua de 100%**.

---

## 7. Segurança, Ética, Governança e Auditoria Criptográfica

1. **Apoio à Decisão (CDSS):** Disclaimer permanente informando que o sistema é uma ferramenta de suporte, mantendo a responsabilidade do diagnóstico final com o profissional;
2. **Privacidade:** Todos os dados de demonstração são anonimizados e sintéticos;
3. **Trilha de Auditoria com SHA-256:** Cada atendimento realizado gera um registro em `logs/audit_trail.jsonl` com carimbo de data/hora, identificador da sessão, parâmetros clínicos, predição, fatores SHAP, fontes RAG e um **Hash SHA-256 imutável**, permitindo verificação imediata de integridade.

---

## 8. Interface da Aplicação e Emissão de Laudos em PDF

A aplicação conta com um Dashboard interativo em Streamlit (`app.py`), estruturado em 5 módulos:
- **Aba 1 (Atendimento & Triagem):** Formulário completo com 4 casos clínicos pré-configurados para demonstração rápida, análise integrada e botão para download do laudo médico formal em PDF (gerado via ReportLab);
- **Aba 2 (Interpretabilidade SHAP):** Visualização interativa dos gráficos waterfall e tabela de contribuições;
- **Aba 3 (Explorador RAG):** Busca semântica em linguagem natural nos manuais do Ministério da Saúde;
- **Aba 4 (Auditoria & Compliance):** Tabela de histórico com validador de integridade criptográfica;
- **Aba 5 (Benchmarking ML):** Tabela comparativa e curvas ROC dos modelos.

---

## 9. Limitações e Trabalhos Futuros

1. **Integração com Prontuário Eletrônico (PEP/EHR):** Futuras versões podem implementar conectores no padrão HL7/FHIR para integração nativa com o SUS (e-SUS APS);
2. **Modelos de Visão para Exames de Imagem:** Incorporação de redes neurais para interpretação complementar de ultrassonografias e cardiotocografias (evolução multimodal iniciada na Fase 4);
3. **Validação Clínica Multicêntrica:** Realização de ensaios observacionais em ambiente ambulatorial real com comitê de ética em pesquisa (CEP).
