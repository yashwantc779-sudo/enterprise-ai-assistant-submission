from __future__ import annotations

import asyncio
import re

from app.config import settings
from app.core.logging import get_logger
from app.llm.prompts import (
    EXPLANATION_PROMPT,
    RESPONSE_SUMMARY_PROMPT,
    SQL_GENERATION_PROMPT,
    SQL_HEAL_PROMPT,
)

logger = get_logger(__name__)


class LLMService:
    def __init__(self) -> None:
        self._model = None
        if not settings.use_mock_llm:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def _generate(self, prompt: str) -> str:
        if settings.use_mock_llm:
            return ""
        assert self._model is not None
        response = await asyncio.to_thread(self._model.generate_content, prompt)
        return (response.text or "").strip()

    async def generate_sql(self, user_question: str, schema_context: str) -> str:
        if settings.use_mock_llm:
            return self._mock_sql(user_question)
        prompt = SQL_GENERATION_PROMPT.format(
            dialect=settings.sql_dialect,
            schema_context=schema_context,
            question=user_question,
        )
        text = await self._generate(prompt)
        return self._strip_sql(text)

    async def self_heal_sql(
        self,
        broken_sql: str,
        error_message: str,
        schema_context: str,
        user_question: str,
    ) -> str:
        if settings.use_mock_llm:
            return self._mock_sql(user_question)
        prompt = SQL_HEAL_PROMPT.format(
            dialect=settings.sql_dialect,
            broken_sql=broken_sql,
            error_message=error_message,
            schema_context=schema_context,
        )
        text = await self._generate(prompt)
        return self._strip_sql(text)

    async def explain_sql(self, sql: str, question: str) -> str:
        if settings.use_mock_llm:
            return (
                f"This query retrieves data related to: {question}. "
                f"It reads from the database using: {sql[:120]}..."
            )
        prompt = EXPLANATION_PROMPT.format(sql=sql, question=question)
        return await self._generate(prompt)

    async def summarize_results(self, question: str, row_count: int, sample: str) -> str:
        if settings.use_mock_llm:
            return f"Found {row_count} record(s) matching your question about: {question}."
        prompt = RESPONSE_SUMMARY_PROMPT.format(
            question=question, row_count=row_count, sample=sample[:2000]
        )
        return await self._generate(prompt)

    @staticmethod
    def _strip_sql(text: str) -> str:
        text = text.replace("```sql", "").replace("```", "").strip()
        match = re.search(r"(SELECT[\s\S]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else text

    @staticmethod
    def _mock_sql(question: str) -> str:
        q = question.lower()
        if "unpaid" in q and ("lakh" in q or "500000" in q or "5 lakh" in q):
            return (
                "SELECT i.invoice_id, c.company_name, i.amount, i.status, i.due_date "
                "FROM invoices i "
                "JOIN customers c ON i.customer_id = c.customer_id "
                "WHERE i.status = 'UNPAID' AND i.amount > 500000 "
                "AND i.fiscal_period_id = 1"
            )
        if "vendor" in q and ("top" in q or "delay" in q):
            return (
                "SELECT v.vendor_name, v.payment_delays_days "
                "FROM vendors v "
                "ORDER BY v.payment_delays_days DESC "
                "LIMIT 10"
            )
        if "outstanding" in q and "customer" in q:
            return (
                "SELECT company_name, outstanding_balance "
                "FROM customers "
                "ORDER BY outstanding_balance DESC "
                "LIMIT 10"
            )
        if "invoice" in q:
            return "SELECT * FROM invoices WHERE status = 'UNPAID' LIMIT 20"
        return "SELECT company_name, outstanding_balance FROM customers ORDER BY outstanding_balance DESC LIMIT 5"
