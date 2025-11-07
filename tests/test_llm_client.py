"""Tests for LLM client functionality and error handling."""

import os
import sys
import time
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.config import LLM_MAX_RETRIES, LLM_TIMEOUT, MODEL_NAME
from agent_pipeline.llms.client import call_huggingface_llm, call_llm, create_llm, get_llm


class TestLLMCreation:
    """Test LLM client creation and configuration."""

    @patch("agent_pipeline.llms.client.OllamaLLM")
    def test_create_llm(self, mock_ollama_class):
        """Test LLM creation with proper configuration."""
        mock_llm = Mock()
        mock_llm.invoke.return_value = "OK"
        mock_ollama_class.return_value = mock_llm

        llm = create_llm()

        assert llm is not None
        mock_ollama_class.assert_called_once()

        # Verify configuration parameters
        call_args = mock_ollama_class.call_args[1]  # kwargs
        assert call_args["model"] == MODEL_NAME
        assert call_args["timeout"] == LLM_TIMEOUT

    @patch("agent_pipeline.llms.client.OllamaLLM")
    def test_create_llm_connection_test(self, mock_ollama_class):
        """Test that LLM creation includes connection testing."""
        mock_llm = Mock()
        mock_llm.invoke.return_value = "OK"
        mock_ollama_class.return_value = mock_llm

        create_llm()

        # Should test connection with simple prompt
        mock_llm.invoke.assert_called_with("Hello, respond with just 'OK'")

    @patch("agent_pipeline.llms.client.OllamaLLM")
    def test_create_llm_connection_failure(self, mock_ollama_class):
        """Test LLM creation when connection test fails."""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("Connection failed")
        mock_ollama_class.return_value = mock_llm

        with pytest.raises(Exception, match="Connection failed"):
            create_llm()

    def test_get_llm_singleton(self):
        """Test that get_llm returns same instance (singleton pattern)."""
        with patch("agent_pipeline.llms.client.create_llm") as mock_create:
            mock_llm = Mock()
            mock_create.return_value = mock_llm

            llm1 = get_llm()
            llm2 = get_llm()

            assert llm1 is llm2
            mock_create.assert_called_once()  # Should only create once


class TestLLMCalls:
    """Test LLM call functionality and retry logic."""

    def test_call_llm_success(self, mock_llm):
        """Test successful LLM call."""
        mock_llm.invoke.return_value = Mock(content="Test response")

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            response = call_llm("System prompt", "User prompt")

        assert response == "Test response"
        assert mock_llm.invoke.call_count == 1

    def test_call_llm_fallback_format(self, mock_llm):
        """Test LLM call with fallback response format."""
        # Mock response without .content attribute
        mock_llm.invoke.return_value = "Direct response string"

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            response = call_llm("System prompt", "User prompt")

        assert response == "Direct response string"

    def test_call_llm_timeout_retry(self, mock_llm):
        """Test LLM call retry logic on timeout."""
        # First call times out, second succeeds
        mock_llm.invoke.side_effect = [
            Exception("Read timed out"),
            Mock(content="Success after retry"),
        ]

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            patch("time.sleep"),  # Skip actual sleep in tests
        ):
            response = call_llm("System prompt", "User prompt", max_retries=2)

        assert response == "Success after retry"
        assert mock_llm.invoke.call_count == 2

    def test_call_llm_timeout_exhausted(self, mock_llm):
        """Test LLM call when all retries are exhausted."""
        mock_llm.invoke.side_effect = Exception("Read timed out")

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            patch("time.sleep"),  # Skip actual sleep in tests
            pytest.raises(TimeoutError, match="failed to respond after .* attempts"),
        ):
            call_llm("System prompt", "User prompt", max_retries=2)

        assert mock_llm.invoke.call_count == 2

    def test_call_llm_non_timeout_error(self, mock_llm):
        """Test LLM call with non-timeout error (should not retry)."""
        mock_llm.invoke.side_effect = ValueError("Invalid input")

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            pytest.raises(ValueError, match="Invalid input"),
        ):
            call_llm("System prompt", "User prompt", max_retries=3)

        assert mock_llm.invoke.call_count == 1  # Should not retry

    def test_call_llm_custom_retries(self, mock_llm):
        """Test LLM call with custom retry count."""
        mock_llm.invoke.side_effect = Exception("timeout")

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            patch("time.sleep"),
            pytest.raises(TimeoutError),
        ):
            call_llm("System prompt", "User prompt", max_retries=5)

        assert mock_llm.invoke.call_count == 5

    def test_call_llm_default_retries(self, mock_llm):
        """Test LLM call uses default retry count from config."""
        mock_llm.invoke.side_effect = Exception("timeout")

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            patch("time.sleep"),
            pytest.raises(TimeoutError),
        ):
            call_llm("System prompt", "User prompt")  # No max_retries specified

        assert mock_llm.invoke.call_count == LLM_MAX_RETRIES


class TestLLMMessageFormatting:
    """Test LLM message formatting and prompt handling."""

    def test_call_llm_message_structure(self, mock_llm):
        """Test that LLM calls use proper message structure."""
        mock_llm.invoke.return_value = Mock(content="Response")

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            call_llm("System message", "User message")

        # Check that invoke was called with proper message structure
        args = mock_llm.invoke.call_args[0]
        messages = args[0]

        assert len(messages) == 2
        assert messages[0].content == "System message"
        assert messages[1].content == "User message"

    def test_call_llm_content_stripping(self, mock_llm):
        """Test that response content is properly stripped."""
        mock_llm.invoke.return_value = Mock(content="  Response with whitespace  ")

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            response = call_llm("System", "User")

        assert response == "Response with whitespace"


class TestLLMErrorScenarios:
    """Test various error scenarios and edge cases."""

    def test_call_llm_empty_response(self, mock_llm):
        """Test LLM call with empty response."""
        mock_llm.invoke.return_value = Mock(content="")

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            response = call_llm("System", "User")

        assert response == ""

    def test_call_llm_none_response(self, mock_llm):
        """Test LLM call when response content is None."""
        mock_response = Mock()
        mock_response.content = None
        mock_llm.invoke.return_value = mock_response

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            response = call_llm("System", "User")

        assert response == ""  # str(None or "").strip() == ""

    @patch("agent_pipeline.llms.client.OllamaLLM")
    def test_import_fallback(self, mock_ollama_class):
        """Test import fallback from new to legacy langchain."""
        # This test would need more complex mocking to test the import fallback
        # For now, just verify that the function doesn't crash
        mock_llm = Mock()
        mock_llm.invoke.return_value = "OK"
        mock_ollama_class.return_value = mock_llm

        llm = create_llm()
        assert llm is not None


class TestLLMPerformance:
    """Test LLM performance and timing."""

    def test_call_llm_timing(self, mock_llm):
        """Test that LLM calls complete within reasonable time."""
        mock_llm.invoke.return_value = Mock(content="Response")

        with patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm):
            start_time = time.time()
            call_llm("System", "User")
            end_time = time.time()

        # Should complete quickly in test (< 1 second)
        assert end_time - start_time < 1.0

    def test_call_llm_retry_timing(self, mock_llm):
        """Test timing behavior during retries."""
        # First call fails, second succeeds
        mock_llm.invoke.side_effect = [Exception("timeout"), Mock(content="Success")]

        with (
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
            patch("time.sleep") as mock_sleep,
        ):
            call_llm("System", "User", max_retries=2)

        # Should sleep between retries
        mock_sleep.assert_called_once_with(5)


class TestHuggingFaceRouting:
    """Ensure HuggingFace-specific paths behave as expected."""

    def test_get_llm_uses_huggingface_backend(self):
        """get_llm should instantiate HuggingFace pipeline when enabled."""
        mock_llm = Mock()
        with (
            patch("agent_pipeline.llms.client.USE_HUGGINGFACE", True),
            patch("agent_pipeline.llms.client.HF_MODEL_NAME", "hf/test-model"),
            patch(
                "agent_pipeline.llms.client.create_huggingface_llm",
                return_value=mock_llm,
            ) as mock_create_hf,
            patch("agent_pipeline.llms.client.create_llm") as mock_create_ollama,
        ):
            llm = get_llm()

        assert llm is mock_llm
        mock_create_hf.assert_called_once_with("hf/test-model")
        mock_create_ollama.assert_not_called()

    def test_call_llm_routes_to_huggingface(self, mock_llm):
        """call_llm should switch to HF prompt formatting when enabled."""
        mock_llm.invoke.return_value = "HF response"

        with (
            patch("agent_pipeline.llms.client.USE_HUGGINGFACE", True),
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
        ):
            response = call_llm("System prompt", "User prompt")

        assert response == "HF response"
        prompt_passed = mock_llm.invoke.call_args[0][0]
        assert isinstance(prompt_passed, str)
        assert "System: System prompt" in prompt_passed
        assert "User: User prompt" in prompt_passed

    def test_call_huggingface_llm_requires_flag(self):
        """Direct HF calls should fail when the flag is disabled."""
        with (
            patch("agent_pipeline.llms.client.USE_HUGGINGFACE", False),
            pytest.raises(RuntimeError, match="disabled"),
        ):
            call_huggingface_llm("System", "User")

    def test_call_huggingface_llm_success(self, mock_llm):
        """Direct HF calls should work when backend is enabled."""
        mock_llm.invoke.return_value = "HF direct response"

        with (
            patch("agent_pipeline.llms.client.USE_HUGGINGFACE", True),
            patch("agent_pipeline.llms.client.get_llm", return_value=mock_llm),
        ):
            response = call_huggingface_llm("System", "User")

        assert response == "HF direct response"
