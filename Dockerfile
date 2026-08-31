# Dockerfile para Guardiã AI (Tech Challenge Fase 5)
FROM python:3.11-slim

# Variáveis de ambiente para Python e Streamlit
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# Instalar dependências de sistema para OpenMP e build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código-fonte e dados do projeto
COPY . .

# Treinar os modelos na inicialização do container (garante presença dos pesos)
RUN PYTHONPATH=. python src/ml/train.py

# Porta de exposição do Streamlit
EXPOSE 8501

# Healthcheck do container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicialização
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
