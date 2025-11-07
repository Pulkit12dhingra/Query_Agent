"""Test CLI functionality."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_pipeline.cli.main import main


class TestCLIMain:
    """Test cases for the CLI main function."""

    def test_main_no_arguments(self, capsys):
        """Test CLI with no arguments shows usage."""
        with patch.object(sys, "argv", ["main.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            captured = capsys.readouterr()
            assert "Usage:" in captured.out
            assert exc_info.value.code == 1

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_with_query_argument(self, mock_get_final, mock_run_pipeline, mock_init):
        """Test CLI with a query argument."""
        test_query = "Show all users"

        # Mock pipeline functions
        mock_init.return_value = True
        mock_run_pipeline.return_value = ["mock_results"]
        mock_final_result = MagicMock()
        mock_final_result.sql = "SELECT * FROM users"
        mock_final_result.result_df.head.return_value = "mock_df"
        mock_final_result.result_df.__len__ = lambda self: 5
        mock_get_final.return_value = mock_final_result

        with patch.object(sys, "argv", ["main.py", test_query]):
            main()

            mock_init.assert_called_once()
            mock_run_pipeline.assert_called_once_with(test_query)
            mock_get_final.assert_called_once_with(["mock_results"])

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_with_multi_word_query(self, mock_get_final, mock_run_pipeline, mock_init):
        """Test CLI with multi-word query."""
        mock_init.return_value = True
        mock_run_pipeline.return_value = ["mock_results"]
        mock_get_final.return_value = None

        with patch.object(sys, "argv", ["main.py", "Show", "all", "users", "with", "salary"]):
            main()

            # Should join all arguments after script name
            mock_run_pipeline.assert_called_once_with("Show all users with salary")

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    def test_main_pipeline_initialization_failure(self, mock_init):
        """Test CLI when pipeline initialization fails."""
        test_query = "Test query"
        mock_init.return_value = False

        with patch.object(sys, "argv", ["main.py", test_query]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            mock_init.assert_called_once()

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    def test_main_pipeline_exception(self, mock_run_pipeline, mock_init):
        """Test CLI when pipeline raises an exception."""
        test_query = "Test query"
        mock_init.return_value = True
        mock_run_pipeline.side_effect = Exception("Connection failed")

        with patch.object(sys, "argv", ["main.py", test_query]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            mock_init.assert_called_once()
            mock_run_pipeline.assert_called_once_with(test_query)

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_pipeline_success_with_results(
        self, mock_get_final, mock_run_pipeline, mock_init, capsys
    ):
        """Test CLI with successful pipeline that returns results."""
        test_query = "Show users"

        # Mock pipeline functions
        mock_init.return_value = True
        mock_run_pipeline.return_value = ["mock_results"]
        mock_final_result = MagicMock()
        mock_final_result.sql = "SELECT * FROM users"
        mock_final_result.result_df.head.return_value = "Users data"
        mock_final_result.result_df.__len__ = lambda self: 10
        mock_get_final.return_value = mock_final_result

        with patch.object(sys, "argv", ["main.py", test_query]):
            main()

            captured = capsys.readouterr()
            assert test_query in captured.out
            assert "FINAL RESULT:" in captured.out
            assert "SELECT * FROM users" in captured.out

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_no_results(self, mock_get_final, mock_run_pipeline, mock_init, capsys):
        """Test CLI when no results are generated."""
        test_query = "Empty query"

        mock_init.return_value = True
        mock_run_pipeline.return_value = []
        mock_get_final.return_value = None

        with patch.object(sys, "argv", ["main.py", test_query]):
            main()

            captured = capsys.readouterr()
            assert "No successful results generated." in captured.out

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_whitespace_only_query(self, mock_get_final, mock_run_pipeline, mock_init):
        """Test CLI with whitespace-only query - should still process."""
        mock_init.return_value = True
        mock_run_pipeline.return_value = []
        mock_get_final.return_value = None

        with patch.object(sys, "argv", ["main.py", "   ", "\t", "\n"]):
            main()

        # Should join whitespace arguments
        mock_run_pipeline.assert_called_once_with("    \t \n")

    @patch("agent_pipeline.cli.main.initialize_pipeline")
    @patch("agent_pipeline.cli.main.run_query_pipeline")
    @patch("agent_pipeline.cli.main.get_final_result")
    def test_main_empty_string_query(self, mock_get_final, mock_run_pipeline, mock_init):
        """Test CLI with empty string query."""
        mock_init.return_value = True
        mock_run_pipeline.return_value = []
        mock_get_final.return_value = None

        with patch.object(sys, "argv", ["main.py", ""]):
            main()

        # Should still call pipeline with empty string
        mock_run_pipeline.assert_called_once_with("")
