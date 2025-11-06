#!/usr/bin/env python3
"""
Example usage of the modular agent pipeline.
This replaces the notebook-based approach with clean modular code.
"""

from src.agent_pipeline import get_final_result, run_query_pipeline


def main():
    """Example usage of the agent pipeline."""

    # Example query
    user_request = (
        "Top 10 highest paid employees with their department, performance score, and hire date."
    )

    print(f"Running query: {user_request}")
    print("=" * 80)

    try:
        # Run the complete pipeline
        results = run_query_pipeline(user_request)

        # Display step-by-step results
        print("\n" + "=" * 80)
        print("PIPELINE EXECUTION RESULTS")
        print("=" * 80)

        for result in results:
            print(f"\nStep {result.step_id}: {result.title}")
            if result.description:
                print(f"Description: {result.description}")

            if result.error:
                print(f" FAILED: {result.error}")
            else:
                print(f" SUCCESS: {len(result.result_df)} rows returned")
                if result.sql:
                    print(f"SQL: {result.sql[:100]}...")

        # Display final result
        final_result = get_final_result(results)
        if final_result and final_result.result_df is not None:
            print("\n" + "=" * 80)
            print("FINAL RESULT")
            print("=" * 80)
            print("Final SQL Query:")
            print(final_result.sql)
            print(f"\nResult ({len(final_result.result_df)} rows):")
            print(final_result.result_df.to_string())
        else:
            print("\n No successful final result generated")

    except Exception as e:
        print(f" Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
