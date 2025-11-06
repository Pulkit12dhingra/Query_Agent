#!/usr/bin/env python3
"""
Simple CLI test script to verify the command-line interface works.
"""

import os
from pathlib import Path
import subprocess
import sys


def test_cli_basic():
    """Test basic CLI functionality."""
    print(" Testing CLI Basic Functionality")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent.parent

    # Simple test query
    test_query = "Show all users"

    cmd = [sys.executable, "-m", "agent_pipeline.cli.main", test_query]

    print(f" Running command: {' '.join(cmd)}")
    print(f" Working directory: {project_dir}")

    try:
        # Set up environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_dir / "src")

        result = subprocess.run(
            cmd, cwd=project_dir, env=env, capture_output=True, text=True, timeout=30
        )

        print(f"\n Return code: {result.returncode}")

        if result.stdout:
            print(" Output:")
            print(result.stdout)

        if result.stderr:
            print(" Error output:")
            print(result.stderr)

        if result.returncode == 0:
            print(" CLI test passed!")
            return True
        else:
            print(" CLI test failed!")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ CLI test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f" CLI test error: {e}")
        return False


def test_cli_help():
    """Test CLI help and error handling."""
    print("\n Testing CLI Help/Error Handling")
    print("=" * 50)

    project_dir = Path(__file__).parent.parent

    # Test with no arguments
    cmd = [sys.executable, "-m", "agent_pipeline.cli.main"]

    print(f" Running command: {' '.join(cmd)}")

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_dir / "src")

        result = subprocess.run(
            cmd, cwd=project_dir, env=env, capture_output=True, text=True, timeout=10
        )

        print(f" Return code: {result.returncode}")

        if result.stdout:
            print(" Output:")
            print(result.stdout)

        if result.stderr:
            print(" Error output:")
            print(result.stderr)

        # Should return error code for no arguments
        if result.returncode != 0:
            print(" CLI help test passed (correctly showed usage)")
            return True
        else:
            print(" CLI should show usage when no arguments provided")
            return False

    except Exception as e:
        print(f" CLI help test error: {e}")
        return False


def show_quick_start():
    """Show quick start instructions."""
    print("\n Quick Start Instructions")
    print("=" * 50)

    instructions = """
To use the CLI immediately:

1. Open terminal and navigate to project directory:
   cd /Users/pulkit/Desktop/test/query_automation

2. Activate virtual environment:
   source .venv/bin/activate

3. Ensure Ollama is running:
   ollama serve

4. Run a simple query:
   python -m agent_pipeline.cli.main "Show all users"

5. Try more complex queries:
   python -m agent_pipeline.cli.main "Find employees with salary > 60000"
   python -m agent_pipeline.cli.main "What's the average salary by department?"
   python -m agent_pipeline.cli.main "Show top 5 highest paid employees"

 Query Tips:
   • Use natural language
   • Be specific about what data you want
   • Ask for analytics (averages, counts, top N, etc.)
   • Reference table relationships naturally

 Available Data:
   • users (id, name, email)
   • departments (dept_id, dept_name, budget)
   • employee_records (user_id, dept_id, salary, performance_score, hire_date)
"""

    print(instructions)


def main():
    """Main test function."""
    print(" CLI Testing & Usage Guide")
    print("=" * 60)

    # Run tests
    basic_test = test_cli_basic()
    help_test = test_cli_help()

    # Show results
    print("\n Test Summary:")
    print(f"  Basic CLI test: {' PASS' if basic_test else ' FAIL'}")
    print(f"  Help/Error test: {' PASS' if help_test else ' FAIL'}")

    # Show quick start
    show_quick_start()

    if basic_test and help_test:
        print("\n CLI is working correctly!")
    else:
        print("\n Some CLI tests failed - check configuration")


if __name__ == "__main__":
    main()
