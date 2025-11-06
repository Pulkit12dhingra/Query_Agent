# Query Automation Agent Pipeline

[![CI](https://github.com/username/query_automation/workflows/CI/badge.svg)](https://github.com/username/query_automation/actions)
[![codecov](https://codecov.io/gh/username/query_automation/branch/main/graph/badge.svg)](https://codecov.io/gh/username/query_automation)

An intelligent SQL query automation system that converts natural language questions into SQL queries and executes them against your database. Built with Python, LangChain, Ollama, and SQLite.

## Features

- **Natural Language to SQL**: Convert plain English questions to SQL queries using LLM
- **RAG-Enhanced Context**: Retrieval-Augmented Generation for better SQL generation
- **Multi-Step Query Planning**: Break down complex questions into manageable subtasks
- **Robust Error Handling**: Comprehensive retry logic and graceful failure handling
- **CLI Interface**: Easy-to-use command-line interface for quick queries
- **Comprehensive Testing**: Full test suite with pytest for reliability
- **Modular Architecture**: Clean, maintainable codebase with separation of concerns

## Quick Start

### Prerequisites

1. **Python 3.13+** with virtual environment
2. **Ollama** with `qwen2.5-coder:7b` model
3. **SQLite database** with employee data

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd query_automation

# Install dependencies
uv install
# or: pip install -e .

# Activate virtual environment
source .venv/bin/activate

# Start Ollama (in another terminal)
ollama serve

# Verify model is available
ollama list
# Should show: qwen2.5-coder:7b
```

### Basic Usage

```bash
# Simple query wrapper (easiest)
python scripts/query.py "Show all users"
python scripts/query.py "Find employees with salary > 60000"
python scripts/query.py "What's the average salary by department?"

# Direct CLI usage
PYTHONPATH=src python -m agent_pipeline.cli.main "Your question here"

# Interactive mode
python scripts/batch_cli_demo.py
```

## Database Schema

Your database contains these tables:

### `users` table (Dimension Table)
- `id` - User ID (primary key)
- `name` - User's full name
- `age` - User's age

### `departments` table (Dimension Table)
- `dept_id` - Department ID (primary key)
- `dept_name` - Department name
- `budget` - Department budget

### `employee_records` table (Fact Table)
- `id` - Record ID (primary key)
- `user_id` - Foreign key to users table
- `dept_id` - Foreign key to departments table
- `salary` - Employee salary
- `performance_score` - Performance rating (1.0 - 5.0)
- `hire_date` - Date of hire

## Query Examples

### Basic Data Retrieval
```bash
python scripts/query.py "Show all users"
python scripts/query.py "List all departments"
python scripts/query.py "Show employee records"
```

### Filtering & Searching
```bash
python scripts/query.py "Find users older than 30"
python scripts/query.py "Show employees in Engineering department"
python scripts/query.py "Find employees with salary greater than 70000"
```

### Analytics & Aggregation
```bash
python scripts/query.py "What's the average salary by department?"
python scripts/query.py "Count employees in each department"
python scripts/query.py "Find the highest paid employee"
python scripts/query.py "Show salary statistics"
```

### Complex Queries
```bash
python scripts/query.py "Find top 5 highest paid employees with their departments"
python scripts/query.py "Show average age by department"
python scripts/query.py "Find employees with above average salary in their department"
```

## Architecture

### Core Components

#### Agent Pipeline (`src/agent_pipeline/`)
- **`config.py`** - Configuration management and settings
- **`prompts.py`** - LLM prompts for SQL generation and planning
- **`logging_utils.py`** - Logging setup and utilities

#### Agent System (`src/agent_pipeline/agent/`)
- **`run_steps.py`** - Main agent orchestration and step execution
- **`generate_sql.py`** - SQL generation using LLM with RAG context
- **`validate_sql.py`** - SQL syntax validation

#### Database Layer (`src/agent_pipeline/db/`)
- **`engine.py`** - SQLAlchemy engine management
- **`execute.py`** - SQL execution with timeout protection

#### LLM Integration (`src/agent_pipeline/llms/`)
- **`client.py`** - Ollama LLM client with retry logic

#### RAG System (`src/agent_pipeline/rag/`)
- **`loader.py`** - Document loading for schema documentation
- **`splitter.py`** - Document chunking for retrieval
- **`embeddings.py`** - HuggingFace embeddings
- **`vectorstore.py`** - FAISS vector store for context retrieval

#### Health Checks (`src/agent_pipeline/health/`)
- **`ollama_check.py`** - Ollama service and model health verification

#### Orchestration (`src/agent_pipeline/orchestration/`)
- **`pipeline.py`** - Main pipeline orchestration and initialization

#### CLI Interface (`src/agent_pipeline/cli/`)
- **`main.py`** - Command-line interface

### Key Features

- **Modular Design**: Each component has a single responsibility
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Singleton Patterns**: Efficient resource management for LLM and database connections
- **Timeout Protection**: Prevents runaway queries and LLM calls
- **RAG Integration**: Uses schema documentation for better SQL generation

## Testing

### Test Suite Overview

The project includes a comprehensive pytest test suite covering:

- **Database Testing** (33 tests) - Engine, SQL execution, timeouts
- **LLM Client Testing** (25 tests) - Connection, calls, retries, error handling
- **SQL Validation Testing** (27 tests) - Syntax validation, edge cases
- **Pipeline Testing** (25 tests) - End-to-end scenarios, error handling

### Running Tests

```bash
# Install pytest
uv add pytest

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/agent_pipeline --cov-report=html

# Run specific test files
python -m pytest tests/test_db_execute.py -v
python -m pytest tests/test_llm_client.py -v
python -m pytest tests/test_sql_validation.py -v
python -m pytest tests/test_pipeline_scenarios.py -v
```

### System Testing Scripts

```bash
# Test database connection
python scripts/test_db_connection.py

# Test LLM connection
python scripts/test_llm_client.py

# Test RAG system
python scripts/test_rag_system.py

# Test CLI functionality
python scripts/test_cli.py
```

## Scripts Directory

The `scripts/` directory contains various test and example scripts:

### System Testing
- **`test_db_connection.py`** - Database connectivity testing
- **`test_llm_client.py`** - LLM functionality testing
- **`test_rag_system.py`** - RAG system component testing
- **`test_cli.py`** - CLI functionality testing

### Usage Examples
- **`example_pipeline_usage.py`** - Comprehensive pipeline examples
- **`cli_usage_guide.py`** - Complete CLI usage guide
- **`batch_cli_demo.py`** - Batch processing and interactive mode
- **`query.py`** - Simple query wrapper script

## Configuration

### Environment Variables

Create a `.env` file (optional) to override defaults:
```bash
MODEL_NAME=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URI=sqlite:///data/Employee_Information.db
```

### Custom Configuration

Edit `src/agent_pipeline/config.py` to modify:
- Model parameters (temperature, context window)
- Database settings and connection pool
- Timeout values for LLM and SQL operations
- Logging levels and output formats
- RAG settings (chunk size, overlap, search parameters)

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   ```bash
   # Ensure you're in project directory
   pwd  # Should show: /path/to/query_automation

   # Activate virtual environment
   source .venv/bin/activate
   ```

2. **Ollama connection errors:**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version

   # Start Ollama if needed
   ollama serve

   # Verify model is available
   ollama run qwen2.5-coder:7b "Hello"
   ```

3. **Database errors:**
   ```bash
   # Test database connection
   python scripts/test_db_connection.py

   # Check database file exists
   ls data/Employee_Information.db
   ```

4. **Query timeouts:**
   - Try simpler queries first
   - Check Ollama model response time
   - Increase timeout values in `config.py`

### Debug Mode

```bash
# Check logs for detailed information
tail -f logs/agent_pipeline.log

# Enable debug logging in config.py
LOG_LEVEL = "DEBUG"
```

## Performance Considerations

- **Query Limits**: Automatic LIMIT clauses prevent large result sets
- **Timeout Protection**: SQL and LLM calls have configurable timeouts
- **Connection Pooling**: SQLAlchemy engine manages database connections
- **Singleton Patterns**: Efficient resource reuse for LLM and vector store
- **Retry Logic**: Intelligent retry mechanisms for failed operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
uv add pytest coverage black flake8

# Run tests before committing
python -m pytest tests/ -v

# Format code
black src/ tests/

# Check code quality
flake8 src/ tests/
```

## Dependencies

### Core Dependencies
- **LangChain** - LLM orchestration and RAG
- **SQLAlchemy** - Database ORM and connection management
- **Requests** - HTTP client for Ollama API
- **FAISS** - Vector store for similarity search
- **HuggingFace Transformers** - Embedding models
- **SQLParse** - SQL syntax validation

### Development Dependencies
- **pytest** - Testing framework
- **coverage** - Test coverage reporting
- **black** - Code formatting
- **flake8** - Code quality checking

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- Built with LangChain and Ollama for LLM integration
- Uses HuggingFace models for embeddings
- FAISS for efficient vector similarity search
- SQLAlchemy for robust database operations
