# generate_sql_for_subtask() using LLM & prior context

"""SQL generation utilities for the agent pipeline."""

import re

from ..llms.client import call_llm
from ..prompts import SQL_SYSTEM, SQL_USER_TEMPLATE
from ..rag.vectorstore import retrieve_schema_context


def generate_sql_for_subtask(subtask_text: str, prior_sql: list[str], user_request: str) -> str:
    """Generate SQL for a specific subtask using LLM with schema context and prior steps."""
    schema_ctx = retrieve_schema_context(user_request + "\n\n" + subtask_text)
    prior = (
        "\n\n".join([f"-- Step {i+1}\n{q}" for i, q in enumerate(prior_sql)])
        if prior_sql
        else "(none)"
    )
    user_prompt = SQL_USER_TEMPLATE.format(
        subtask_text=subtask_text, schema_context=schema_ctx, prior_sql=prior
    )
    raw = call_llm(SQL_SYSTEM, user_prompt)
    # Extract fenced code if LLM returned it with backticks
    code_block = re.search(r"```(?:sql)?\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    sql = code_block.group(1).strip() if code_block else raw.strip()
    return sql
