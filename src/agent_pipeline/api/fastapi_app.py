"""FastAPI server for the query automation agent."""

import logging
from pathlib import Path
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup path for imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

# Import after path setup
from agent_pipeline.agent.run_steps import StepResult  # noqa: E402
from agent_pipeline.orchestration.pipeline import (  # noqa: E402
    get_final_result,
    initialize_pipeline,
    run_query_pipeline,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track initialization
_pipeline_initialized = False


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query", min_length=1)
    max_steps: int | None = Field(None, description="Maximum steps in the pipeline")
    per_step_retries: int | None = Field(None, description="Number of retries per step")


class QueryValidationRequest(BaseModel):
    query: str = Field(..., description="Natural language query to validate", min_length=1)


class HealthResponse(BaseModel):
    status: str
    message: str
    pipeline_initialized: bool


class QueryResponse(BaseModel):
    success: bool
    query: str
    sql: str | None = None
    row_count: int | None = None
    data: list[dict[str, Any]] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class ValidationResponse(BaseModel):
    valid: bool
    query: str
    message: str | None = None
    suggestions: list[str] = []
    error: str | None = None


class SchemaResponse(BaseModel):
    success: bool
    database_info: dict[str, Any] | None = None
    error: str | None = None


class ExecutionStep(BaseModel):
    step: int
    success: bool
    has_data: bool
    error: str | None = None
    sql_generated: bool | None = None
    sql_preview: str | None = None


# Initialize FastAPI app
app = FastAPI(
    title="Query Automation Agent API",
    description="Natural language to SQL query automation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_pipeline_initialized():
    """Ensure the pipeline is initialized before processing requests."""
    global _pipeline_initialized
    if not _pipeline_initialized:
        logger.info("Initializing pipeline...")
        if initialize_pipeline():
            _pipeline_initialized = True
            logger.info("Pipeline initialized successfully!")
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Pipeline initialization failed",
            )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        ensure_pipeline_initialized()
        return HealthResponse(
            status="healthy",
            message="Query automation agent is running",
            pipeline_initialized=_pipeline_initialized,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy", message=str(e), pipeline_initialized=_pipeline_initialized
        )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query and return SQL results.

    - **query**: Natural language query (required)
    - **max_steps**: Maximum steps in the pipeline (optional)
    - **per_step_retries**: Number of retries per step (optional)
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Ensure pipeline is ready
        ensure_pipeline_initialized()

        # Run the query pipeline
        results = run_query_pipeline(
            user_request=request.query,
            max_steps=request.max_steps,
            per_step_retries=request.per_step_retries,
            auto_initialize=False,  # We already initialized
        )

        # Get final result
        final_result = get_final_result(results)

        if final_result:
            # Convert DataFrame to dict for JSON serialization
            result_data = (
                final_result.result_df.to_dict("records")
                if final_result.result_df is not None
                else []
            )

            response = QueryResponse(
                success=True,
                query=request.query,
                sql=final_result.sql,
                row_count=len(result_data),
                data=result_data,
                metadata={
                    "total_steps": len(results),
                    "successful_steps": len([r for r in results if r.error is None]),
                    "execution_summary": _get_execution_summary(results),
                },
            )

            logger.info(f"Query processed successfully. Generated SQL: {final_result.sql}")
            return response
        else:
            # No successful result
            response = QueryResponse(
                success=False,
                query=request.query,
                error="No successful results generated",
                metadata={
                    "total_steps": len(results),
                    "successful_steps": 0,
                    "execution_summary": _get_execution_summary(results),
                },
            )

            logger.warning(f"Query failed to produce results: {request.query}")
            return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@app.post("/query/validate", response_model=ValidationResponse)
async def validate_query(request: QueryValidationRequest):
    """
    Validate a natural language query without executing it.

    - **query**: Natural language query to validate
    """
    try:
        user_query = request.query.strip()

        # Simple validation - just check if query is reasonable
        response = ValidationResponse(
            valid=True,
            query=user_query,
            message="Query appears to be valid natural language",
            suggestions=[],
        )

        # Add some basic suggestions
        if len(user_query.split()) < 3:
            response.suggestions.append("Consider providing more details in your query")

        if "?" not in user_query and not any(
            word in user_query.lower() for word in ["show", "get", "find", "list", "count"]
        ):
            response.suggestions.append(
                "Try starting with action words like 'show', 'get', 'find', or 'list'"
            )

        return response

    except Exception as e:
        logger.error(f"Error validating query: {e}")
        return ValidationResponse(valid=False, query=request.query, error=str(e))


@app.get("/schema", response_model=SchemaResponse)
async def get_schema_info():
    """Get information about the database schema."""
    try:
        ensure_pipeline_initialized()

        # Import here to avoid circular imports
        from agent_pipeline.db.engine import get_engine, test_db_connection

        engine = get_engine()
        tables = test_db_connection(engine)

        return SchemaResponse(
            success=True, database_info={"table_count": len(tables), "tables": tables}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting schema info: {e}")
        return SchemaResponse(success=False, error=str(e))


def _get_execution_summary(results: list[StepResult]) -> list[ExecutionStep]:
    """Create a summary of the execution steps."""
    summary = []
    for i, result in enumerate(results, 1):
        step_info = ExecutionStep(
            step=i,
            success=result.error is None,
            has_data=result.result_df is not None and not result.result_df.empty
            if result.result_df is not None
            else False,
        )

        if result.error:
            step_info.error = str(result.error)

        if result.sql:
            step_info.sql_generated = True
            step_info.sql_preview = (
                result.sql[:100] + "..." if len(result.sql) > 100 else result.sql
            )

        summary.append(step_info)

    return summary


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Query Automation Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "GET /health - Health check",
            "query": "POST /query - Process natural language query",
            "validate": "POST /query/validate - Validate query without execution",
            "schema": "GET /schema - Get database schema information",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Query Automation Agent FastAPI Server...")
    print("API will be available at: http://127.0.0.1:8000")
    print("Interactive docs at: http://127.0.0.1:8000/docs")
    print("Alternative docs at: http://127.0.0.1:8000/redoc")
    print("\nPress Ctrl+C to stop the server")

    uvicorn.run(
        "agent_pipeline.api.app:app", host="127.0.0.1", port=8000, reload=False, log_level="info"
    )
