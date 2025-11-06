# load_documents() from disk/dirs

"""Document loading utilities for RAG pipeline."""

import os

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from ..config import SCHEMA_DOC_PATH


def load_documents(doc_path: str = None) -> list[Document]:
    """Load documents from the specified path or default schema documentation."""
    if doc_path is None:
        doc_path = SCHEMA_DOC_PATH

    # Check if our documentation exists, if not use the existing one
    if not os.path.exists(doc_path):
        fallback_path = "../data/data_documentation.txt"
        print(f"Using existing documentation: {fallback_path}")
        doc_path = fallback_path
    else:
        print(f"Using database documentation: {doc_path}")

    # Load text doc
    loader = TextLoader(doc_path, encoding="utf-8")
    docs = loader.load()

    print(f"Loaded {len(docs)} documents")
    return docs
