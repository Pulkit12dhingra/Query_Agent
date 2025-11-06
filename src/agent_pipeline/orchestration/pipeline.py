# end-to-end pipeline() that wires RAG + Agent + DB

"""Main pipeline orchestration that connects all components."""

from sqlalchemy.engine import Engine

from ..agent.run_steps import StepResult, run_agent
from ..db.engine import get_engine, test_db_connection
from ..health.ollama_check import check_ollama_health
from ..logging_utils import log_and_print
from ..rag.vectorstore import get_retriever, get_vectorstore


def initialize_pipeline() -> bool:
    """Initialize all pipeline components and verify they're working."""
    log_and_print("Initializing pipeline components...")

    # 1. Check Ollama health
    log_and_print("Checking Ollama health...")
    if not check_ollama_health():
        log_and_print("Ollama health check failed!", "error")
        return False

    # 2. Test database connection
    log_and_print("Testing database connection...")
    try:
        engine = get_engine()
        tables = test_db_connection(engine)
        log_and_print(f"Database connection successful. Found {len(tables)} tables.")
    except Exception as e:
        log_and_print(f"Database connection failed: {e}", "error")
        return False

    # 3. Initialize RAG system
    log_and_print("Initializing RAG system...")
    try:
        get_vectorstore()  # Initialize vectorstore
        get_retriever()  # Initialize retriever
        log_and_print("RAG system initialized successfully.")
    except Exception as e:
        log_and_print(f"RAG system initialization failed: {e}", "error")
        return False

    log_and_print("Pipeline initialization completed successfully!")
    return True


def run_query_pipeline(
    user_request: str,
    engine: Engine = None,
    max_steps: int = None,
    per_step_retries: int = None,
    auto_initialize: bool = True,
) -> list[StepResult]:
    """
    Run the complete query automation pipeline.

    Args:
        user_request: The user's natural language query request
        engine: Database engine (will use default if None)
        max_steps: Maximum steps in the pipeline
        per_step_retries: Number of retries per step
        auto_initialize: Whether to automatically initialize components

    Returns:
        List of StepResult objects containing the pipeline execution results
    """
    if auto_initialize and not initialize_pipeline():
        raise RuntimeError("Pipeline initialization failed")

    if engine is None:
        engine = get_engine()

    log_and_print(f"Starting query pipeline for: {user_request}")

    try:
        results = run_agent(
            user_request=user_request,
            engine=engine,
            max_steps=max_steps,
            per_step_retries=per_step_retries,
        )

        # Log summary
        success_count = len([r for r in results if r.error is None])
        log_and_print(f"Pipeline completed: {success_count}/{len(results)} steps successful")

        return results

    except Exception as e:
        log_and_print(f"Pipeline execution failed: {e}", "error")
        raise


def get_final_result(results: list[StepResult]) -> StepResult | None:
    """Get the final successful result from pipeline execution."""
    successful = [r for r in results if r.error is None and r.result_df is not None]
    return successful[-1] if successful else None
