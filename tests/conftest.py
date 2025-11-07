"""Pytest configuration and shared fixtures for the test suite."""

import os

# Add src to path for imports
import sys
import tempfile
from unittest.mock import Mock

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.agent.run_steps import StepResult


@pytest.fixture
def temp_db():
    """Create a temporary in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", future=True)

    # Create test tables and data
    with engine.connect() as conn:
        # Create tables
        conn.execute(
            text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """)
        )

        conn.execute(
            text("""
            CREATE TABLE departments (
                dept_id INTEGER PRIMARY KEY,
                dept_name TEXT NOT NULL,
                budget REAL
            )
        """)
        )

        conn.execute(
            text("""
            CREATE TABLE employee_records (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                dept_id INTEGER,
                salary REAL,
                performance_score REAL,
                hire_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (dept_id) REFERENCES departments (dept_id)
            )
        """)
        )

        # Insert test data
        conn.execute(
            text("""
            INSERT INTO users (id, name, email) VALUES
            (1, 'John Doe', 'john@test.com'),
            (2, 'Jane Smith', 'jane@test.com'),
            (3, 'Bob Johnson', 'bob@test.com')
        """)
        )

        conn.execute(
            text("""
            INSERT INTO departments (dept_id, dept_name, budget) VALUES
            (1, 'Engineering', 100000),
            (2, 'Sales', 80000),
            (3, 'Marketing', 60000)
        """)
        )

        conn.execute(
            text("""
            INSERT INTO employee_records (user_id, dept_id, salary, performance_score, hire_date) VALUES
            (1, 1, 75000, 4.5, '2023-01-15'),
            (2, 2, 65000, 4.2, '2022-06-01'),
            (3, 3, 55000, 3.8, '2023-03-10')
        """)
        )

        conn.commit()

    return engine


@pytest.fixture
def mock_llm():
    """Create a mock LLM client for testing."""
    mock = Mock()
    mock.invoke.return_value = "SELECT * FROM test_table;"
    return mock


@pytest.fixture
def mock_ollama_response():
    """Mock response for Ollama health checks."""
    return {"version": "0.12.9", "models": [{"name": "qwen2.5-coder:7b", "size": 4500000000}]}


@pytest.fixture
def sample_step_result():
    """Create a sample StepResult for testing."""
    df = pd.DataFrame(
        {
            "name": ["John Doe", "Jane Smith"],
            "salary": [75000, 65000],
            "dept_name": ["Engineering", "Sales"],
        }
    )

    return StepResult(
        step_id=1,
        title="Test Query",
        description="A test query for unit testing",
        sql="SELECT name, salary, dept_name FROM test_view;",
        result_df=df,
        error=None,
    )


@pytest.fixture
def sample_planning_response():
    """Sample LLM response for task planning."""
    return """1) Get employee data - Retrieve basic employee information
2) Join department data - Add department names to employee records
3) Apply filters - Filter by performance score
4) Sort and limit - Order by salary and limit to top 10"""


@pytest.fixture
def sample_sql_response():
    """Sample LLM response for SQL generation."""
    return """```sql
SELECT u.name, er.salary, d.dept_name, er.performance_score
FROM employee_records er
JOIN users u ON er.user_id = u.id
JOIN departments d ON er.dept_id = d.dept_id
WHERE er.performance_score > 4.0
ORDER BY er.salary DESC
LIMIT 10;
```"""


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        log_file = f.name

    yield log_file

    # Cleanup
    if os.path.exists(log_file):
        os.unlink(log_file)


@pytest.fixture
def mock_vectorstore():
    """Create a mock vector store for RAG testing."""
    mock = Mock()
    mock_retriever = Mock()
    mock_retriever.invoke.return_value = [
        Mock(page_content="Table: users - Contains user information"),
        Mock(page_content="Table: departments - Contains department data"),
        Mock(page_content="Table: employee_records - Contains employee records"),
    ]
    mock.as_retriever.return_value = mock_retriever
    return mock


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    # Reset any global/singleton instances to ensure test isolation
    yield

    # Clean up after test
    import agent_pipeline.db.engine as db_engine
    import agent_pipeline.llms.client as llm_client
    import agent_pipeline.logging_utils as logging_utils
    import agent_pipeline.rag.vectorstore as vectorstore

    # Reset global instances
    llm_client._llm_instance = None
    db_engine._engine_instance = None
    vectorstore._vectorstore_instance = None
    vectorstore._retriever_instance = None
    logging_utils._logger = None
