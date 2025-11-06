# pydantic/typed settings: MODEL_NAME, DB URI, timeouts, limits

"""Configuration settings for the agent pipeline."""

import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Model Configuration
MODEL_NAME = "qwen2.5-coder:7b"  # or whatever model you have installed in Ollama
# Common alternatives: "codellama", "deepseek-coder", "qwen2.5-coder", "llama3.1"

# Database Configuration
SQLALCHEMY_DATABASE_URI = (
    f"sqlite:///{os.path.join(PROJECT_ROOT, 'data', 'Employee_Information.db')}"
)

# Schema Documentation
SCHEMA_DOC_PATH = os.path.join(PROJECT_ROOT, "data", "data_documentation.txt")

# Timeout and Limit Settings
LLM_TIMEOUT = 300  # 5 minutes timeout for LLM calls
LLM_MAX_RETRIES = 3
SQL_TIMEOUT = 60  # 60 seconds for SQL execution
MAX_SQL_ROWS = 500  # Maximum rows to return from SQL queries
MAX_STEPS = 4  # Maximum steps in pipeline
PER_STEP_RETRIES = 2

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TEMPERATURE = 0.2
OLLAMA_NUM_PREDICT = 1024  # max tokens
OLLAMA_TOP_P = 0.9
OLLAMA_REPEAT_PENALTY = 1.05
OLLAMA_NUM_CTX = 4096  # context window

# RAG Configuration
RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 100
RAG_SEPARATORS = ["\n\n", "\n", " ", ""]
RAG_SEARCH_K = 6  # Number of chunks to retrieve
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
