#!/usr/bin/env python3
"""
CLI Usage Examples for Agent Pipeline
Shows different ways to use the command-line interface.
"""

from pathlib import Path
import subprocess
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_cli_command(command, description):
    """Run a CLI command and display results."""
    print(f"\n{'=' * 60}")
    print(f" {description}")
    print(f" Command: {command}")
    print(f"{'=' * 60}")

    try:
        # Split command for subprocess
        cmd_parts = command.split()
        result = subprocess.run(
            cmd_parts, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(" Success!")
            print("\n Output:")
            print(result.stdout)
        else:
            print(" Error!")
            print("\n Error Output:")
            print(result.stderr)

    except Exception as e:
        print(f" Failed to run command: {e}")


def demonstrate_cli_usage():
    """Demonstrate various CLI usage patterns."""

    print(" Agent Pipeline CLI Usage Examples")
    print("=" * 60)
    print("""
    The CLI provides several ways to interact with the agent pipeline:

    1. Direct module execution
    2. Python script execution
    3. Interactive usage
    4. Batch processing
    """)

    # Example CLI commands
    examples = [
        # Basic usage
        ("python -m agent_pipeline.cli.main 'Show all users'", "Basic Query - Get all users"),
        (
            "python -m agent_pipeline.cli.main 'Find employees with salary > 60000'",
            "Filtered Query - High salary employees",
        ),
        (
            "python -m agent_pipeline.cli.main 'Show department budgets and employee counts'",
            "Complex Query - Department analytics",
        ),
        # Using main.py
        ("python main.py", "Main entry point (basic hello)"),
    ]

    print("\n Available CLI Commands:")
    for i, (command, description) in enumerate(examples, 1):
        print(f"{i}. {description}")
        print(f"    {command}")

    print("\n" + "=" * 60)
    print(" CLI Setup Instructions:")
    print("""
    1. Ensure you're in the project root directory
    2. Activate virtual environment: source .venv/bin/activate
    3. Make sure all dependencies are installed: pip install -r requirements.txt
    4. Ensure Ollama is running: ollama serve
    5. Run CLI commands as shown above
    """)

    print("\n CLI Usage Patterns:")
    print("""
    # Basic pattern:
    python -m agent_pipeline.cli.main "<your natural language query>"

    # Examples:
    python -m agent_pipeline.cli.main "Show me all departments"
    python -m agent_pipeline.cli.main "Find top 5 highest paid employees"
    python -m agent_pipeline.cli.main "What's the average salary by department?"

    # For complex queries with quotes:
    python -m agent_pipeline.cli.main 'Find employees hired after "2023-01-01" with good performance'
    """)


def create_interactive_cli_demo():
    """Create an interactive CLI demonstration."""
    print("\n" + "=" * 60)
    print(" Interactive CLI Demo")
    print("=" * 60)

    # Sample queries users might want to try
    sample_queries = [
        "Show all users",
        "Find employees with high performance scores",
        "What departments do we have?",
        "Show employee salaries by department",
        "Find the highest paid employee in each department",
        "Show recent hires",
    ]

    print(" Try these sample queries:")
    for i, query in enumerate(sample_queries, 1):
        print(f"{i}. {query}")

    print("\n To run any of these:")
    print("   python -m agent_pipeline.cli.main '<query>'")

    print("\n Or create your own natural language queries!")
    print("   The agent will convert them to SQL and execute against the database.")


def show_cli_help():
    """Show comprehensive CLI help."""
    print("\n" + "=" * 60)
    print(" CLI Help & Documentation")
    print("=" * 60)

    help_content = """
 AGENT PIPELINE CLI

DESCRIPTION:
    The Agent Pipeline CLI allows you to query a database using natural language.
    It converts your questions into SQL queries and executes them automatically.

USAGE:
    python -m agent_pipeline.cli.main "<natural language query>"

EXAMPLES:
    # Basic queries
    python -m agent_pipeline.cli.main "Show all users"
    python -m agent_pipeline.cli.main "How many employees do we have?"

    # Analytical queries
    python -m agent_pipeline.cli.main "What's the average salary by department?"
    python -m agent_pipeline.cli.main "Find top performing employees"

    # Complex queries
    python -m agent_pipeline.cli.main "Show employees hired in the last year with salary > 50000"

FEATURES:
     Natural language to SQL conversion
     Automatic query execution
     Error handling and retry logic
     Detailed logging
     Multiple output formats

REQUIREMENTS:
    • Python 3.8+
    • Virtual environment activated
    • Ollama server running
    • Database accessible

TROUBLESHOOTING:
    • If Ollama connection fails: Check if 'ollama serve' is running
    • If database errors: Verify database path in config.py
    • If import errors: Ensure virtual environment is activated
    • For detailed logs: Check logs/ directory

CONFIGURATION:
    Edit src/agent_pipeline/config.py to modify:
    • Model settings
    • Database connection
    • Timeout values
    • Logging levels
    """

    print(help_content)


def main():
    """Main function to demonstrate CLI usage."""
    demonstrate_cli_usage()
    create_interactive_cli_demo()
    show_cli_help()

    print("\n" + "=" * 60)
    print(" Ready to use the CLI!")
    print("=" * 60)
    print("""
Next steps:
1. Open a new terminal window
2. Navigate to the project directory
3. Activate virtual environment: source .venv/bin/activate
4. Try a command: python -m agent_pipeline.cli.main "Show all users"
5. Experiment with your own queries!
    """)


if __name__ == "__main__":
    main()
