"""
Módulo de Configuração Central da Guardiã AI
Gerencia caminhos, hiperparâmetros de ML, diretórios de RAG e chaves de API.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente de .env ou .env.local
load_dotenv()

# Diretórios Base
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_PROTOCOLS_DIR = DATA_DIR / "protocols"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Garantir existência dos diretórios
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_PROTOCOLS_DIR, MODELS_DIR, LOGS_DIR, OUTPUTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Arquivos de Dados e Modelos
RAW_DATASET_PATH = DATA_RAW_DIR / "gestational_diabetes.csv"
PROCESSED_DATASET_PATH = DATA_PROCESSED_DIR / "dataset_triagem_consolidado.csv"
MODEL_XGBOOST_PATH = MODELS_DIR / "xgboost_model.joblib"
MODEL_RF_PATH = MODELS_DIR / "random_forest_model.joblib"
MODEL_LR_PATH = MODELS_DIR / "logistic_regression_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
METRICS_SUMMARY_PATH = MODELS_DIR / "metrics_summary.json"
AUDIT_LOG_PATH = LOGS_DIR / "audit_trail.jsonl"

# Configurações de Machine Learning
RANDOM_STATE = 42
TEST_SIZE = 0.20
DECISION_THRESHOLD_HIGH_RECALL = 0.40  # Limiar ajustado para priorizar sensibilidade clínica

# Features Clínicas Principais
FEATURE_COLUMNS = [
    "Age",
    "Pregnancy_No",
    "Weight",
    "Height",
    "BMI",
    "Heredity",
    "Fasting_Glucose",
    "Systolic_BP",
    "Gestational_Weeks",
]

# Configurações de RAG
CHROMA_PERSIST_DIR = DATA_DIR / "chroma_db"
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K_PROTOCOLS = int(os.getenv("TOP_K_PROTOCOLS", "3"))

# Configurações de LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
