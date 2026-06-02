from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Natural language business question")
    session_id: str | None = Field(None, description="Optional session ID for multi-turn chat")
    include_explanation: bool = True


class QueryResponse(BaseModel):
    session_id: str
    question: str
    generated_sql: str
    tables_retrieved: list[str]
    row_count: int
    data: list[dict[str, Any]]
    explanation: str
    business_summary: str
    confidence_score: float
    retry_count: int
    cache_hit: bool


class HealthResponse(BaseModel):
    status: str
    catalog_tables: int
    mock_llm: bool


class SchemaStatsResponse(BaseModel):
    total_tables_in_catalog: int
    executable_tables: int
    vector_index_count: int
