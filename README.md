# Query Automation Agent Pipeline

[![CI](https://github.com/Pulkit12dhingra/Query_Agent/workflows/CI/badge.svg)](https://github.com/Pulkit12dhingra/Query_Agent/actions)
[![codecov](https://codecov.io/gh/Pulkit12dhingra/Query_Agent/branch/main/graph/badge.svg)](https://codecov.io/gh/Pulkit12dhingra/Query_Agent)

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

# Install the package in development mode (required for the CLI to work)
uv pip install -e .
# or: pip install -e .

# Start Ollama (in another terminal)
ollama serve

# Verify model is available
ollama list
# Should show: qwen2.5-coder:7b
```

### Basic Usage

```bash
# Simple query wrapper (easiest)
python query.py "Show all users"
python query.py "Find employees with salary > 60000"
python query.py "What's the average salary by department?"

# Direct CLI usage
python -m agent_pipeline.cli.main "Your question here"

# Run with HuggingFace instead of Ollama (optional)
USE_HUGGINGFACE=true HF_MODEL_NAME=sshleifer/tiny-gpt2 python -m agent_pipeline.cli.main "Your question here"

# Direct CLI usage
python -m agent_pipeline.cli.main "Your question here"
```

## Database Schema

Your database contains these tables:

### `users` table (Dimension Table)
**Description:** Core employee information containing personal details and demographics
**Purpose:** Stores basic employee data and serves as the primary employee dimension
**Records:** ~100 employees

| Column Name | Data Type | Null Allowed | Default | Primary Key | Description |
|-------------|-----------|--------------|---------|-------------|-------------|
| id          | INTEGER   | NO          | None    | YES         | Unique employee identifier (auto-increment) |
| name        | TEXT      | YES         | None    | NO          | Full employee name (First Last format) |
| age         | INTEGER   | YES         | None    | NO          | Employee age (range: 18-65 years) |

#### Sample Data:
```
ID | Name             | Age
---|------------------|----
1  | John Smith       | 34
2  | Jane Johnson     | 28
3  | Michael Williams | 45
```

### `departments` table (Dimension Table)
**Description:** Organizational structure containing department information and management details
**Purpose:** Defines company departments with location, budget, and leadership information
**Records:** 8 departments

| Column Name | Data Type | Null Allowed | Default | Primary Key | Description |
|-------------|-----------|--------------|---------|-------------|-------------|
| dept_id     | INTEGER   | NO          | None    | YES         | Unique department identifier (auto-increment) |
| dept_name   | TEXT      | NO          | None    | NO          | Department name (unique) |
| dept_head   | TEXT      | YES         | None    | NO          | Name of department head/manager |
| location    | TEXT      | YES         | None    | NO          | Physical building location |
| budget      | INTEGER   | YES         | None    | NO          | Annual department budget in USD |

#### Department Breakdown:
```
Dept ID | Department Name        | Head             | Location  | Budget
--------|------------------------|------------------|-----------|----------
1       | Engineering            | Sarah Wilson     | Building A| $500,000
2       | Marketing              | Michael Brown    | Building B| $200,000
3       | Sales                  | Jessica Davis    | Building B| $300,000
4       | Human Resources        | David Garcia     | Building C| $150,000
5       | Finance                | Emily Johnson    | Building C| $250,000
6       | Operations             | Chris Martinez   | Building A| $180,000
7       | Customer Support       | Amanda Rodriguez | Building D| $120,000
8       | Research & Development | Matthew Lopez    | Building A| $400,000
```

### `employee_records` table (Fact Table)
**Description:** Central fact table connecting employees to departments with performance and compensation metrics
**Purpose:** Stores transactional employee data for analytics and reporting
**Records:** ~100 records (one per employee)

| Column Name       | Data Type | Null Allowed | Default | Primary Key | Foreign Key | Description |
|-------------------|-----------|--------------|---------|-------------|-------------|-------------|
| record_id         | INTEGER   | NO          | None    | YES         | NO          | Unique record identifier (auto-increment) |
| user_id           | INTEGER   | YES         | None    | NO          | YES         | References users.id - links to employee |
| dept_id           | INTEGER   | YES         | None    | NO          | YES         | References departments.dept_id - department assignment |
| hire_date         | DATE      | YES         | None    | NO          | NO          | Employee start date (YYYY-MM-DD format) |
| salary            | INTEGER   | YES         | None    | NO          | NO          | Annual salary in USD (whole dollars) |
| performance_score | REAL      | YES         | None    | NO          | NO          | Performance rating (1.0-5.0 scale) |
| hours_worked      | INTEGER   | YES         | None    | NO          | NO          | Monthly hours worked (120-200 range) |

#### Foreign Key Relationships:
- `user_id` -> `users.id` (Many-to-One: Multiple records can reference same user)
- `dept_id` -> `departments.dept_id` (Many-to-One: Multiple employees per department)

#### Salary Ranges by Department:
```
Department             | Base Salary | Typical Range
-----------------------|-------------|---------------
Engineering            | $85,000     | $70,000-$110,000
Marketing              | $55,000     | $40,000-$80,000
Sales                  | $60,000     | $45,000-$85,000
Human Resources        | $65,000     | $50,000-$90,000
Finance                | $70,000     | $55,000-$95,000
Operations             | $58,000     | $43,000-$83,000
Customer Support       | $45,000     | $30,000-$70,000
Research & Development | $90,000     | $75,000-$115,000
```

## Query Examples

### Basic Data Retrieval
```bash
python query.py "Show all users"
python query.py "List all departments"
python query.py "Show employee records"
```

### Filtering & Searching
```bash
python query.py "Find users older than 30"
python query.py "Show employees in Engineering department"
python query.py "Find employees with salary greater than 70000"
```

### Analytics & Aggregation
```bash
python query.py "What's the average salary by department?"
python query.py "Count employees in each department"
python query.py "Find the highest paid employee"
python query.py "Show salary statistics"
```

### Complex Queries
```bash
python query.py "Find top 5 highest paid employees with their departments"
python query.py "Show average age by department"
python query.py "Find employees with above average salary in their department"
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

### System Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific components
python -m pytest tests/test_db_execute.py -v
python -m pytest tests/test_llm_client.py -v
python -m pytest tests/test_sql_validation.py -v
python -m pytest tests/test_pipeline_scenarios.py -v
```

## Usage Scripts

The project includes the following usage scripts:

### Main Query Interface
- **`query.py`** - Simple query wrapper script (located in root directory)
- **`main.py`** - Basic usage example

### Testing
All test files are located in the `tests/` directory and can be run with pytest.

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
   # Test database connection with pytest
   python -m pytest tests/test_db_execute.py -v

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

# Run with verbose output
python -m agent_pipeline.cli.main "your query" --verbose
```

## Database Documentation

The RAG system uses detailed database documentation located in `data/data_documentation.txt`. This file contains:
- Complete database schema with table relationships
- Column descriptions and business rules
- Sample data patterns and constraints
- Query optimization guidelines

This documentation is automatically loaded by the RAG system to provide context for SQL generation.

## Project Structure

```
query_automation/
├── src/agent_pipeline/          # Main application code
│   ├── agent/                   # SQL generation and validation
│   ├── cli/                     # Command-line interface
│   ├── db/                      # Database connection and execution
│   ├── llms/                    # LLM client wrapper
│   ├── orchestration/           # Pipeline orchestration
│   └── rag/                     # Document retrieval system
├── tests/                       # Comprehensive test suite
├── data/                        # Database and documentation
│   ├── Employee_Information.db  # SQLite database
│   └── data_documentation.txt   # Schema documentation (used by RAG)
├── query.py                     # Simple query wrapper script (root level)
├── main.py                      # Basic usage example
└── pyproject.toml               # Project configuration
```

## Performance Considerations

- **Query Limits**: Automatic LIMIT clauses prevent large result sets
- **Timeout Protection**: SQL and LLM calls have configurable timeouts
- **Connection Pooling**: SQLAlchemy engine manages database connections
- **Singleton Patterns**: Efficient resource reuse for LLM and vector store
- **Retry Logic**: Intelligent retry mechanisms for failed operations

## Contributing

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

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Local Checks** (Optional - auto-runs on commit)
   ```bash
   # Run all pre-commit hooks
   uv run pre-commit run --all-files

   # Run specific checks
   uv run ruff check . --fix
   uv run ruff format .
   uv run python -m pytest tests/ -v
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks run automatically
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   # CI pipeline runs automatically
   ```

### CI/CD Pipeline

The CI pipeline consists of 5 main jobs that run in parallel:

#### 1. **Test Job** (`test`)
- **Purpose**: Core testing and validation
- **Runs on**: Ubuntu Latest with Python 3.13
- **Steps**:
  - Checkout code
  - Set up Python and uv package manager
  - Install dependencies with `uv sync --dev`
  - Run Ruff linting: `uv run ruff check . --exclude "*.ipynb"`
  - Check formatting: `uv run ruff format --check . --exclude "*.ipynb"`
  - Run pytest tests: `uv run python -m pytest tests/ -v --tb=short`
  - Check file formatting (trailing whitespace, newlines)

#### 2. **Lint and Format Job** (`lint-and-format`)
- **Purpose**: Run pre-commit hooks
- **Steps**:
  - Install dependencies
  - Run all pre-commit hooks: `uv run pre-commit run --all-files --show-diff-on-failure`

#### 3. **Security Job** (`security`)
- **Purpose**: Security vulnerability scanning
- **Steps**:
  - Run Ruff security checks: `uv run ruff check . --select=S --exclude "*.ipynb"`

#### 4. **Type Check Job** (`type-check`)
- **Purpose**: Static type checking (optional)
- **Steps**:
  - Install mypy
  - Run type checking: `uv run mypy src/ --ignore-missing-imports --no-strict-optional`
  - Set to `continue-on-error: true` (non-blocking)

#### 5. **Coverage Job** (`coverage`)
- **Purpose**: Test coverage reporting
- **Steps**:
  - Install coverage tools
  - Run tests with coverage: `uv run coverage run -m pytest tests/`
  - Generate reports: `uv run coverage report --show-missing`
  - Upload to Codecov

### Quality Standards

#### Code Quality
- **Linting**: Ruff with strict rules (pycodestyle, Pyflakes, isort, etc.)
- **Formatting**: Consistent code formatting with Ruff
- **Type Hints**: Encouraged but not enforced (mypy runs as advisory)

#### Testing
- **Coverage**: Aim for >80% test coverage
- **Test Types**: Unit tests, integration tests, and end-to-end tests
- **Test Data**: Use fixtures and mocks to ensure reproducible tests

#### Security
- **Security Scanning**: Automated security checks with Ruff
- **Dependency Management**: Regular dependency updates with uv

#### Documentation
- **Code Documentation**: Docstrings for all public functions/classes
- **README**: Keep README.md updated with latest setup instructions
- **Changelog**: Update for significant changes

### Troubleshooting CI Issues

#### Common Failures

**Linting Failures**
```bash
# Fix locally
uv run ruff check . --fix
uv run ruff format .
git add .
git commit -m "fix: resolve linting issues"
```

**Test Failures**
```bash
# Run tests locally
uv run python -m pytest tests/ -v --tb=long

# Debug specific test
uv run python -m pytest tests/test_specific.py::test_function -vvv
```

**Coverage Issues**
```bash
# Generate coverage report
uv run coverage run -m pytest tests/
uv run coverage report --show-missing

# View HTML report
uv run coverage html
open htmlcov/index.html
```

**Pre-commit Hook Failures**
```bash
# Update pre-commit hooks
uv run pre-commit autoupdate

# Run specific hook
uv run pre-commit run ruff --all-files
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
