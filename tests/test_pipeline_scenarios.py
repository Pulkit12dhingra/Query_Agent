"""Tests for end-to-end pipeline scenarios."""

import os
import sys
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.agent.run_steps import StepResult
from agent_pipeline.orchestration.pipeline import (
    get_final_result,
    initialize_pipeline,
    run_query_pipeline,
)


class TestPipelineInitialization:
    """Test pipeline initialization and component setup."""

    @patch("agent_pipeline.orchestration.pipeline.check_ollama_health")
    @patch("agent_pipeline.orchestration.pipeline.test_db_connection")
    @patch("agent_pipeline.orchestration.pipeline.get_vectorstore")
    @patch("agent_pipeline.orchestration.pipeline.get_retriever")
    def test_initialize_pipeline_success(
        self, mock_retriever, mock_vectorstore, mock_db_test, mock_ollama_health
    ):
        """Test successful pipeline initialization."""
        # Mock all components as working
        mock_ollama_health.return_value = True
        mock_db_test.return_value = ["users", "departments", "employee_records"]
        mock_vectorstore.return_value = Mock()
        mock_retriever.return_value = Mock()

        result = initialize_pipeline()

        assert result is True
        mock_ollama_health.assert_called_once()
        mock_db_test.assert_called_once()
        mock_vectorstore.assert_called_once()
        mock_retriever.assert_called_once()

    @patch("agent_pipeline.orchestration.pipeline.check_ollama_health")
    def test_initialize_pipeline_ollama_failure(self, mock_ollama_health):
        """Test pipeline initialization when Ollama health check fails."""
        mock_ollama_health.return_value = False

        result = initialize_pipeline()

        assert result is False
        mock_ollama_health.assert_called_once()

    @patch("agent_pipeline.orchestration.pipeline.check_ollama_health")
    @patch("agent_pipeline.orchestration.pipeline.test_db_connection")
    def test_initialize_pipeline_db_failure(self, mock_db_test, mock_ollama_health):
        """Test pipeline initialization when database connection fails."""
        mock_ollama_health.return_value = True
        mock_db_test.side_effect = Exception("Database connection failed")

        result = initialize_pipeline()

        assert result is False


class TestBasicPipelineScenarios:
    """Test basic pipeline execution scenarios."""

    def test_simple_query_success(self, temp_db, sample_step_result):
        """Test simple query execution with successful result."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            # Mock successful agent execution
            mock_run_agent.return_value = [sample_step_result]

            results = run_query_pipeline("Show all users", engine=temp_db, auto_initialize=False)

            assert len(results) == 1
            assert results[0].error is None
            assert results[0].result_df is not None

    def test_query_with_initialization_failure(self, temp_db):
        """Test query execution when initialization fails."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=False),
            pytest.raises(RuntimeError, match="Pipeline initialization failed"),
        ):
            run_query_pipeline("Show all users", engine=temp_db)

    def test_query_with_agent_failure(self, temp_db):
        """Test query execution when agent fails."""
        failed_result = StepResult(
            step_id=1,
            title="Failed Query",
            description="A query that failed",
            sql="INVALID SQL",
            error="SQL execution failed",
        )

        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = [failed_result]

            results = run_query_pipeline("Invalid query", engine=temp_db, auto_initialize=False)

            assert len(results) == 1
            assert results[0].error is not None

    def test_multi_step_query_success(self, temp_db):
        """Test multi-step query execution."""
        step1 = StepResult(
            step_id=1,
            title="Step 1",
            description="First step",
            sql="SELECT * FROM users",
            result_df=pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]}),
            error=None,
        )

        step2 = StepResult(
            step_id=2,
            title="Step 2",
            description="Second step",
            sql="SELECT name FROM users WHERE id = 1",
            result_df=pd.DataFrame({"name": ["Alice"]}),
            error=None,
        )

        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = [step1, step2]

            results = run_query_pipeline("Multi-step query", engine=temp_db, auto_initialize=False)

            assert len(results) == 2
            assert all(r.error is None for r in results)
            assert all(r.result_df is not None for r in results)


class TestComplexPipelineScenarios:
    """Test complex and edge case pipeline scenarios."""

    def test_query_with_mixed_success_failure(self, temp_db):
        """Test pipeline with some successful and some failed steps."""
        step1 = StepResult(
            step_id=1,
            title="Success Step",
            description="Successful step",
            sql="SELECT * FROM users",
            result_df=pd.DataFrame({"name": ["Alice"]}),
            error=None,
        )

        step2 = StepResult(
            step_id=2,
            title="Failed Step",
            description="Failed step",
            sql="INVALID SQL",
            error="SQL syntax error",
        )

        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = [step1, step2]

            results = run_query_pipeline(
                "Mixed success/failure query", engine=temp_db, auto_initialize=False
            )

            assert len(results) == 2
            assert results[0].error is None
            assert results[1].error is not None

    def test_empty_result_handling(self, temp_db):
        """Test pipeline handling when query returns no results."""
        empty_result = StepResult(
            step_id=1,
            title="Empty Result",
            description="Query with no results",
            sql="SELECT * FROM users WHERE id = 999",
            result_df=pd.DataFrame(),  # Empty DataFrame
            error=None,
        )

        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = [empty_result]

            results = run_query_pipeline(
                "Query with no results", engine=temp_db, auto_initialize=False
            )

            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].result_df) == 0

    def test_large_result_set_handling(self, temp_db):
        """Test pipeline handling of large result sets."""
        # Create large DataFrame (simulating many rows)
        large_df = pd.DataFrame(
            {"id": range(1000), "name": [f"User_{i}" for i in range(1000)], "value": range(1000)}
        )

        large_result = StepResult(
            step_id=1,
            title="Large Result",
            description="Query with many results",
            sql="SELECT * FROM large_table",
            result_df=large_df,
            error=None,
        )

        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = [large_result]

            results = run_query_pipeline(
                "Query with large results", engine=temp_db, auto_initialize=False
            )

            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].result_df) == 1000


class TestPipelineResultHandling:
    """Test pipeline result processing and extraction."""

    def test_get_final_result_success(self, sample_step_result):
        """Test extracting final result from successful pipeline."""
        results = [sample_step_result]
        final_result = get_final_result(results)

        assert final_result is not None
        assert final_result.error is None
        assert final_result.result_df is not None

    def test_get_final_result_no_success(self):
        """Test extracting final result when no steps succeeded."""
        failed_result = StepResult(
            step_id=1, title="Failed Step", description="Failed step", error="Some error"
        )

        results = [failed_result]
        final_result = get_final_result(results)

        assert final_result is None

    def test_get_final_result_multiple_success(self, sample_step_result):
        """Test extracting final result from multiple successful steps."""
        step1 = StepResult(
            step_id=1,
            title="Step 1",
            description="First step",
            sql="SELECT * FROM table1",
            result_df=pd.DataFrame({"col1": [1, 2]}),
            error=None,
        )

        step2 = sample_step_result  # This will be the final result

        results = [step1, step2]
        final_result = get_final_result(results)

        assert final_result is step2  # Should return the last successful step

    def test_get_final_result_empty_list(self):
        """Test extracting final result from empty results list."""
        final_result = get_final_result([])
        assert final_result is None


class TestPipelineParameterHandling:
    """Test pipeline parameter handling and configuration."""

    def test_custom_parameters(self, temp_db):
        """Test pipeline with custom parameters."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = []

            run_query_pipeline(
                "Test query",
                engine=temp_db,
                max_steps=6,
                per_step_retries=3,
                auto_initialize=False,
            )

            # Verify parameters were passed through
            mock_run_agent.assert_called_once()
            call_args = mock_run_agent.call_args[1]
            assert call_args["max_steps"] == 6
            assert call_args["per_step_retries"] == 3

    def test_default_parameters(self, temp_db):
        """Test pipeline with default parameters."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.return_value = []

            run_query_pipeline("Test query", engine=temp_db, auto_initialize=False)

            # Verify default parameters were used (None passed through)
            mock_run_agent.assert_called_once()
            call_args = mock_run_agent.call_args[1]
            assert call_args.get("max_steps") is None
            assert call_args.get("per_step_retries") is None


class TestPipelineErrorHandling:
    """Test pipeline error handling and recovery."""

    def test_agent_exception_handling(self, temp_db):
        """Test pipeline handling when agent raises exception."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
        ):
            mock_run_agent.side_effect = Exception("Agent execution failed")

            with pytest.raises(Exception, match="Agent execution failed"):
                run_query_pipeline("Test query", engine=temp_db, auto_initialize=False)

    def test_pipeline_logging(self, temp_db, sample_step_result):
        """Test that pipeline operations are properly logged."""
        with (
            patch("agent_pipeline.orchestration.pipeline.initialize_pipeline", return_value=True),
            patch("agent_pipeline.orchestration.pipeline.run_agent") as mock_run_agent,
            patch("agent_pipeline.orchestration.pipeline.log_and_print") as mock_log,
        ):
            mock_run_agent.return_value = [sample_step_result]

            run_query_pipeline("Test query", engine=temp_db, auto_initialize=False)

            # Should have logged start and completion
            assert mock_log.call_count >= 2
            log_messages = [call[0][0] for call in mock_log.call_args_list]
            assert any("Starting query pipeline" in msg for msg in log_messages)
            assert any("Pipeline completed" in msg for msg in log_messages)
