# OllamaLLM wrapper, call_llm() with retry/backoff

"""LLM client wrapper with retry logic and timeout handling.

This module provides LLM integration with Ollama as the primary method,
and HuggingFace models as an alternative option.
"""

import time
from typing import Union

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

# Optional HuggingFace imports (commented out by default)
# Uncomment these imports if you want to use HuggingFace models
# from langchain_huggingface import HuggingFacePipeline
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# import torch

# Global LLM instance
_llm_instance: Union[OllamaLLM, None] = None


def get_llm() -> Union[OllamaLLM, None]:
    """Get the global LLM instance, creating it if necessary."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_llm()
    return _llm_instance


def create_llm() -> OllamaLLM:
    """Create and configure the Ollama LLM instance.

    This is the primary method for LLM creation using Ollama.
    For HuggingFace models, see create_huggingface_llm() below.
    """
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


# =============================================================================
# HUGGINGFACE MODEL SUPPORT (ALTERNATIVE TO OLLAMA)
# =============================================================================
#
# The following functions provide an alternative to Ollama using HuggingFace models.
# To use HuggingFace instead of Ollama:
#
# 1. Uncomment the HuggingFace imports at the top of this file
# 2. Install required packages:
#    uv add transformers torch langchain-huggingface accelerate
# 3. Replace the call to create_llm() with create_huggingface_llm() in get_llm()
# 4. Optionally set HF_MODEL_NAME in config.py
#
# Popular models for SQL generation:
# - "microsoft/DialoGPT-medium" (lighter, faster)
# - "microsoft/CodeBERT-base" (code-focused)
# - "codellama/CodeLlama-7b-Instruct-hf" (instruction-tuned)
# - "WizardLM/WizardCoder-Python-7B-V1.0" (Python/SQL focused)
# - "bigcode/starcoder" (code generation)


def create_huggingface_llm(model_name: str = "microsoft/DialoGPT-medium"):
    """Create and configure a HuggingFace LLM instance.

    IMPORTANT: This function is commented out by default. To use:
    1. Uncomment the HuggingFace imports at the top of this file
    2. Install dependencies: uv add transformers torch langchain-huggingface
    3. Uncomment this function code

    Args:
        model_name: HuggingFace model identifier

    Returns:
        HuggingFacePipeline: Configured LLM instance

    Example usage:
        # Replace create_llm() call with:
        _llm_instance = create_huggingface_llm("microsoft/DialoGPT-medium")
    """
    # UNCOMMENT THE CODE BELOW TO ENABLE HUGGINGFACE SUPPORT
    #
    # print(f"Loading HuggingFace model: {model_name}")
    # print("This may take a few minutes on first run...")
    #
    # # Check if CUDA is available
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # print(f"Using device: {device}")
    #
    # # Load tokenizer and model
    # try:
    #     tokenizer = AutoTokenizer.from_pretrained(model_name)
    #     model = AutoModelForCausalLM.from_pretrained(
    #         model_name,
    #         torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    #         device_map="auto" if device == "cuda" else None,
    #         trust_remote_code=True
    #     )
    #
    #     # Create text generation pipeline
    #     text_pipeline = pipeline(
    #         "text-generation",
    #         model=model,
    #         tokenizer=tokenizer,
    #         max_new_tokens=OLLAMA_NUM_PREDICT,  # Use same max tokens as Ollama
    #         temperature=OLLAMA_TEMPERATURE,
    #         do_sample=True,
    #         top_p=OLLAMA_TOP_P,
    #         repetition_penalty=OLLAMA_REPEAT_PENALTY,
    #         device=device,
    #         return_full_text=False,  # Only return generated text
    #     )
    #
    #     # Wrap in LangChain HuggingFacePipeline
    #     llm = HuggingFacePipeline(pipeline=text_pipeline)
    #
    #     # Test the model
    #     print("Testing HuggingFace model connection...")
    #     test_response = llm.invoke("Hello, respond with just 'OK'")
    #     print("HuggingFace model loaded successfully!")
    #     print(f"Test response: {test_response[:50]}...")
    #
    #     return llm
    #
    # except Exception as e:
    #     print(f"Failed to load HuggingFace model: {e}")
    #     print("Make sure you have sufficient GPU memory or try a smaller model")
    #     raise

    # Default fallback - this should be uncommented when enabling HF support
    raise NotImplementedError(
        "HuggingFace support is disabled. See comments in this function to enable it."
    )


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

    # Format prompts for HuggingFace models
    # Many HF models expect specific prompt formats
    combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"  # noqa: F841

    # UNCOMMENT THE CODE BELOW TO ENABLE HUGGINGFACE SUPPORT
    #
    # llm = get_llm()  # This should return HuggingFace model if configured
    #
    # for attempt in range(max_retries):
    #     try:
    #         print(f"[HF-LLM] Calling HuggingFace model (attempt {attempt + 1}/{max_retries})...")
    #
    #         # HuggingFace models typically expect string input
    #         response = llm.invoke(combined_prompt)
    #
    #         if isinstance(response, str):
    #             result = response.strip()
    #         elif hasattr(response, "content"):
    #             result = str(response.content or "").strip()
    #         else:
    #             result = str(response).strip()
    #
    #         print("[HF-LLM] Response received successfully")
    #         return result
    #
    #     except Exception as e:
    #         error_msg = str(e)
    #         print(f"[HF-LLM] Error on attempt {attempt + 1}/{max_retries}: {error_msg}")
    #
    #         if attempt < max_retries - 1:
    #             print("[HF-LLM] Retrying in 3 seconds...")
    #             time.sleep(3)
    #             continue
    #         else:
    #             print("[HF-LLM] All retry attempts failed")
    #             raise
    #
    # raise Exception("Unexpected error in call_huggingface_llm")

    # Default fallback - this should be uncommented when enabling HF support
    raise NotImplementedError(
        "HuggingFace support is disabled. See comments in this function to enable it."
    )


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
# 2. UNCOMMENT IMPORTS:
#    Uncomment the HuggingFace imports at the top of this file
#
# 3. UPDATE CONFIG.PY:
#    Add these settings to config.py:
#    ```python
#    # HuggingFace Configuration (alternative to Ollama)
#    HF_MODEL_NAME = "microsoft/DialoGPT-medium"  # or any compatible model
#    USE_HUGGINGFACE = False  # Set to True to use HF instead of Ollama
#    ```
#
# 4. MODIFY get_llm() FUNCTION:
#    Replace the create_llm() call with:
#    ```python
#    if USE_HUGGINGFACE:
#        _llm_instance = create_huggingface_llm(HF_MODEL_NAME)
#    else:
#        _llm_instance = create_llm()  # Default Ollama
#    ```
#
# 5. UPDATE CALL SITES (OPTIONAL):
#    You can use call_huggingface_llm() directly, or modify call_llm() to
#    automatically route to the correct implementation based on USE_HUGGINGFACE
#
# 6. RECOMMENDED MODELS FOR SQL GENERATION:
#    - "microsoft/DialoGPT-medium" (3.8GB, good for general text)
#    - "codellama/CodeLlama-7b-Instruct-hf" (13GB, excellent for code/SQL)
#    - "WizardLM/WizardCoder-Python-7B-V1.0" (13GB, Python/SQL focused)
#    - "bigcode/starcoder" (15GB, strong code generation)
#    - "microsoft/CodeBERT-base" (500MB, lightweight code model)
#
# 7. MEMORY REQUIREMENTS:
#    - Small models (< 1GB): CPU is fine, slower but works
#    - Medium models (1-5GB): 8GB+ GPU recommended
#    - Large models (> 5GB): 16GB+ GPU memory required
#
# 8. EXAMPLE COMPLETE SETUP:
#    ```python
#    # In config.py:
#    USE_HUGGINGFACE = True
#    HF_MODEL_NAME = "microsoft/DialoGPT-medium"
#
#    # In this file, uncomment HF imports and modify get_llm():
#    def get_llm():
#        global _llm_instance
#        if _llm_instance is None:
#            if USE_HUGGINGFACE:
#                _llm_instance = create_huggingface_llm(HF_MODEL_NAME)
#            else:
#                _llm_instance = create_llm()
#        return _llm_instance
#    ```
