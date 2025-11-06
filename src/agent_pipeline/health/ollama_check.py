# check_ollama_health(): service, models, test prompt

"""Ollama health check and diagnostic utilities."""

import pandas as pd

from ..config import MODEL_NAME, OLLAMA_BASE_URL
from ..llms.client import get_llm


def check_ollama_health() -> bool:
    """Comprehensive Ollama health check and diagnostics"""
    print("OLLAMA HEALTH CHECK")
    print("=" * 50)

    # 1. Check if Ollama service is running
    try:
        import requests

        response = requests.get(f"{OLLAMA_BASE_URL}/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(
                f"[SUCCESS] Ollama service is running (version: {version_info.get('version', 'unknown')})"
            )
        else:
            print(f"[FAILED] Ollama service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAILED] Cannot connect to Ollama service: {e}")
        print("  Please run: ollama serve")
        return False

    # 2. Check available models
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"[SUCCESS] Found {len(models)} available models:")
            for model in models:
                name = model.get("name", "unknown")
                size_gb = model.get("size", 0) / (1024**3)
                print(f"  - {name} ({size_gb:.1f} GB)")

            # Check if our target model is available
            model_names = [m.get("name", "") for m in models]
            if MODEL_NAME in model_names:
                print(f"[SUCCESS] Target model '{MODEL_NAME}' is available")
            else:
                print(f"[FAILED] Target model '{MODEL_NAME}' not found")
                print(f"  Available models: {', '.join(model_names)}")
                return False
        else:
            print(f"[FAILED] Cannot list models, status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAILED] Error checking models: {e}")
        return False

    # 3. Test simple LLM call
    try:
        print("\n[TESTING] Testing simple LLM call...")
        start_time = pd.Timestamp.now()
        llm = get_llm()
        test_response = llm.invoke("Respond with exactly: 'Ollama working'")
        end_time = pd.Timestamp.now()
        duration = (end_time - start_time).total_seconds()

        if "working" in test_response.lower():
            print(f"[SUCCESS] LLM call successful ({duration:.1f}s)")
            print(f"  Response: {test_response[:100]}...")
        else:
            print(f"[WARNING] LLM responded but content unexpected: {test_response[:100]}...")
        return True
    except Exception as e:
        print(f"[FAILED] LLM call failed: {e}")
        if "timeout" in str(e).lower():
            print("  This is the timeout issue we're trying to fix!")
        return False
