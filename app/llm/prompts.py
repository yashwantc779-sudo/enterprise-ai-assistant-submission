SQL_GENERATION_PROMPT = """You are an expert enterprise data analyst for a company with 800+ database tables.
Generate a single, syntactically correct {dialect} SQL query.

Rules:
- Use ONLY tables and columns from the provided schemas.
- Prefer executable core tables when available.
- Return ONLY raw SQL — no markdown, no explanation.
- Use read-only SELECT statements only.
- For "5 lakhs" use amount > 500000 (INR).
- For "last quarter" use fiscal_period_id = 1 or invoice_date between '2025-10-01' and '2025-12-31' when Q4 2025 is last quarter in sample data.

Schemas:
{schema_context}

User question:
{question}
"""

SQL_HEAL_PROMPT = """The SQL query below failed at runtime.

Failed SQL:
{broken_sql}

Error:
{error_message}

Schemas:
{schema_context}

Return ONLY a corrected {dialect} SELECT query. No markdown."""

EXPLANATION_PROMPT = """Explain this SQL query in plain business language (2-4 sentences, non-technical):

SQL:
{sql}

Question:
{question}
"""

RESPONSE_SUMMARY_PROMPT = """Summarize query results for a business user in 2-3 sentences.

Question: {question}
Row count: {row_count}
Sample rows (JSON): {sample}

Be concise and actionable."""
