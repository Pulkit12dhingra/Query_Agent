# OllamaLLM wrapper, call_llm() with retry/backoff

"""LLM client wrapper with retry logic and timeout handling.

This module provides LLM integration with Ollama as the primary method,
and HuggingFace models as an alternative option.
"""

import time
from typing import Any, cast

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import (
    HF_DEVICE,
    HF_MAX_NEW_TOKENS,
    HF_MODEL_NAME,
    HF_TEMPERATURE,
    HF_TOP_P,
    LLM_MAX_RETRIES,
    LLM_TIMEOUT,
    MODEL_NAME,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
    OLLAMA_REPEAT_PENALTY,
    OLLAMA_TEMPERATURE,
    OLLAMA_TOP_P,
    USE_HUGGINGFACE,
)

# Try to import the appropriate Ollama class
_OllamaLLM: type[Any]
try:  # pragma: no cover - exercised at runtime
    # Try the new recommended import first
    import langchain_ollama as _langchain_ollama_module

    _OllamaLLM = _langchain_ollama_module.OllamaLLM
    print("Using new langchain_ollama.OllamaLLM")
except ImportError:  # pragma: no cover - executed when legacy package present
    # Fallback to the old import if new package not available
    from langchain_community import llms as _langchain_community_llms_module

    _OllamaLLM = _langchain_community_llms_module.Ollama
    print("Using legacy langchain_community.llms.Ollama")

OllamaLLM: type[Any] = _OllamaLLM

# HuggingFace dependencies are imported lazily inside create_huggingface_llm()

# Global LLM instance (OllamaLLM or HuggingFacePipeline)
_llm_instance: Any = None


def get_llm() -> Any:
    """Get the global LLM instance, creating it if necessary."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_huggingface_llm(HF_MODEL_NAME) if USE_HUGGINGFACE else create_llm()
    return _llm_instance


def create_llm() -> Any:
    """Create and configure the Ollama LLM instance.

    This is the primary method for LLM creation using Ollama.
    For HuggingFace models, see create_huggingface_llm() below.
    """
    print(f"Connecting to Ollama model: {MODEL_NAME}")
    print("Make sure Ollama is running locally (ollama serve)")

    # Use only valid parameters for Ollama
    llm = cast(Any, OllamaLLM)(
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
    if USE_HUGGINGFACE:
        return _call_huggingface_with_retry(llm, system_prompt, user_prompt, max_retries)

    return _call_ollama_with_retry(llm, system_prompt, user_prompt, max_retries)


def _call_ollama_with_retry(
    llm: Any, system_prompt: str, user_prompt: str, max_retries: int
) -> str:
    """Invoke Ollama with retry handling."""
    msgs = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Calling Ollama (attempt {attempt + 1}/{max_retries})...")
            out = llm.invoke(msgs)
            print("[LLM] Response received successfully")
            return _extract_response_text(out)

        except Exception as e:  # noqa: PERF203 - clarity trumps micro-optimisation here
            error_msg = str(e)
            if "Read timed out" in error_msg or "timeout" in error_msg.lower():
                print(f"[LLM] Timeout on attempt {attempt + 1}/{max_retries}: {error_msg}")
                if attempt < max_retries - 1:
                    print("[LLM] Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                print("[LLM] All retry attempts failed due to timeout")
                raise TimeoutError(
                    f"Ollama failed to respond after {max_retries} attempts due to timeout"
                ) from e

            print(f"[LLM] Non-timeout error: {error_msg}")
            raise

    raise Exception("Unexpected error in call_llm")


def _format_hf_prompt(system_prompt: str, user_prompt: str) -> str:
    """Format prompts for instruction-oriented HuggingFace models."""
    sys_content = system_prompt.strip()
    user_content = user_prompt.strip()
    return f"System: {sys_content}\n\nUser: {user_content}\n\nAssistant:"


def _call_huggingface_with_retry(
    llm: Any, system_prompt: str, user_prompt: str, max_retries: int
) -> str:
    """Invoke a HuggingFace model with retry handling."""
    combined_prompt = _format_hf_prompt(system_prompt, user_prompt)

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Calling HuggingFace model (attempt {attempt + 1}/{max_retries})...")
            response = llm.invoke(combined_prompt)
            print("[LLM] Response received successfully")
            return _extract_response_text(response)

        except Exception as e:
            error_msg = str(e)
            print(f"[LLM] HuggingFace error on attempt {attempt + 1}/{max_retries}: {error_msg}")
            if attempt < max_retries - 1:
                print("[LLM] Retrying in 3 seconds...")
                time.sleep(3)
                continue
            print("[LLM] All retry attempts failed for HuggingFace model")
            raise

    raise Exception("Unexpected error in HuggingFace call")


def _extract_response_text(out: Any) -> str:
    """Normalise LLM responses to plain text."""
    if hasattr(out, "content"):
        return str(out.content or "").strip()
    return str(out).strip()


# =============================================================================
# HUGGINGFACE MODEL SUPPORT (ALTERNATIVE TO OLLAMA)
# =============================================================================
#
# The following functions provide an alternative to Ollama using HuggingFace models.
# To use HuggingFace instead of Ollama:
#
# 1. Install required packages:
#    uv add transformers torch langchain-huggingface accelerate
# 2. Set USE_HUGGINGFACE=True (via config or environment) and override HF_* settings if needed
# 3. call_llm() will automatically pick the HuggingFace backend once enabled
#
# Popular models for SQL generation:
# - "microsoft/DialoGPT-medium" (lighter, faster)
# - "microsoft/CodeBERT-base" (code-focused)
# - "codellama/CodeLlama-7b-Instruct-hf" (instruction-tuned)
# - "WizardLM/WizardCoder-Python-7B-V1.0" (Python/SQL focused)
# - "bigcode/starcoder" (code generation)


def create_huggingface_llm(model_name: str | None = None):
    """Create and configure a HuggingFace LLM instance."""
    resolved_model = model_name or HF_MODEL_NAME
    print(f"Loading HuggingFace model: {resolved_model}")
    print("This may take a few minutes on first run...")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    except ImportError as exc:
        raise ImportError(
            "transformers is required for HuggingFace support. "
            "Install it with `uv add transformers`."
        ) from exc

    try:
        import torch
    except ImportError as exc:
        raise ImportError(
            "torch is required for HuggingFace support. Install it with `uv add torch`."
        ) from exc

    try:
        from langchain_huggingface import HuggingFacePipeline
    except ImportError as exc:
        raise ImportError(
            "langchain-huggingface is required for HuggingFace support. "
            "Install it with `uv add langchain-huggingface`."
        ) from exc

    device = _resolve_hf_device(torch, HF_DEVICE)
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(resolved_model)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    torch_dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    model = AutoModelForCausalLM.from_pretrained(  # type: ignore[arg-type]
        resolved_model,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )

    if device != "cpu":
        cast(Any, model).to(device)

    pipeline_fn = cast(Any, pipeline)
    text_pipeline = pipeline_fn(  # type: ignore[arg-type]
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=HF_MAX_NEW_TOKENS,
        temperature=HF_TEMPERATURE,
        do_sample=True,
        top_p=HF_TOP_P,
        repetition_penalty=OLLAMA_REPEAT_PENALTY,
        return_full_text=False,  # Only return generated text
    )

    llm = HuggingFacePipeline(pipeline=text_pipeline)

    # Test the model
    print("Testing HuggingFace model connection...")
    try:
        test_response = llm.invoke("Hello, respond with just 'OK'")
        print("HuggingFace model loaded successfully!")
        print(f"Test response: {str(test_response)[:50]}...")
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"Failed to verify HuggingFace model: {exc}")
        raise

    print("HuggingFace setup complete!")
    return llm


def _resolve_hf_device(torch_module: Any, requested: str) -> str:
    """Resolve the device string to use for HuggingFace models."""
    req = (requested or "auto").strip().lower()
    if req != "auto":
        return req

    if torch_module.cuda.is_available():
        return "cuda"

    mps_backend = getattr(getattr(torch_module, "backends", None), "mps", None)
    if mps_backend and mps_backend.is_available():
        return "mps"

    return "cpu"


def call_huggingface_llm(system_prompt: str, user_prompt: str, max_retries: int = None) -> str:
    """Call HuggingFace LLM with system+user prompts and retry logic.

    This is an alternative to call_llm() for use with HuggingFace models.

    IMPORTANT: This function requires HuggingFace setup. See create_huggingface_llm()

    Args:
        system_prompt: System instructions for the model
        user_prompt: User query or input
        max_retries: Number of retry attempts for failed calls

    Returns:
        str: Model response text

    Example usage:
        # Instead of: call_llm(system, user)
        # Use: call_huggingface_llm(system, user)
    """
    if max_retries is None:
        max_retries = LLM_MAX_RETRIES

    if not USE_HUGGINGFACE:
        raise RuntimeError(
            "HuggingFace support is disabled. Set USE_HUGGINGFACE=True in config.py to enable it."
        )

    llm = get_llm()
    return _call_huggingface_with_retry(llm, system_prompt, user_prompt, max_retries)


# =============================================================================
# CONFIGURATION GUIDE FOR HUGGINGFACE MODELS
# =============================================================================
#
# To switch from Ollama to HuggingFace models:
#
# 1. INSTALL DEPENDENCIES:
#    uv add transformers torch langchain-huggingface accelerate
#    # For GPU support (optional but recommended):
#    uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
#
# 2. UPDATE CONFIG.PY OR ENV VARS:
#    Set USE_HUGGINGFACE=True and override HF_* settings as needed.
#
# 3. RUN AS USUAL:
#    call_llm() now routes to the HuggingFace backend automatically.
#    Use call_huggingface_llm() directly only if you explicitly need it.
#
# 4. RECOMMENDED MODELS FOR SQL GENERATION:
#    - "microsoft/DialoGPT-medium" (3.8GB, good for general text)
#    - "codellama/CodeLlama-7b-Instruct-hf" (13GB, excellent for code/SQL)
#    - "WizardLM/WizardCoder-Python-7B-V1.0" (13GB, Python/SQL focused)
#    - "bigcode/starcoder" (15GB, strong code generation)
#    - "microsoft/CodeBERT-base" (500MB, lightweight code model)
#
# 5. MEMORY REQUIREMENTS:
#    - Small models (< 1GB): CPU is fine, slower but works
#    - Medium models (1-5GB): 8GB+ GPU recommended
#    - Large models (> 5GB): 16GB+ GPU memory required
#
# 6. EXAMPLE COMPLETE SETUP:
#    ```bash
#    uv add transformers torch langchain-huggingface accelerate
#    export USE_HUGGINGFACE=true
#    export HF_MODEL_NAME="microsoft/DialoGPT-medium"
#    ```
