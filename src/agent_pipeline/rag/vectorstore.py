# FAISS build/load + retriever factory

"""Vector store and retriever utilities for RAG pipeline."""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from ..config import RAG_SEARCH_K
from .embeddings import create_embeddings
from .loader import load_documents
from .splitter import split_documents

# Global vectorstore and retriever instances
_vectorstore_instance: FAISS | None = None
_retriever_instance: VectorStoreRetriever | None = None


def get_vectorstore() -> FAISS:
    """Get the global vectorstore instance, creating it if necessary."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = create_vectorstore()
    return _vectorstore_instance


def get_retriever() -> VectorStoreRetriever:
    """Get the global retriever instance, creating it if necessary."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = create_retriever()
    return _retriever_instance


def create_vectorstore(docs: list[Document] = None) -> FAISS:
    """Create FAISS vectorstore from documents."""
    if docs is None:
        # Load and split documents
        docs = load_documents()
        chunks = split_documents(docs)
    else:
        chunks = docs

    # Create embeddings
    embed = create_embeddings()

    # Create vector store
    vectorstore = FAISS.from_documents(chunks, embed)

    print("RAG system ready!")
    return vectorstore


def create_retriever(vectorstore: FAISS = None, k: int = None) -> VectorStoreRetriever:
    """Create retriever from vectorstore."""
    if vectorstore is None:
        vectorstore = get_vectorstore()
    if k is None:
        k = RAG_SEARCH_K

    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_schema_context(query_text: str, k: int = None) -> str:
    """Grab top-k schema chunks for the planning or generation step."""
    if k is None:
        k = RAG_SEARCH_K

    retriever = get_retriever()
    # Updated to use invoke instead of get_relevant_documents
    rel_docs = retriever.invoke(query_text)
    return "\n---\n".join(d.page_content for d in rel_docs[:k])
