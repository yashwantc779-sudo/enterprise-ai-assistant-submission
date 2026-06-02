from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from app.config import settings
from app.core.exceptions import QueryExecutionError, SecurityViolationError
from app.core.logging import get_logger
from app.db.database import AsyncSessionLocal
from app.llm.service import LLMService
from app.retrieval.glossary import expand_question_with_glossary
from app.retrieval.vector_store import SchemaRetriever
from app.security.guardrails import SQLGuardrail
from app.services.confidence import score_confidence
from app.services.conversation import ConversationStore
from app.services.semantic_cache import SemanticCache

logger = get_logger(__name__)


class DataAssistantPipeline:
    def __init__(self) -> None:
        self.retriever = SchemaRetriever()  # ChromaDB or keyword fallback
        self.llm = LLMService()
        self.guardrail = SQLGuardrail()
        self.cache = SemanticCache()
        self.conversations = ConversationStore()
        self.retriever.seed_catalog()

    async def run(
        self,
        user_question: str,
        session_id: str | None = None,
        include_explanation: bool = True,
    ) -> dict[str, Any]:
        sid, session = self.conversations.get_or_create(session_id)
        enriched = expand_question_with_glossary(user_question)
        if session.turns:
            enriched = f"Conversation history:\n{session.context_block()}\n\nCurrent question:\n{enriched}"

        session.add("user", user_question)

        cached = self.cache.get(user_question)
        if cached:
            cached = dict(cached)
            cached["session_id"] = sid
            cached["cache_hit"] = True
            session.add("assistant", cached.get("business_summary", ""))
            return cached

        schema_context, table_names = self.retriever.retrieve_relevant_schemas(enriched)
        sql_query = await self.llm.generate_sql(enriched, schema_context)

        valid, sql_query, guard_error = self.guardrail.validate_and_sanitize(sql_query)
        if not valid:
            raise SecurityViolationError(guard_error or "SQL failed safety validation.")

        retry_count = 0
        max_retries = settings.MAX_SQL_RETRIES
        rows: list[dict] = []
        last_error: str | None = None

        async with AsyncSessionLocal() as db_session:
            while retry_count <= max_retries:
                try:
                    logger.info("Executing SQL (attempt %s): %s", retry_count + 1, sql_query)
                    result = await db_session.execute(text(sql_query))
                    columns = list(result.keys())
                    raw = result.fetchall()
                    rows = [dict(zip(columns, row)) for row in raw]
                    last_error = None
                    break
                except Exception as exc:
                    last_error = str(exc)
                    logger.warning("Query failed: %s", last_error)
                    retry_count += 1
                    if retry_count > max_retries:
                        raise QueryExecutionError(last_error) from exc
                    sql_query = await self.llm.self_heal_sql(
                        sql_query, last_error, schema_context, enriched
                    )
                    valid, sql_query, guard_error = self.guardrail.validate_and_sanitize(sql_query)
                    if not valid:
                        raise SecurityViolationError(guard_error or "Healed SQL failed validation.")

        explanation = ""
        if include_explanation:
            explanation = await self.llm.explain_sql(sql_query, user_question)

        sample = json.dumps(rows[:5], default=str)
        business_summary = await self.llm.summarize_results(user_question, len(rows), sample)

        confidence = score_confidence(
            tables_used=table_names,
            sql_valid=valid,
            execution_ok=last_error is None,
            retry_count=retry_count,
        )

        payload: dict[str, Any] = {
            "session_id": sid,
            "question": user_question,
            "generated_sql": sql_query,
            "tables_retrieved": table_names,
            "row_count": len(rows),
            "data": rows,
            "explanation": explanation,
            "business_summary": business_summary,
            "confidence_score": confidence,
            "retry_count": retry_count,
            "cache_hit": False,
        }

        self.cache.set(user_question, payload)
        session.add("assistant", business_summary)
        return payload
