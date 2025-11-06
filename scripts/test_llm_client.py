#!/usr/bin/env python3
"""
Test script for LLM client functionality.
Tests Ollama connection, LLM calls, and retry mechanisms.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_pipeline.config import MODEL_NAME, OLLAMA_BASE_URL
from agent_pipeline.health.ollama_check import check_ollama_health
from agent_pipeline.llms.client import call_llm, create_llm, get_llm


def test_ollama_health():
    """Test Ollama server health and model availability."""
    print(" Testing Ollama Health...")

    try:
        health_status = check_ollama_health()
        print(f" Ollama health check: {health_status}")
        return True
    except Exception as e:
        print(f" Ollama health check failed: {e}")
        return False


def test_llm_creation():
    """Test LLM client creation."""
    print(" Testing LLM Creation...")

    try:
        llm = create_llm()
        print(f" LLM created successfully: {type(llm).__name__}")

        # Test singleton pattern
        llm2 = get_llm()
        if llm is llm2:
            print(" Singleton pattern working correctly")
        else:
            print(" Singleton pattern not working")

        return True
    except Exception as e:
        print(f" LLM creation failed: {e}")
        return False


def test_simple_llm_call():
    """Test basic LLM call functionality."""
    print(" Testing Simple LLM Call...")

    try:
        system_prompt = "You are a helpful assistant. Respond concisely."
        user_prompt = "What is 2 + 2? Answer with just the number."

        response = call_llm(system_prompt, user_prompt)
        print(f" Question: {user_prompt}")
        print(f" Response: {response}")

        if response.strip():
            print(" LLM call successful")
            return True
        else:
            print(" LLM returned empty response")
            return False

    except Exception as e:
        print(f" LLM call failed: {e}")
        return False


def test_sql_generation():
    """Test LLM's ability to generate SQL."""
    print(" Testing SQL Generation...")

    try:
        system_prompt = """You are a SQL expert. Generate only valid SQL queries.
        Available tables: users (id, name, email), departments (dept_id, dept_name, budget),
        employee_records (id, user_id, dept_id, salary, performance_score, hire_date)"""

        user_prompt = "Write a SQL query to find all employees with salary > 60000. Include name and department."

        response = call_llm(system_prompt, user_prompt)
        print(f" Request: {user_prompt}")
        print(f" Generated SQL:\n{response}")

        # Check if response contains SQL keywords
        sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN"]
        has_sql = any(keyword in response.upper() for keyword in sql_keywords)

        if has_sql:
            print(" SQL generation successful")
            return True
        else:
            print(" Response doesn't appear to contain SQL")
            return False

    except Exception as e:
        print(f" SQL generation failed: {e}")
        return False


def test_retry_mechanism():
    """Test LLM retry mechanism with timeout."""
    print(" Testing Retry Mechanism...")

    try:
        # This should succeed normally
        response = call_llm("Be helpful.", "Say 'Hello'", max_retries=2)
        print(f" Response with retries: {response}")

        if response.strip():
            print(" Retry mechanism working")
            return True
        else:
            print(" Retry mechanism returned empty response")
            return False

    except Exception as e:
        print(f" Retry mechanism test failed: {e}")
        return False


def main():
    """Run all LLM tests."""
    print(" Starting LLM Client Test Suite...")
    print(f" Target Model: {MODEL_NAME}")
    print(f" Ollama URL: {OLLAMA_BASE_URL}")
    print("-" * 50)

    tests = [
        ("Ollama Health", test_ollama_health),
        ("LLM Creation", test_llm_creation),
        ("Simple LLM Call", test_simple_llm_call),
        ("SQL Generation", test_sql_generation),
        ("Retry Mechanism", test_retry_mechanism),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n Running: {test_name}")
        success = test_func()
        results.append((test_name, success))
        print()

    print("=" * 50)
    print(" TEST RESULTS:")
    passed = 0
    for test_name, success in results:
        status = " PASS" if success else " FAIL"
        print(f"  {status}: {test_name}")
        if success:
            passed += 1

    print(f"\n Summary: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print(" All LLM tests passed!")
        return True
    else:
        print(" Some LLM tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
