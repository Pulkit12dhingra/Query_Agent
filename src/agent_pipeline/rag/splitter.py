# RecursiveCharacterTextSplitter config

"""Text splitting utilities for RAG pipeline."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE, RAG_SEPARATORS


def create_splitter() -> RecursiveCharacterTextSplitter:
    """Create and configure the text splitter."""
    return RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        separators=RAG_SEPARATORS,
    )


def split_documents(docs: list[Document]) -> list[Document]:
    """Split documents into chunks for retrieval."""
    splitter = create_splitter()
    chunks = splitter.split_documents(docs)

    print(f"Split into {len(chunks)} chunks")
    return chunks
