# Query Automation Agent

[![CI](https://github.com/Pulkit12dhingra/Query_Agent/workflows/CI/badge.svg)](https://github.com/Pulkit12dhingra/Query_Agent/actions)
[![codecov](https://codecov.io/gh/Pulkit12dhingra/Query_Agent/branch/main/graph/badge.svg)](https://codecov.io/gh/Pulkit12dhingra/Query_Agent)

Convert natural language to SQL queries using LLM + RAG. Supports CLI and FastAPI interfaces.

## Features
- Natural Language → SQL with LLM
- RAG-enhanced context for better queries
- CLI & FastAPI interfaces
- Multi-step planning + error handling
- 100+ comprehensive tests

## Quick Start

**Prerequisites:** Python 3.13+, Ollama `qwen2.5-coder:7b`, SQLite

**Install:**
```bash
git clone <repo> && cd query_automation
uv install && source .venv/bin/activate && uv pip install -e .
ollama serve  # separate terminal
```

**Usage:**
```bash
# CLI
python query.py "Show all users"
python query.py "Find employees with salary > 60000"

# FastAPI
pip install fastapi uvicorn[standard] && python run_api.py

# API call
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"query": "Show top 10 highest paid employees"}'

# Docker
docker-compose up --build
```

## Database Schema
- **users** (id, name, age) - 100 employees
- **departments** (dept_id, dept_name, dept_head, location, budget) - 8 depts
- **employee_records** (record_id, user_id, dept_id, hire_date, salary, performance_score, hours_worked)

## Example Queries
```bash
python query.py "Show all users"
python query.py "Average salary by department"
python query.py "Top 5 highest paid with departments"
```

## Architecture
- **agent/** - SQL generation & validation
- **db/** - Database engine & execution
- **llms/** - Ollama client with retry
- **rag/** - Document retrieval
- **cli/api/** - User interfaces

## Testing & Config
```bash
python -m pytest tests/ -v  # 100+ tests
```

**Config:** `.env` file or edit `src/agent_pipeline/config.py`
```bash
MODEL_NAME=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
```

## Troubleshooting
1. **Module errors:** `source .venv/bin/activate`
2. **Ollama issues:** `curl http://localhost:11434/api/version`
3. **DB errors:** `python -m pytest tests/test_db_execute.py -v`
4. **Debug:** `tail -f logs/agent_pipeline.log`

## Dependencies
**Core:** LangChain, SQLAlchemy, FAISS, HuggingFace
**Dev:** pytest, ruff, mypy

## Contributing
```bash
git checkout -b feature/name && python -m pytest tests/ -v
uv run ruff check . --fix && git commit -m "feat: description"
```

**License:** MIT
