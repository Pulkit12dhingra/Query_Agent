#!/usr/bin/env python3
"""
Batch CLI usage example - run multiple queries automatically.
"""

from pathlib import Path
import subprocess
import sys
import time


def run_cli_query(query, timeout=30):
    """Run a single CLI query and return results."""
    project_dir = Path(__file__).parent.parent

    cmd = [sys.executable, "-m", "agent_pipeline.cli.main", query]

    try:
        result = subprocess.run(
            cmd, cwd=project_dir, capture_output=True, text=True, timeout=timeout
        )

        return {
            "query": query,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "query": query,
            "success": False,
            "output": "",
            "error": f"Query timed out after {timeout} seconds",
        }
    except Exception as e:
        return {"query": query, "success": False, "output": "", "error": str(e)}


def batch_query_example():
    """Run a batch of queries to demonstrate CLI capabilities."""
    print(" Batch CLI Query Example")
    print("=" * 60)

    # Define a set of queries to test different aspects
    queries = [
        "Show all users",
        "How many employees do we have?",
        "What departments are available?",
        "Find employees with salary greater than 60000",
        "Show average salary by department",
        "Find the highest paid employee",
        "Show recent hires from this year",
        "What's the total budget across all departments?",
    ]

    print(f" Running {len(queries)} queries...")
    print()

    results = []

    for i, query in enumerate(queries, 1):
        print(f" Query {i}/{len(queries)}: {query}")

        start_time = time.time()
        result = run_cli_query(query)
        duration = time.time() - start_time

        results.append(result)

        if result["success"]:
            print(f" Success ({duration:.1f}s)")
            # Show first few lines of output
            output_lines = result["output"].split("\n")[:3]
            for line in output_lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f" Failed ({duration:.1f}s)")
            print(f"   Error: {result['error'][:100]}")

        print()

        # Small delay between queries
        time.sleep(1)

    # Summary
    successful = sum(1 for r in results if r["success"])
    print("=" * 60)
    print(" Batch Query Summary")
    print(f" Successful: {successful}/{len(queries)}")
    print(f" Failed: {len(queries) - successful}/{len(queries)}")

    if successful == len(queries):
        print(" All queries completed successfully!")
    else:
        print("\n Failed queries:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['query']}")
                print(f"    Error: {result['error']}")


def interactive_cli_demo():
    """Create an interactive CLI demonstration."""
    print("\n Interactive CLI Demo Mode")
    print("=" * 60)

    predefined_queries = [
        "Show all users",
        "Find high-salary employees (> 65000)",
        "Department budget analysis",
        "Top performers by department",
        "Recent hiring trends",
    ]

    print("Choose a query to run:")
    for i, query in enumerate(predefined_queries, 1):
        print(f"{i}. {query}")
    print("0. Enter custom query")
    print("q. Quit")

    while True:
        try:
            choice = input("\nEnter your choice: ").strip().lower()

            if choice == "q":
                print(" Goodbye!")
                break
            elif choice == "0":
                custom_query = input("Enter your custom query: ").strip()
                if custom_query:
                    print(f"\n Running: {custom_query}")
                    result = run_cli_query(custom_query)
                    display_result(result)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(predefined_queries):
                        query = predefined_queries[idx]
                        print(f"\n Running: {query}")
                        result = run_cli_query(query)
                        display_result(result)
                    else:
                        print(" Invalid choice. Please try again.")
                except ValueError:
                    print(" Invalid choice. Please enter a number.")

        except KeyboardInterrupt:
            print("\n Goodbye!")
            break
        except EOFError:
            print("\n Goodbye!")
            break


def display_result(result):
    """Display query result in a formatted way."""
    if result["success"]:
        print(" Query successful!")
        print(" Output:")
        print(result["output"])
    else:
        print(" Query failed!")
        print(f"Error: {result['error']}")


def main():
    """Main function."""
    print(" CLI Batch Processing & Interactive Demo")
    print()

    # Ask user what they want to do
    print("What would you like to do?")
    print("1. Run batch queries automatically")
    print("2. Interactive query mode")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        batch_query_example()
    elif choice == "2":
        interactive_cli_demo()
    elif choice == "3":
        batch_query_example()
        interactive_cli_demo()
    else:
        print(" Invalid choice. Running batch example by default.")
        batch_query_example()


if __name__ == "__main__":
    main()
