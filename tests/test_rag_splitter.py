"""Test RAG text splitting functionality."""

from unittest.mock import Mock, patch

from langchain_core.documents import Document

from agent_pipeline.rag.splitter import create_splitter, split_documents


class TestTextSplitter:
    """Test cases for text splitting functionality."""

    @patch("agent_pipeline.rag.splitter.RecursiveCharacterTextSplitter")
    def test_create_splitter(self, mock_splitter_class):
        """Test creating a text splitter with correct configuration."""
        mock_splitter = Mock()
        mock_splitter_class.return_value = mock_splitter

        result = create_splitter()

        assert result == mock_splitter
        mock_splitter_class.assert_called_once_with(
            chunk_size=800,  # RAG_CHUNK_SIZE
            chunk_overlap=100,  # RAG_CHUNK_OVERLAP
            separators=["\n\n", "\n", " ", ""],  # RAG_SEPARATORS
        )

    def test_split_documents_single_document(self):
        """Test splitting a single document."""
        # Create test document
        test_doc = Document(
            page_content="This is a test document with some content that might need splitting.",
            metadata={"source": "test"},
        )

        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter

            # Mock the split result
            chunk1 = Document(page_content="This is a test document", metadata={"source": "test"})
            chunk2 = Document(
                page_content="with some content that might need splitting.",
                metadata={"source": "test"},
            )
            mock_splitter.split_documents.return_value = [chunk1, chunk2]

            result = split_documents([test_doc])

            assert len(result) == 2
            assert result[0].page_content == "This is a test document"
            assert result[1].page_content == "with some content that might need splitting."
            mock_create.assert_called_once()
            mock_splitter.split_documents.assert_called_once_with([test_doc])

    def test_split_documents_multiple_documents(self):
        """Test splitting multiple documents."""
        # Create test documents
        test_docs = [
            Document(page_content="First document content", metadata={"source": "doc1"}),
            Document(page_content="Second document content", metadata={"source": "doc2"}),
            Document(page_content="Third document content", metadata={"source": "doc3"}),
        ]

        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter

            # Mock the split result - each doc becomes 2 chunks
            chunks = []
            for i, doc in enumerate(test_docs):
                chunks.extend(
                    [
                        Document(page_content=f"Chunk 1 from doc {i + 1}", metadata=doc.metadata),
                        Document(page_content=f"Chunk 2 from doc {i + 1}", metadata=doc.metadata),
                    ]
                )
            mock_splitter.split_documents.return_value = chunks

            result = split_documents(test_docs)

            assert len(result) == 6  # 3 docs * 2 chunks each
            assert "Chunk 1 from doc 1" in result[0].page_content
            assert "Chunk 2 from doc 1" in result[1].page_content
            assert "Chunk 1 from doc 2" in result[2].page_content
            mock_splitter.split_documents.assert_called_once_with(test_docs)

    def test_split_documents_empty_input(self):
        """Test splitting with empty document list."""
        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter
            mock_splitter.split_documents.return_value = []

            result = split_documents([])

            assert len(result) == 0
            assert result == []
            mock_splitter.split_documents.assert_called_once_with([])

    def test_split_documents_no_splitting_needed(self):
        """Test splitting documents that don't need to be split."""
        test_doc = Document(page_content="Short content", metadata={"source": "test"})

        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter

            # Mock that splitter returns the same document (no splitting needed)
            mock_splitter.split_documents.return_value = [test_doc]

            result = split_documents([test_doc])

            assert len(result) == 1
            assert result[0] == test_doc
            mock_splitter.split_documents.assert_called_once_with([test_doc])

    def test_split_documents_large_document(self):
        """Test splitting a large document into many chunks."""
        large_content = "This is a very large document. " * 100  # Repeat to make it large
        test_doc = Document(page_content=large_content, metadata={"source": "large_doc"})

        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter

            # Mock splitting into 5 chunks
            chunks = []
            for i in range(5):
                chunk_content = f"Chunk {i + 1} content from large document"
                chunks.append(
                    Document(page_content=chunk_content, metadata={"source": "large_doc"})
                )
            mock_splitter.split_documents.return_value = chunks

            result = split_documents([test_doc])

            assert len(result) == 5
            for i, chunk in enumerate(result):
                assert f"Chunk {i + 1} content" in chunk.page_content
                assert chunk.metadata["source"] == "large_doc"

    def test_split_documents_preserves_metadata(self):
        """Test that splitting preserves document metadata."""
        test_doc = Document(
            page_content="Document content to be split",
            metadata={"source": "test_file.txt", "author": "test_author", "date": "2024-01-01"},
        )

        with patch("agent_pipeline.rag.splitter.create_splitter") as mock_create:
            mock_splitter = Mock()
            mock_create.return_value = mock_splitter

            # Mock splitting into 2 chunks with preserved metadata
            chunk1 = Document(
                page_content="Document content",
                metadata={"source": "test_file.txt", "author": "test_author", "date": "2024-01-01"},
            )
            chunk2 = Document(
                page_content="to be split",
                metadata={"source": "test_file.txt", "author": "test_author", "date": "2024-01-01"},
            )
            mock_splitter.split_documents.return_value = [chunk1, chunk2]

            result = split_documents([test_doc])

            assert len(result) == 2
            for chunk in result:
                assert chunk.metadata["source"] == "test_file.txt"
                assert chunk.metadata["author"] == "test_author"
                assert chunk.metadata["date"] == "2024-01-01"
