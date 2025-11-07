#!/usr/bin/env python3
"""Example client for the Query Automation Agent API."""

import sys

import requests


def query_agent(question: str, base_url: str = "http://127.0.0.1:8000"):
    """Send a natural language query to the agent."""
    try:
        response = requests.post(
            f"{base_url}/query",
            headers={"Content-Type": "application/json"},
            json={"query": question},
            timeout=60,  # 60 second timeout
        )

        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✓ Query: {result['query']}")
                print(f"Generated SQL: {result['sql']}")
                print(f"Rows returned: {result['row_count']}")

                if result["data"]:
                    print("Data preview (first 5 rows):")
                    for i, row in enumerate(result["data"][:5], 1):
                        print(f"  {i}. {row}")

                print(
                    f"Execution: {result['metadata']['successful_steps']}/{result['metadata']['total_steps']} steps successful"
                )
                return True
            else:
                print(f"✗ Query failed: {result['error']}")
                return False
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def check_health(base_url: str = "http://127.0.0.1:8000"):
    """Check if the API server is healthy."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            if health["status"] == "healthy":
                print("✓ API server is healthy and ready")
                return True
            else:
                print(f"! API server is unhealthy: {health['message']}")
                return False
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to API server: {e}")
        return False


def get_schema(base_url: str = "http://127.0.0.1:8000"):
    """Get database schema information."""
    try:
        response = requests.get(f"{base_url}/schema", timeout=30)
        if response.status_code == 200:
            schema = response.json()
            if schema["success"]:
                db_info = schema["database_info"]
                print(f"Database has {db_info['table_count']} tables:")
                for table in db_info["tables"]:
                    print(f"  - {table}")
                return True
            else:
                print(f"✗ Schema request failed: {schema['error']}")
                return False
        else:
            print(f"Schema request error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Schema request error: {e}")
        return False


def main():
    """Main function - interactive mode or command line query."""
    base_url = "http://127.0.0.1:8000"

    print("Query Automation Agent - API Client")
    print("=" * 50)

    # Check if server is running
    if not check_health(base_url):
        print("\nMake sure the API server is running with: python run_api.py")
        sys.exit(1)

    # If query provided as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\nProcessing query: {query}")
        print("-" * 50)
        query_agent(query, base_url)
        return

    # Interactive mode
    print("\nAvailable commands:")
    print("  - Type a natural language query")
    print("  - 'schema' - Show database schema")
    print("  - 'examples' - Show example queries")
    print("  - 'quit' or 'exit' - Exit")

    example_queries = [
        "Show all employees",
        "Find the highest paid employee",
        "Count employees by department",
        "Show average salary by department",
        "List employees hired in the last year",
        "Find employees with salary > 50000",
    ]

    while True:
        try:
            query = input("\nEnter your query: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            elif query.lower() == "schema":
                print("\nDatabase Schema:")
                print("-" * 30)
                get_schema(base_url)
            elif query.lower() == "examples":
                print("\nExample queries:")
                print("-" * 20)
                for i, example in enumerate(example_queries, 1):
                    print(f"  {i}. {example}")
            elif query:
                print(f"\nProcessing: {query}")
                print("-" * 50)
                query_agent(query, base_url)
            else:
                print("Please enter a query or command")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
