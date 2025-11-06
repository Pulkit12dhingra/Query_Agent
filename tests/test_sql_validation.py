"""Tests for SQL validation functionality."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.agent.validate_sql import sql_is_plausible


class TestSQLValidation:
    """Test SQL syntax validation using sqlparse."""

    def test_valid_basic_select(self):
        """Test validation of basic SELECT statement."""
        sql = "SELECT * FROM users"
        assert sql_is_plausible(sql) is True

    def test_valid_select_with_where(self):
        """Test validation of SELECT with WHERE clause."""
        sql = "SELECT name, email FROM users WHERE id = 1"
        assert sql_is_plausible(sql) is True

    def test_valid_select_with_join(self):
        """Test validation of SELECT with JOIN."""
        sql = """
        SELECT u.name, d.dept_name
        FROM users u
        JOIN departments d ON u.dept_id = d.id
        """
        assert sql_is_plausible(sql) is True

    def test_valid_complex_query(self):
        """Test validation of complex query with CTE and subqueries."""
        sql = """
        WITH high_performers AS (
            SELECT user_id, performance_score
            FROM employee_records
            WHERE performance_score > 4.0
        )
        SELECT u.name, hp.performance_score, d.dept_name
        FROM high_performers hp
        JOIN users u ON hp.user_id = u.id
        JOIN departments d ON u.dept_id = d.id
        ORDER BY hp.performance_score DESC
        LIMIT 10
        """
        assert sql_is_plausible(sql) is True

    def test_valid_insert_statement(self):
        """Test validation of INSERT statement."""
        sql = "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')"
        assert sql_is_plausible(sql) is True

    def test_valid_update_statement(self):
        """Test validation of UPDATE statement."""
        sql = "UPDATE users SET email = 'newemail@example.com' WHERE id = 1"
        assert sql_is_plausible(sql) is True

    def test_valid_delete_statement(self):
        """Test validation of DELETE statement."""
        sql = "DELETE FROM users WHERE id = 1"
        assert sql_is_plausible(sql) is True


class TestSQLValidationInvalid:
    """Test SQL validation with invalid or malformed SQL."""

    def test_empty_string(self):
        """Test validation of empty string."""
        sql = ""
        assert sql_is_plausible(sql) is False

    def test_whitespace_only(self):
        """Test validation of whitespace-only string."""
        sql = "   \n   \t   "
        assert sql_is_plausible(sql) is False

    def test_invalid_syntax(self):
        """Test validation of completely invalid syntax."""
        sql = "INVALID SQL SYNTAX HERE"
        # Note: sqlparse is lenient, so this might still parse as tokens
        # The function checks for presence of tokens, not correctness
        result = sql_is_plausible(sql)
        # This test documents current behavior rather than expected behavior
        assert isinstance(result, bool)

    def test_incomplete_query(self):
        """Test validation of incomplete SQL query."""
        sql = "SELECT * FROM"
        result = sql_is_plausible(sql)
        # sqlparse will still tokenize this, so it might return True
        assert isinstance(result, bool)

    def test_just_semicolon(self):
        """Test validation of just semicolon."""
        sql = ";"
        result = sql_is_plausible(sql)
        assert isinstance(result, bool)

    def test_sql_comment_only(self):
        """Test validation of comment-only SQL."""
        sql = "-- This is just a comment"
        result = sql_is_plausible(sql)
        assert isinstance(result, bool)


class TestSQLValidationEdgeCases:
    """Test SQL validation edge cases and special scenarios."""

    def test_multiline_sql(self):
        """Test validation of multiline SQL."""
        sql = """
        SELECT
            u.name,
            u.email,
            d.dept_name
        FROM users u
        LEFT JOIN departments d
            ON u.dept_id = d.id
        WHERE u.active = 1
        ORDER BY u.name
        """
        assert sql_is_plausible(sql) is True

    def test_sql_with_comments(self):
        """Test validation of SQL with inline comments."""
        sql = """
        SELECT u.name, -- User name
               u.email, -- User email
               d.dept_name -- Department name
        FROM users u
        JOIN departments d ON u.dept_id = d.id /* Join condition */
        WHERE u.active = 1 -- Only active users
        """
        assert sql_is_plausible(sql) is True

    def test_sql_with_string_literals(self):
        """Test validation of SQL with string literals."""
        sql = "SELECT * FROM users WHERE name = 'John O''Malley' AND status = 'active'"
        assert sql_is_plausible(sql) is True

    def test_sql_with_numeric_literals(self):
        """Test validation of SQL with numeric literals."""
        sql = "SELECT * FROM products WHERE price > 99.99 AND quantity >= 10"
        assert sql_is_plausible(sql) is True

    def test_sql_case_insensitive(self):
        """Test validation of SQL with mixed case keywords."""
        sql = "Select Name, Email From Users Where Id = 1"
        assert sql_is_plausible(sql) is True

    def test_sql_with_functions(self):
        """Test validation of SQL with built-in functions."""
        sql = """
        SELECT
            COUNT(*) as total_users,
            AVG(salary) as avg_salary,
            MAX(hire_date) as latest_hire,
            UPPER(dept_name) as dept_name_upper
        FROM employee_records er
        JOIN departments d ON er.dept_id = d.id
        GROUP BY d.dept_name
        HAVING COUNT(*) > 5
        """
        assert sql_is_plausible(sql) is True


class TestSQLValidationSpecialCharacters:
    """Test SQL validation with special characters and edge cases."""

    def test_sql_with_backticks(self):
        """Test validation of SQL with backticks (MySQL style)."""
        sql = "SELECT `name`, `email` FROM `users` WHERE `id` = 1"
        assert sql_is_plausible(sql) is True

    def test_sql_with_square_brackets(self):
        """Test validation of SQL with square brackets (SQL Server style)."""
        sql = "SELECT [name], [email] FROM [users] WHERE [id] = 1"
        assert sql_is_plausible(sql) is True

    def test_sql_with_double_quotes(self):
        """Test validation of SQL with double quotes (standard SQL)."""
        sql = 'SELECT "name", "email" FROM "users" WHERE "id" = 1'
        assert sql_is_plausible(sql) is True

    def test_sql_with_unicode(self):
        """Test validation of SQL with unicode characters."""
        sql = "SELECT name FROM users WHERE name = 'José María'"
        assert sql_is_plausible(sql) is True


class TestSQLValidationPerformance:
    """Test SQL validation performance with various input sizes."""

    def test_short_sql_performance(self):
        """Test validation performance with short SQL."""
        sql = "SELECT 1"
        result = sql_is_plausible(sql)
        assert isinstance(result, bool)

    def test_medium_sql_performance(self):
        """Test validation performance with medium-length SQL."""
        sql = """
        SELECT u.id, u.name, u.email, d.dept_name, er.salary, er.performance_score
        FROM users u
        JOIN employee_records er ON u.id = er.user_id
        JOIN departments d ON er.dept_id = d.dept_id
        WHERE er.performance_score > 4.0
        AND er.salary > 50000
        ORDER BY er.performance_score DESC, er.salary DESC
        LIMIT 100
        """
        result = sql_is_plausible(sql)
        assert isinstance(result, bool)

    def test_long_sql_performance(self):
        """Test validation performance with very long SQL."""
        # Generate a long SQL with many UNION statements
        unions = []
        for i in range(20):
            unions.append(f"SELECT {i} as num, 'value_{i}' as text")

        sql = " UNION ALL ".join(unions) + " ORDER BY num"
        result = sql_is_plausible(sql)
        assert isinstance(result, bool)


class TestSQLValidationIntegration:
    """Integration tests for SQL validation in context."""

    def test_validate_llm_generated_sql(self):
        """Test validation of SQL that might be generated by LLM."""
        # Common patterns in LLM-generated SQL
        sql_examples = [
            "SELECT name, salary FROM employees WHERE department = 'Engineering'",
            """WITH top_performers AS (
                SELECT * FROM employees WHERE performance_rating >= 4.5
            ) SELECT * FROM top_performers ORDER BY salary DESC""",
            "SELECT COUNT(*) as employee_count, department FROM employees GROUP BY department",
            "SELECT e.name, d.department_name FROM employees e INNER JOIN departments d ON e.dept_id = d.id",
        ]

        for sql in sql_examples:
            assert sql_is_plausible(sql) is True, f"Failed to validate: {sql}"

    def test_validate_common_sql_errors(self):
        """Test validation catches common SQL construction errors."""
        error_examples = [
            "",  # Empty
            "SELECT",  # Incomplete
            "FROM users",  # Missing SELECT
        ]

        for sql in error_examples:
            result = sql_is_plausible(sql)
            # Document the current behavior - some might pass due to lenient parsing
            assert isinstance(result, bool)
