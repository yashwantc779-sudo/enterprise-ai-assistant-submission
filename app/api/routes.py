from fastapi import APIRouter, HTTPException

from app.api.schemas import HealthResponse, QueryRequest, QueryResponse, SchemaStatsResponse
from app.config import settings
from app.core.exceptions import QueryExecutionError, SecurityViolationError
from app.core.logging import get_logger
from app.pipeline.executor import DataAssistantPipeline
from app.retrieval.schema_catalog import EXECUTABLE_TABLES, catalog_table_count

logger = get_logger(__name__)
router = APIRouter()
_pipeline: DataAssistantPipeline | None = None


def get_pipeline() -> DataAssistantPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = DataAssistantPipeline()
    return _pipeline


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    pipeline = get_pipeline()
    index_count = pipeline.retriever._collection.count()
    return HealthResponse(
        status="ok",
        catalog_tables=catalog_table_count(),
        mock_llm=settings.use_mock_llm,
    )


@router.get("/schema/stats", response_model=SchemaStatsResponse)
async def schema_stats() -> SchemaStatsResponse:
    pipeline = get_pipeline()
    return SchemaStatsResponse(
        total_tables_in_catalog=catalog_table_count(),
        executable_tables=len(EXECUTABLE_TABLES),
        vector_index_count=pipeline.retriever._collection.count(),
    )


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    try:
        result = await get_pipeline().run(
            user_question=request.prompt,
            session_id=request.session_id,
            include_explanation=request.include_explanation,
        )
        return QueryResponse(**result)
    except SecurityViolationError as exc:
        logger.error("Security violation: %s", exc)
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except QueryExecutionError as exc:
        logger.error("Query execution failed: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected pipeline error")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc
