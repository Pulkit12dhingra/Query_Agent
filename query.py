#!/usr/bin/env python3
"""
Simple CLI wrapper for easy querying.
Usage: python scripts/query.py "Your natural language question"
"""

from pathlib import Path
import subprocess
import sys


def main():
    """Simple wrapper for the CLI."""
    if len(sys.argv) < 2:
        print(" Agent Pipeline Query Tool")
        print("=" * 40)
        print("Usage: python scripts/query.py '<your question>'")
        print()
        print("Examples:")
        print("  python scripts/query.py 'Show all users'")
        print("  python scripts/query.py 'Find employees with salary > 60000'")
        print("  python scripts/query.py 'What departments do we have?'")
        print("  python scripts/query.py 'Show average salary by department'")
        print()
        sys.exit(1)

    # Get query from command line
    query = " ".join(sys.argv[1:])

    # Project root directory
    project_dir = Path(__file__).parent.parent

    # Build command
    cmd = [sys.executable, "-m", "agent_pipeline.cli.main", query]

    print(f" Query: {query}")
    print(" Processing...")
    print()

    try:
        # Run the CLI with proper environment
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=project_dir,
            env={**dict(os.environ), "PYTHONPATH": str(project_dir / "src")},
            timeout=120,  # 2 minute timeout
        )

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print("⏰ Query timed out after 2 minutes")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n Query cancelled")
        sys.exit(1)
    except Exception as e:
        print(f" Error running query: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import os

    main()
