# StepResult dataclass, per-step retries/orchestration

"""Step execution and result management for the agent pipeline."""

from dataclasses import dataclass
import re

import pandas as pd
from sqlalchemy.engine import Engine

from ..config import MAX_STEPS, PER_STEP_RETRIES
from ..db.execute import execute_sql
from ..llms.client import call_llm
from ..prompts import PLANNER_SYSTEM, PLANNER_USER_TEMPLATE
from ..rag.vectorstore import retrieve_schema_context
from .generate_sql import generate_sql_for_subtask
from .validate_sql import sql_is_plausible


@dataclass
class StepResult:
    step_id: int
    title: str
    description: str
    sql: str | None = None
    result_df: pd.DataFrame | None = None
    error: str | None = None


def parse_numbered_list(text: str) -> list[tuple[str, str]]:
    """
    Parse "1) Title — description" style list into [(title, desc), ...].
    Quite forgiving to variations.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    steps = []
    for ln in lines:
        m = re.match(r"^\s*\d+\)?[.)]?\s*(.+)$", ln)
        if not m:
            continue
        body = m.group(1)
        # split on em dash or hyphen dash types
        parts = re.split(r"\s+—\s+|\s+-\s+|:\s+", body, maxsplit=1)
        if len(parts) == 2:
            steps.append((parts[0].strip(), parts[1].strip()))
        else:
            steps.append((body.strip(), ""))  # only title
    return steps


def plan_subtasks(user_request: str, max_steps: int = None) -> list[tuple[str, str]]:
    if max_steps is None:
        max_steps = MAX_STEPS

    print(f"[PLANNING] Starting task planning for: {user_request}")
    schema_ctx = retrieve_schema_context(user_request)
    print(f"[PLANNING] Retrieved schema context ({len(schema_ctx)} characters)")

    user_prompt = PLANNER_USER_TEMPLATE.format(
        user_request=user_request, schema_context=schema_ctx, max_steps=max_steps
    )
    print("[PLANNING] Calling LLM for task breakdown...")
    plan_text = call_llm(PLANNER_SYSTEM, user_prompt)

    steps = parse_numbered_list(plan_text)
    if not steps:
        print("[PLANNING] No steps parsed, using default single-step approach")
        steps = [("Single-step query", "Directly produce the final answer in one query.")]

    print(f"[PLANNING] Generated {len(steps)} steps:")
    for i, (title, desc) in enumerate(steps, 1):
        print(f"[PLANNING]   Step {i}: {title}")

    return steps[:max_steps]


def run_agent(
    user_request: str, engine: Engine, max_steps: int = None, per_step_retries: int = None
) -> list[StepResult]:
    if max_steps is None:
        max_steps = MAX_STEPS
    if per_step_retries is None:
        per_step_retries = PER_STEP_RETRIES

    print("[AGENT] Starting agent execution")
    print(f"[AGENT] Configuration: max_steps={max_steps}, retries={per_step_retries}")

    steps = plan_subtasks(user_request, max_steps=max_steps)
    results: list[StepResult] = []
    prior_sql: list[str] = []

    for i, (title, desc) in enumerate(steps, start=1):
        print(f"\n[STEP {i}] Processing: {title}")
        print(f"[STEP {i}] Description: {desc}")

        sr = StepResult(step_id=i, title=title, description=desc)

        # Generate initial SQL
        print(f"[STEP {i}] Generating initial SQL...")
        sql = generate_sql_for_subtask(f"{title} — {desc}", prior_sql, user_request)
        sr.sql = sql
        print(f"[STEP {i}] Generated SQL: {sql[:100]}...")

        # Track all attempts for debugging
        attempted_queries = [sql]
        attempt = 0
        success = False
        final_error = None

        while attempt < per_step_retries and not success:
            attempt += 1
            current_sql = attempted_queries[-1]
            print(f"[STEP {i}] Attempt {attempt}/{per_step_retries}")

            # Check SQL plausibility first
            print(f"[STEP {i}] Validating SQL syntax...")
            if not sql_is_plausible(current_sql):
                print(f"[STEP {i}] SQL syntax validation FAILED")
                syntax_error = "SQL syntax validation failed. Please check for proper SQL syntax, missing keywords, or malformed statements."

                if attempt < per_step_retries:
                    print(f"[STEP {i}] Generating corrected SQL for syntax error...")
                    corrected_sql = generate_sql_for_subtask(
                        f"(Fix syntax error - Attempt {attempt}) {title} — {desc}. "
                        f"Previous failed query: {current_sql}. "
                        f"Error: {syntax_error}",
                        prior_sql,
                        user_request,
                    )
                    attempted_queries.append(corrected_sql)
                    sr.sql = corrected_sql
                    print(f"[STEP {i}] Generated corrected SQL: {corrected_sql[:100]}...")
                    continue
                else:
                    print(f"[STEP {i}] Max retries reached for syntax errors")
                    final_error = (
                        f"SQL syntax validation failed after {per_step_retries} attempts. "
                    )
                    final_error += f"Attempted queries: {'; '.join(attempted_queries)}"
                    break

            # Try to execute SQL
            print(f"[STEP {i}] SQL syntax validation PASSED")
            print(f"[STEP {i}] Executing SQL query...")

            try:
                df_result = execute_sql(engine, current_sql, max_rows=500)
                print(f"[STEP {i}] SQL execution SUCCESSFUL - {len(df_result)} rows returned")
                success = True
                sr.result_df = df_result
            except Exception as e:
                execution_error = str(e)
                print(f"[STEP {i}] SQL execution FAILED: {execution_error}")

                if attempt < per_step_retries:
                    print(f"[STEP {i}] Generating corrected SQL for execution error...")
                    corrected_sql = generate_sql_for_subtask(
                        f"(Fix execution error - Attempt {attempt}) {title} — {desc}. "
                        f"Previous failed query: {current_sql}. "
                        f"Execution error: {execution_error}",
                        prior_sql,
                        user_request,
                    )
                    attempted_queries.append(corrected_sql)
                    sr.sql = corrected_sql
                    print(f"[STEP {i}] Generated corrected SQL: {corrected_sql[:100]}...")
                else:
                    print(f"[STEP {i}] Max retries reached for execution errors")
                    final_error = f"SQL execution failed after {per_step_retries} attempts. "
                    final_error += f"Last error: {execution_error}. "
                    final_error += f"Attempted queries: {'; '.join(attempted_queries)}"

        # Set error if not successful
        if not success:
            print(f"[STEP {i}] Step FAILED after all retries")
            sr.error = final_error
        else:
            print(f"[STEP {i}] Step completed SUCCESSFULLY")

        results.append(sr)

        # Only append prior SQL if success
        if success and sr.sql:
            prior_sql.append(sr.sql)
            print(f"[STEP {i}] Added successful SQL to context for next steps")
        else:
            print(f"[AGENT] Pipeline stopped at step {i} due to repeated failures")
            print(f"[AGENT] Failed queries attempted: {attempted_queries}")
            break

    print(
        f"\n[AGENT] Execution completed - {len([r for r in results if r.error is None])} successful steps"
    )
    return results
