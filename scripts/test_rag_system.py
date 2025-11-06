#!/usr/bin/env python3
"""
Test script for RAG (Retrieval-Augmented Generation) functionality.
Tests document loading, embedding, vector storage, and retrieval.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_pipeline.config import DATA_DIR
from agent_pipeline.rag.embeddings import create_embeddings
from agent_pipeline.rag.loader import load_documents
from agent_pipeline.rag.splitter import split_documents
from agent_pipeline.rag.vectorstore import create_vectorstore, get_retriever


def test_document_loading():
    """Test document loading from data directory."""
    print(" Testing Document Loading...")

    try:
        docs = load_documents(DATA_DIR)
        print(f" Loaded {len(docs)} documents")

        if docs:
            print(" Sample document content:")
            print(f"  - Source: {docs[0].metadata.get('source', 'Unknown')}")
            print(f"  - Content preview: {docs[0].page_content[:100]}...")
            return True
        else:
            print(" No documents loaded")
            return False

    except Exception as e:
        print(f" Document loading failed: {e}")
        return False


def test_document_splitting():
    """Test document splitting into chunks."""
    print(" Testing Document Splitting...")

    try:
        # Load documents first
        docs = load_documents(DATA_DIR)
        if not docs:
            print(" No documents to split")
            return False

        # Split documents
        chunks = split_documents(docs)
        print(f" Split into {len(chunks)} chunks")

        if chunks:
            print(" Sample chunk:")
            print(f"  - Size: {len(chunks[0].page_content)} characters")
            print(f"  - Content: {chunks[0].page_content[:150]}...")
            return True
        else:
            print(" No chunks created")
            return False

    except Exception as e:
        print(f" Document splitting failed: {e}")
        return False


def test_embeddings_creation():
    """Test embedding model creation."""
    print(" Testing Embeddings Creation...")

    try:
        embeddings = create_embeddings()
        print(f" Embeddings model created: {type(embeddings).__name__}")

        # Test embedding a sample text
        sample_text = "This is a test sentence for embedding."
        embedding_vector = embeddings.embed_query(sample_text)
        print(f" Sample embedding dimension: {len(embedding_vector)}")

        return True

    except Exception as e:
        print(f" Embeddings creation failed: {e}")
        return False


def test_vectorstore_creation():
    """Test vector store creation and population."""
    print(" Testing Vector Store Creation...")

    try:
        # Load and split documents
        docs = load_documents(DATA_DIR)
        if not docs:
            print(" No documents available for vector store")
            return False

        chunks = split_documents(docs)
        if not chunks:
            print(" No chunks available for vector store")
            return False

        # Create vector store
        vectorstore = create_vectorstore(chunks)
        print(f" Vector store created with {len(chunks)} documents")

        # Test similarity search
        query = "table structure"
        results = vectorstore.similarity_search(query, k=2)
        print(f" Search results for '{query}':")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.page_content[:100]}...")

        return True

    except Exception as e:
        print(f" Vector store creation failed: {e}")
        return False


def test_retriever_functionality():
    """Test retriever functionality."""
    print(" Testing Retriever Functionality...")

    try:
        # Get retriever (this will create vector store if needed)
        retriever = get_retriever()
        print(" Retriever obtained successfully")

        # Test retrieval
        query = "employee database schema"
        docs = retriever.invoke(query)
        print(f" Retrieved {len(docs)} documents for query: '{query}'")

        if docs:
            print(" Top result:")
            print(f"  - Content: {docs[0].page_content[:200]}...")
            return True
        else:
            print(" No documents retrieved")
            return False

    except Exception as e:
        print(f" Retriever test failed: {e}")
        return False


def test_rag_integration():
    """Test full RAG pipeline integration."""
    print(" Testing RAG Integration...")

    try:
        # Test the complete RAG flow
        queries = [
            "What tables are in the database?",
            "How are users and departments related?",
            "What columns are in the employee_records table?",
        ]

        retriever = get_retriever()

        for query in queries:
            print(f"\n Query: {query}")
            docs = retriever.invoke(query)

            if docs:
                print(f"   Found {len(docs)} relevant documents")
                # Show the most relevant content
                best_doc = docs[0]
                print(f"   Best match: {best_doc.page_content[:150]}...")
            else:
                print("   No relevant documents found")

        print(" RAG integration test completed")
        return True

    except Exception as e:
        print(f" RAG integration test failed: {e}")
        return False


def main():
    """Run all RAG tests."""
    print(" Starting RAG Test Suite...")
    print(f" Data Directory: {DATA_DIR}")
    print("-" * 60)

    tests = [
        ("Document Loading", test_document_loading),
        ("Document Splitting", test_document_splitting),
        ("Embeddings Creation", test_embeddings_creation),
        ("Vector Store Creation", test_vectorstore_creation),
        ("Retriever Functionality", test_retriever_functionality),
        ("RAG Integration", test_rag_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n Running: {test_name}")
        success = test_func()
        results.append((test_name, success))
        print()

    print("=" * 60)
    print(" TEST RESULTS:")
    passed = 0
    for test_name, success in results:
        status = " PASS" if success else " FAIL"
        print(f"  {status}: {test_name}")
        if success:
            passed += 1

    print(f"\n Summary: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print(" All RAG tests passed!")
        return True
    else:
        print(" Some RAG tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
