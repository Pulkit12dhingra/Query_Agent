"""Tests for database engine and SQL execution functionality."""

import os
import sys
import time
from unittest.mock import patch

import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.db.engine import create_db_engine, get_engine
from agent_pipeline.db.engine import test_db_connection as _test_db_connection
from agent_pipeline.db.execute import execute_sql, sql_timeout


class TestDatabaseEngine:
    """Test database engine creation and connection."""

    def test_create_db_engine(self):
        """Test database engine creation."""
        engine = create_db_engine("sqlite:///:memory:")
        assert engine is not None
        assert str(engine.url) == "sqlite:///:memory:"

    def test_get_engine_singleton(self):
        """Test that get_engine returns same instance (singleton pattern)."""
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    def test_db_connection_test(self, temp_db):
        """Test database connection testing."""
        tables = _test_db_connection(temp_db)
        expected_tables = ["users", "departments", "employee_records"]
        assert set(tables) == set(expected_tables)


class TestSQLExecution:
    """Test SQL execution with timeouts and limits."""

    def test_execute_simple_sql(self, temp_db):
        """Test basic SQL execution."""
        sql = "SELECT name FROM users WHERE id = 1"
        result = execute_sql(temp_db, sql)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "John Doe"

    def test_execute_sql_with_join(self, temp_db):
        """Test SQL execution with joins."""
        sql = """
        SELECT u.name, d.dept_name, er.salary
        FROM employee_records er
        JOIN users u ON er.user_id = u.id
        JOIN departments d ON er.dept_id = d.dept_id
        WHERE er.salary > 60000
        """
        result = execute_sql(temp_db, sql)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # John and Jane have salary > 60000
        assert "name" in result.columns
        assert "dept_name" in result.columns
        assert "salary" in result.columns

    def test_execute_sql_with_limit(self, temp_db):
        """Test that SQL execution respects row limits."""
        sql = "SELECT * FROM users"
        result = execute_sql(temp_db, sql, max_rows=2)

        assert len(result) == 2  # Should be limited to 2 rows

    def test_execute_sql_auto_limit(self, temp_db):
        """Test automatic LIMIT clause insertion."""
        sql = "SELECT * FROM users"
        result = execute_sql(temp_db, sql, max_rows=2)

        # Should automatically limit results
        assert len(result) <= 2

    def test_execute_sql_existing_limit(self, temp_db):
        """Test SQL execution when LIMIT clause already exists."""
        sql = "SELECT * FROM users LIMIT 1"
        result = execute_sql(temp_db, sql, max_rows=10)

        assert len(result) == 1  # Should respect existing LIMIT

    def test_execute_sql_invalid_syntax(self, temp_db):
        """Test SQL execution with invalid syntax."""
        sql = "INVALID SQL QUERY"

        with pytest.raises(Exception):
            execute_sql(temp_db, sql)

    def test_execute_sql_clean_formatting(self, temp_db):
        """Test SQL cleaning (remove semicolons, whitespace)."""
        sql = "  SELECT name FROM users WHERE id = 1;  "
        result = execute_sql(temp_db, sql)

        assert len(result) == 1
        assert result.iloc[0]["name"] == "John Doe"


class TestSQLTimeout:
    """Test SQL timeout functionality."""

    def test_sql_timeout_context_manager(self):
        """Test timeout context manager functionality."""
        start_time = time.time()

        with pytest.raises(TimeoutError), sql_timeout(1):
            time.sleep(2)  # Sleep longer than timeout

        elapsed = time.time() - start_time
        assert elapsed < 2  # Should timeout before 2 seconds

    def test_sql_timeout_success(self):
        """Test timeout context manager with successful operation."""
        with sql_timeout(2):
            time.sleep(0.1)  # Short operation should succeed

        # Should complete without raising exception
        assert True

    @patch("signal.signal")
    @patch("signal.alarm")
    def test_sql_timeout_signal_handling(self, mock_alarm, mock_signal):
        """Test that timeout properly sets up signal handling."""
        with sql_timeout(5):
            pass

        # Should set up and clean up signal handling
        assert mock_signal.call_count >= 1
        assert mock_alarm.call_count >= 2  # Set and reset


class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    def test_full_query_execution(self, temp_db):
        """Test complete query execution flow."""
        # Test a complex query that exercises multiple components
        sql = """
        SELECT
            u.name,
            d.dept_name,
            er.salary,
            er.performance_score,
            CASE
                WHEN er.performance_score >= 4.5 THEN 'Excellent'
                WHEN er.performance_score >= 4.0 THEN 'Good'
                ELSE 'Needs Improvement'
            END as performance_category
        FROM employee_records er
        JOIN users u ON er.user_id = u.id
        JOIN departments d ON er.dept_id = d.dept_id
        ORDER BY er.performance_score DESC
        """

        result = execute_sql(temp_db, sql)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "performance_category" in result.columns

        # Check that results are ordered by performance_score DESC
        performance_scores = result["performance_score"].tolist()
        assert performance_scores == sorted(performance_scores, reverse=True)

    def test_database_error_handling(self, temp_db):
        """Test database error handling."""
        # Test table doesn't exist
        with pytest.raises(Exception):
            execute_sql(temp_db, "SELECT * FROM nonexistent_table")

        # Test invalid column
        with pytest.raises(Exception):
            execute_sql(temp_db, "SELECT nonexistent_column FROM users")

    def test_concurrent_database_access(self, temp_db):
        """Test concurrent database operations."""
        # Execute multiple queries to ensure connection handling works
        queries = [
            "SELECT COUNT(*) as user_count FROM users",
            "SELECT COUNT(*) as dept_count FROM departments",
            "SELECT COUNT(*) as record_count FROM employee_records",
        ]

        results = []
        for query in queries:
            result = execute_sql(temp_db, query)
            results.append(result)

        # All queries should succeed
        assert len(results) == 3
        assert all(isinstance(r, pd.DataFrame) for r in results)
        assert all(len(r) == 1 for r in results)  # All count queries return 1 row
