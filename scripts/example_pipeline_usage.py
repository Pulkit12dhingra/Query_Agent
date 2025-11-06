#!/usr/bin/env python3
"""
Example script demonstrating simple agent pipeline usage.
Shows how to run a basic query through the complete pipeline.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_pipeline.config import SQLALCHEMY_DATABASE_URI
from agent_pipeline.orchestration.pipeline import initialize_pipeline, run_query_pipeline


def example_simple_query():
    """Example of running a simple query through the pipeline."""
    print(" Simple Pipeline Query Example")
    print("=" * 50)

    try:
        # Initialize the pipeline
        print(" Initializing pipeline...")
        init_success = initialize_pipeline()

        if not init_success:
            print(" Pipeline initialization failed")
            return False

        print(" Pipeline initialized successfully")

        # Example query
        user_question = "Show me all employees with their departments and salaries"

        print(f"\n User Question: {user_question}")
        print(" Processing query through agent pipeline...")

        # Run the query
        results = run_query_pipeline(user_question)

        print(f"\n Query completed with {len(results)} steps")

        # Display results
        for i, step in enumerate(results, 1):
            print(f"\n--- Step {i}: {step.title} ---")
            print(f" Description: {step.description}")

            if step.sql:
                print(f" SQL: {step.sql}")

            if step.error:
                print(f" Error: {step.error}")
            elif step.result_df is not None and not step.result_df.empty:
                print(f" Success: {len(step.result_df)} rows returned")
                print(" Sample results:")
                print(step.result_df.head(3).to_string(index=False))
            else:
                print(" No results returned")

        # Check if we got a successful result
        successful_steps = [s for s in results if s.error is None and s.result_df is not None]
        if successful_steps:
            print("\n Query completed successfully!")
            final_result = successful_steps[-1]
            print(f" Final result: {len(final_result.result_df)} rows")
            return True
        else:
            print("\n Query completed but no successful results found")
            return False

    except Exception as e:
        print(f" Pipeline execution failed: {e}")
        return False


def example_complex_query():
    """Example of running a more complex analytical query."""
    print("\n Complex Pipeline Query Example")
    print("=" * 50)

    try:
        # Complex analytical question
        user_question = """
        Find the top performing employees in each department.
        Show employee name, department, salary, and performance score.
        Only include employees with performance score above 4.0.
        """

        print(f" User Question: {user_question.strip()}")
        print(" Processing complex query...")

        # Run the query
        results = run_query_pipeline(user_question, max_steps=5)

        print(f"\n Complex query completed with {len(results)} steps")

        # Display results with more detail
        for i, step in enumerate(results, 1):
            print(f"\n--- Step {i}: {step.title} ---")
            print(f" {step.description}")

            if step.sql:
                print(" Generated SQL:")
                # Format SQL for better readability
                sql_lines = step.sql.strip().split("\n")
                for line in sql_lines:
                    print(f"    {line.strip()}")

            if step.error:
                print(f" Error: {step.error}")
            elif step.result_df is not None and not step.result_df.empty:
                print(f" Success: {len(step.result_df)} rows")
                if len(step.result_df) <= 10:
                    print(" All results:")
                    print(step.result_df.to_string(index=False))
                else:
                    print(" First 5 results:")
                    print(step.result_df.head(5).to_string(index=False))
            else:
                print(" No data returned")

        return True

    except Exception as e:
        print(f" Complex query failed: {e}")
        return False


def example_error_handling():
    """Example showing how the pipeline handles errors."""
    print("\n Error Handling Example")
    print("=" * 50)

    try:
        # Intentionally problematic query
        user_question = "Show me data from a table that doesn't exist called 'unicorns'"

        print(f" User Question: {user_question}")
        print(" Testing error handling...")

        # Run the query
        results = run_query_pipeline(user_question, max_steps=3)

        print(f"\n Error handling test completed with {len(results)} steps")

        # Show how errors are handled
        for i, step in enumerate(results, 1):
            print(f"\n--- Step {i}: {step.title} ---")
            print(f" {step.description}")

            if step.sql:
                print(f" SQL: {step.sql}")

            if step.error:
                print(f" Error (as expected): {step.error}")
            else:
                print(" Unexpected success")

        print(
            "\n Notice how the pipeline gracefully handles errors and continues trying different approaches."
        )
        return True

    except Exception as e:
        print(f" Error handling test failed: {e}")
        return False


def main():
    """Run all pipeline examples."""
    print(" Agent Pipeline Usage Examples")
    print(f" Database: {SQLALCHEMY_DATABASE_URI}")
    print("=" * 60)

    examples = [
        ("Simple Query", example_simple_query),
        ("Complex Query", example_complex_query),
        ("Error Handling", example_error_handling),
    ]

    for example_name, example_func in examples:
        print(f"\n Running: {example_name}")
        try:
            success = example_func()
            status = " Completed" if success else " Completed with issues"
            print(f"\n{status}: {example_name}")
        except Exception as e:
            print(f"\n Failed: {example_name} - {e}")

    print("\n" + "=" * 60)
    print(" All examples completed!")
    print("\n Tips:")
    print("  - Check the logs/ directory for detailed execution logs")
    print("  - Modify the queries above to test different scenarios")
    print("  - Use initialize_pipeline() and run_query() in your own scripts")


if __name__ == "__main__":
    main()
