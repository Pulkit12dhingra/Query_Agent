# execute_sql_with_limit()/timeouts -> DataFrame

"""SQL execution utilities with timeout protection and row limits."""

from contextlib import contextmanager
import signal

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..config import MAX_SQL_ROWS, SQL_TIMEOUT
from .engine import get_engine


@contextmanager
def sql_timeout(duration: int):
    """Context manager to timeout SQL operations"""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"SQL execution timed out after {duration} seconds")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)


def execute_sql(
    engine: Engine = None, sql: str = None, max_rows: int = None, timeout_seconds: int = None
) -> pd.DataFrame:
    """
    Execute SQL directly with timeout protection; return DataFrame. Limits rows to avoid runaway results.
    Any errors will be raised as exceptions.
    """
    if engine is None:
        engine = get_engine()
    if max_rows is None:
        max_rows = MAX_SQL_ROWS
    if timeout_seconds is None:
        timeout_seconds = SQL_TIMEOUT

    # Clean the SQL - remove trailing semicolons and whitespace
    clean_sql = sql.strip().rstrip(";").strip()

    # Check if query already has LIMIT clause
    sql_upper = clean_sql.upper()
    if "LIMIT" not in sql_upper:
        # Add LIMIT clause safely - max_rows is an integer parameter, not user input
        limited_sql = f"SELECT * FROM ({clean_sql}) AS limited_query LIMIT {max_rows}"  # noqa: S608
    else:
        # Query already has LIMIT, use as-is
        limited_sql = clean_sql

    # Execute with timeout protection
    with sql_timeout(timeout_seconds), engine.connect() as conn:
        df = pd.read_sql(text(limited_sql), conn)
    return df
