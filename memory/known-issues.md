# ⚠️ Problemas Conhecidos, Riscos e Lições Aprendidas — Guardiã AI

Este documento cataloga os problemas técnicos identificados, soluções de contorno (*workarounds*) aplicadas e diretrizes de mitigação para a equipe de sustentação.

---

## 1. Problemas Resolvidos & Mitigações

### 1.1. Caminho Absoluto Hardcoded no Dataset (`src/ml/dataset.py`)
- **Status:** RESOLVIDO.
- **Sintoma:** O código tentava acessar `/Users/wallacen/...` em caso de ausência do dataset bruto.
- **Causa:** Resquício de ambiente de desenvolvimento do autor original no macOS.
- **Correção:** Remoção da referência estática. Validação direta de `RAW_DATASET_PATH` (`data/raw/gestational_diabetes.csv`) com `FileNotFoundError` instrutivo.

### 1.2. Ausência de Dependências no Interpretador Global do Host
- **Status:** RESOLVIDO.
- **Sintoma:** Erro de importação ao rodar testes (`No module named 'reportlab'`, `'sklearn'`, etc.).
- **Causa:** O interpretador global do Windows não continha as dependências instaladas.
- **Mitigação:** Criação do ambiente virtual `.venv` isolado no projeto e execução padronizada via `.venv\Scripts\...` ou Docker.

### 1.3. Conflito Potencial de SDK do Google
- **Status:** RESOLVIDO.
- **Sintoma:** `google-genai` e `google-generativeai` declarados simultaneamente.
- **Causa:** O projeto utiliza `google.generativeai` em `src/orchestration/chains.py`.
- **Mitigação:** Limpeza em `requirements.txt` e inclusão de `openai` para suporte multi-provedor integral.

---

## 2. Pontos de Atenção & Monitoramento Contínuo

### 2.1. Download Inicial do Modelo SentenceTransformer
- **Ponto de Atenção:** Na primeira execução da busca semântica, o `SentenceTransformer("all-MiniLM-L6-v2")` tenta baixar os pesos da HuggingFace (~80MB).
- **Mitigação Implementada:** Caso não haja internet ou o download falhe, o `HybridVectorStore` possui um bloco `try/except` que desativa o modo neural e opera em **100% de capacidade léxica via TF-IDF**, sem travar a aplicação.

### 2.2. Geração de Gráficos Matplotlib em Servidor Web
- **Ponto de Atenção:** Em ambientes sem interface gráfica (Docker/Linux headless), chamadas a `matplotlib.pyplot` podem causar erros de display.
- **Mitigação Implementada:** Em [src/ml/explainer.py](file:///c:/Users/Foton/Documents/pos-IA/hackaton/techchallenge5/src/ml/explainer.py), foi forçado explicitamente o backend não interativo:
  ```python
  import matplotlib
  matplotlib.use("Agg")
  ```

### 2.3. Integridade dos Modelos Serializados (.joblib)
- **Ponto de Atenção:** Modelos serializados com versões diferentes de scikit-learn ou joblib podem emitir warnings de incompatibilidade.
- **Mitigação Implementada:** O `Dockerfile` executa `python src/ml/train.py` durante o processo de `docker build`, garantindo que os pesos correspondam exatamente ao runtime instalado.
