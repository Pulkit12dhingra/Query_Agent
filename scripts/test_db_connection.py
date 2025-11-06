#!/usr/bin/env python3
"""
Test script for database connection and basic queries.
Tests the database engine, connection, and basic SQL execution.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_pipeline.config import SQLALCHEMY_DATABASE_URI
from agent_pipeline.db.engine import get_engine, test_db_connection
from agent_pipeline.db.execute import execute_sql


def test_database_connection():
    """Test database connection and basic functionality."""
    print(" Testing Database Connection...")

    try:
        # Test engine creation
        print(f" Database URI: {SQLALCHEMY_DATABASE_URI}")
        engine = get_engine()
        print(f" Engine created successfully: {engine}")

        # Test connection
        tables = test_db_connection(engine)
        print(f" Available tables: {tables}")

        # Test basic query
        print("\n Testing basic queries...")

        # Count users
        result = execute_sql(engine, "SELECT COUNT(*) as user_count FROM users")
        print(f" Total users: {result.iloc[0]['user_count']}")

        # Get sample user data - check what columns actually exist
        result = execute_sql(engine, "SELECT * FROM users LIMIT 3")
        print(" Sample users:")
        print(result.to_string(index=False))

        # Test join query
        result = execute_sql(
            engine,
            """
            SELECT u.name, d.dept_name, er.salary
            FROM employee_records er
            JOIN users u ON er.user_id = u.id
            JOIN departments d ON er.dept_id = d.dept_id
            LIMIT 3
        """,
        )
        print("\n Employee information:")
        for _, row in result.iterrows():
            print(f"  - {row['name']}: {row['dept_name']}, ${row['salary']:,.0f}")

        print("\n Database connection test completed successfully!")
        return True

    except Exception as e:
        print(f" Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
