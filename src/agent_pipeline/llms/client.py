# OllamaLLM wrapper, call_llm() with retry/backoff

"""LLM client wrapper with retry logic and timeout handling."""

import time

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import (
    LLM_MAX_RETRIES,
    LLM_TIMEOUT,
    MODEL_NAME,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
    OLLAMA_REPEAT_PENALTY,
    OLLAMA_TEMPERATURE,
    OLLAMA_TOP_P,
)

# Try to import the appropriate Ollama class
try:
    # Try the new recommended import first
    from langchain_ollama import OllamaLLM

    print("Using new langchain_ollama.OllamaLLM")
except ImportError:
    # Fallback to the old import if new package not available
    from langchain_community.llms import Ollama as OllamaLLM

    print("Using legacy langchain_community.llms.Ollama")

# Global LLM instance
_llm_instance: OllamaLLM | None = None


def get_llm() -> OllamaLLM:
    """Get the global LLM instance, creating it if necessary."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_llm()
    return _llm_instance


def create_llm() -> OllamaLLM:
    """Create and configure the Ollama LLM instance."""
    print(f"Connecting to Ollama model: {MODEL_NAME}")
    print("Make sure Ollama is running locally (ollama serve)")

    # Use only valid parameters for Ollama
    llm = OllamaLLM(
        model=MODEL_NAME,
        temperature=OLLAMA_TEMPERATURE,
        # Increased timeout to handle complex queries
        timeout=LLM_TIMEOUT,  # 5 minutes timeout (was default 60 seconds)
        # Valid parameters for Ollama
        num_predict=OLLAMA_NUM_PREDICT,  # max tokens - increased for complex queries
        top_p=OLLAMA_TOP_P,
        repeat_penalty=OLLAMA_REPEAT_PENALTY,
        # Additional valid parameters
        num_ctx=OLLAMA_NUM_CTX,  # context window
    )

    # Test the connection with a simple query
    print("Testing Ollama connection...")
    try:
        test_response = llm.invoke("Hello, respond with just 'OK'")
        print("Ollama connection successful!")
        print(f"Test response: {test_response[:50]}...")
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        print("Please ensure Ollama is running: ollama serve")
        raise

    print("Setup complete!")
    return llm


def call_llm(system_prompt: str, user_prompt: str, max_retries: int = None) -> str:
    """Small helper to call the LC LLM with system+human messages, with retry logic for timeouts."""
    if max_retries is None:
        max_retries = LLM_MAX_RETRIES

    llm = get_llm()
    msgs = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Calling Ollama (attempt {attempt + 1}/{max_retries})...")
            out = llm.invoke(msgs)
            if hasattr(out, "content"):
                print("[LLM] Response received successfully")
                return str(out.content or "").strip()
            # Fallback for HF text
            print("[LLM] Response received successfully (fallback format)")
            return str(out).strip()

        except Exception as e:
            error_msg = str(e)
            if "Read timed out" in error_msg or "timeout" in error_msg.lower():
                print(f"[LLM] Timeout on attempt {attempt + 1}/{max_retries}: {error_msg}")
                if attempt < max_retries - 1:
                    print("[LLM] Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    print("[LLM] All retry attempts failed due to timeout")
                    raise TimeoutError(
                        f"Ollama failed to respond after {max_retries} attempts due to timeout"
                    )
            else:
                print(f"[LLM] Non-timeout error: {error_msg}")
                raise

    # Should not reach here
    raise Exception("Unexpected error in call_llm")
