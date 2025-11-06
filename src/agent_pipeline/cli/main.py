# Typer/Click CLI: `python -m sample_pipeline ...`

"""Command-line interface for the agent pipeline."""

from pathlib import Path
import sys

# Add src to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from agent_pipeline.orchestration.pipeline import (
    get_final_result,
    initialize_pipeline,
    run_query_pipeline,
)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m agent_pipeline.cli.main '<your query>'")
        print("Example: python -m agent_pipeline.cli.main 'Show top 10 highest paid employees'")
        sys.exit(1)

    user_request = " ".join(sys.argv[1:])

    try:
        print(f"Processing query: {user_request}")
        print("=" * 60)

        # Initialize pipeline
        print("Initializing pipeline...")
        if not initialize_pipeline():
            print("Pipeline initialization failed!")
            sys.exit(1)

        # Run query
        results = run_query_pipeline(user_request)

        # Display final result
        final_result = get_final_result(results)
        if final_result:
            print("\nFINAL RESULT:")
            print("=" * 60)
            print(f"SQL: {final_result.sql}")
            print(f"Rows: {len(final_result.result_df)}")
            print("\nData Preview:")
            print(final_result.result_df.head(10))
        else:
            print("No successful results generated.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
