# HF embeddings factory

"""Embeddings utilities for RAG pipeline."""

from langchain_huggingface import HuggingFaceEmbeddings

from ..config import EMBEDDINGS_MODEL


def create_embeddings() -> HuggingFaceEmbeddings:
    """Create and configure the HuggingFace embeddings."""
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
