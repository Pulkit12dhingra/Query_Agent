"""Test RAG document loading functionality."""

import os
import tempfile
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from agent_pipeline.rag.loader import load_documents


class TestDocumentLoader:
    """Test cases for document loading functionality."""

    def test_load_documents_with_default_path(self):
        """Test loading documents with default path."""
        with (
            patch("agent_pipeline.rag.loader.os.path.exists") as mock_exists,
            patch("agent_pipeline.rag.loader.TextLoader") as mock_loader,
        ):
            # Mock that default path exists
            mock_exists.return_value = True

            # Mock loader and documents
            mock_doc = Document(page_content="Test content", metadata={"source": "test"})
            mock_loader_instance = Mock()
            mock_loader_instance.load.return_value = [mock_doc]
            mock_loader.return_value = mock_loader_instance

            # Test
            result = load_documents()

            # Assertions
            assert len(result) == 1
            assert result[0].page_content == "Test content"
            mock_loader.assert_called_once()
            mock_loader_instance.load.assert_called_once()

    def test_load_documents_with_custom_path(self):
        """Test loading documents with custom path."""
        custom_path = "/custom/path/doc.txt"

        with (
            patch("agent_pipeline.rag.loader.os.path.exists") as mock_exists,
            patch("agent_pipeline.rag.loader.TextLoader") as mock_loader,
        ):
            # Mock that custom path exists
            mock_exists.return_value = True

            # Mock loader and documents
            mock_doc = Document(page_content="Custom content", metadata={"source": "custom"})
            mock_loader_instance = Mock()
            mock_loader_instance.load.return_value = [mock_doc]
            mock_loader.return_value = mock_loader_instance

            # Test
            result = load_documents(custom_path)

            # Assertions
            assert len(result) == 1
            assert result[0].page_content == "Custom content"
            mock_exists.assert_called_once_with(custom_path)
            mock_loader.assert_called_once_with(custom_path, encoding="utf-8")

    def test_load_documents_fallback_to_existing(self):
        """Test fallback to existing documentation when default doesn't exist."""
        with (
            patch("agent_pipeline.rag.loader.os.path.exists") as mock_exists,
            patch("agent_pipeline.rag.loader.TextLoader") as mock_loader,
        ):
            # Mock that default path doesn't exist
            mock_exists.return_value = False

            # Mock loader and documents
            mock_doc = Document(page_content="Fallback content", metadata={"source": "fallback"})
            mock_loader_instance = Mock()
            mock_loader_instance.load.return_value = [mock_doc]
            mock_loader.return_value = mock_loader_instance

            # Test
            result = load_documents()

            # Assertions
            assert len(result) == 1
            assert result[0].page_content == "Fallback content"
            mock_loader.assert_called_once_with("../data/data_documentation.txt", encoding="utf-8")

    def test_load_documents_multiple_documents(self):
        """Test loading multiple documents."""
        with (
            patch("agent_pipeline.rag.loader.os.path.exists") as mock_exists,
            patch("agent_pipeline.rag.loader.TextLoader") as mock_loader,
        ):
            # Mock that path exists
            mock_exists.return_value = True

            # Mock loader with multiple documents
            mock_docs = [
                Document(page_content="Doc 1", metadata={"source": "doc1"}),
                Document(page_content="Doc 2", metadata={"source": "doc2"}),
                Document(page_content="Doc 3", metadata={"source": "doc3"}),
            ]
            mock_loader_instance = Mock()
            mock_loader_instance.load.return_value = mock_docs
            mock_loader.return_value = mock_loader_instance

            # Test
            result = load_documents()

            # Assertions
            assert len(result) == 3
            assert result[0].page_content == "Doc 1"
            assert result[1].page_content == "Doc 2"
            assert result[2].page_content == "Doc 3"

    def test_load_documents_empty_result(self):
        """Test loading documents when no documents are found."""
        with (
            patch("agent_pipeline.rag.loader.os.path.exists") as mock_exists,
            patch("agent_pipeline.rag.loader.TextLoader") as mock_loader,
        ):
            # Mock that path exists
            mock_exists.return_value = True

            # Mock loader with empty result
            mock_loader_instance = Mock()
            mock_loader_instance.load.return_value = []
            mock_loader.return_value = mock_loader_instance

            # Test
            result = load_documents()

            # Assertions
            assert len(result) == 0
            assert result == []

    def test_load_documents_with_real_temp_file(self):
        """Test loading documents with a real temporary file."""
        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write("This is test content for RAG loading.")
            temp_file_path = temp_file.name

        try:
            # Test loading the real file
            with patch("agent_pipeline.rag.loader.TextLoader") as mock_loader:
                mock_doc = Document(
                    page_content="This is test content for RAG loading.",
                    metadata={"source": temp_file_path},
                )
                mock_loader_instance = Mock()
                mock_loader_instance.load.return_value = [mock_doc]
                mock_loader.return_value = mock_loader_instance

                result = load_documents(temp_file_path)

                # Assertions
                assert len(result) == 1
                assert "test content" in result[0].page_content
                mock_loader.assert_called_once_with(temp_file_path, encoding="utf-8")
        finally:
            # Clean up
            os.unlink(temp_file_path)
