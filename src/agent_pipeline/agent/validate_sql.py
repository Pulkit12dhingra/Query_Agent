# sql_is_plausible() using sqlparse/heuristics

"""SQL validation utilities for the agent pipeline."""

import sqlparse


def sql_is_plausible(sql: str) -> bool:
    """Very light static check using sqlparse (ensures at least one statement, no obvious empties)."""
    parsed = sqlparse.parse(sql)
    return len(parsed) >= 1 and any(
        tok.ttype is not None or tok.is_group for tok in parsed[0].tokens
    )
