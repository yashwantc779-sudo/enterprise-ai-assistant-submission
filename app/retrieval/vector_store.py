from __future__ import annotations

import re
from pathlib import Path

from app.config import settings
from app.core.logging import get_logger
from app.retrieval.schema_catalog import SCHEMA_CATALOG

logger = get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


class _KeywordSchemaRetriever:
    """Fallback retrieval when ChromaDB / sentence-transformers are unavailable."""

    def __init__(self) -> None:
        self._catalog = SCHEMA_CATALOG
        self._seeded = False

    @property
    def _collection(self):
        class _Count:
            def count(_self) -> int:
                return len(SCHEMA_CATALOG)

        return _Count()

    def seed_catalog(self, force: bool = False) -> None:
        self._seeded = True
        logger.info("Using keyword schema retriever (%s tables)", len(self._catalog))

    def retrieve_relevant_schemas(
        self,
        user_query: str,
        limit: int | None = None,
        prefer_executable: bool = True,
    ) -> tuple[str, list[str]]:
        limit = limit or settings.MAX_SCHEMA_RESULTS
        query_tokens = _tokens(user_query)
        scored: list[tuple[float, dict]] = []
        for item in self._catalog:
            doc_tokens = _tokens(f"{item['table_name']} {item['description']}")
            overlap = len(query_tokens & doc_tokens)
            bonus = 3.0 if item.get("executable") and prefer_executable else 0.0
            if overlap or bonus:
                scored.append((overlap + bonus, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            core = [e for e in self._catalog if e.get("executable")][:limit]
            selected = core
        else:
            selected = [item for _, item in scored[:limit]]
        table_names = [s["table_name"] for s in selected]
        ddl_blocks = [s["schema_ddl"] for s in selected]
        return "\n\n".join(ddl_blocks), table_names


class _ChromaSchemaRetriever:
    """Semantic schema retrieval over 800+ table metadata via ChromaDB."""

    def __init__(self) -> None:
        import chromadb
        from sentence_transformers import SentenceTransformer

        Path(settings.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self._collection = self._client.get_or_create_collection(
            name="enterprise_schema_catalog",
            metadata={"hnsw:space": "cosine"},
        )
        self._seeded = False

    def seed_catalog(self, force: bool = False) -> None:
        if self._seeded and not force:
            return
        if self._collection.count() > 0 and not force:
            self._seeded = True
            logger.info("Schema catalog already seeded (%s tables indexed)", self._collection.count())
            return

        logger.info("Seeding %s schema definitions into vector store...", len(SCHEMA_CATALOG))
        batch_size = 100
        for start in range(0, len(SCHEMA_CATALOG), batch_size):
            batch = SCHEMA_CATALOG[start : start + batch_size]
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            for item in batch:
                doc = f"{item['table_name']}: {item['description']}"
                emb = self._embedding_model.encode(doc).tolist()
                ids.append(item["table_name"])
                embeddings.append(emb)
                documents.append(doc)
                metadatas.append(
                    {
                        "table_name": item["table_name"],
                        "ddl": item["schema_ddl"],
                        "executable": str(item.get("executable", False)),
                    }
                )
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
        self._seeded = True
        logger.info("Schema catalog seeding complete.")

    def retrieve_relevant_schemas(
        self,
        user_query: str,
        limit: int | None = None,
        prefer_executable: bool = True,
    ) -> tuple[str, list[str]]:
        limit = limit or settings.MAX_SCHEMA_RESULTS
        query_vector = self._embedding_model.encode(user_query).tolist()
        fetch_n = min(limit * 3, 30) if prefer_executable else limit
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=fetch_n,
        )

        if not results or not results.get("metadatas") or not results["metadatas"][0]:
            raise ValueError("No relevant schemas found for the question.")

        metas = results["metadatas"][0]
        if prefer_executable:
            executable = [m for m in metas if m.get("executable") == "True"]
            others = [m for m in metas if m.get("executable") != "True"]
            ordered = executable + others
        else:
            ordered = metas

        selected = ordered[:limit]
        table_names = [m["table_name"] for m in selected]
        ddl_blocks = [m["ddl"] for m in selected]
        return "\n\n".join(ddl_blocks), table_names


def SchemaRetriever():
    try:
        import chromadb  # noqa: F401
        from sentence_transformers import SentenceTransformer  # noqa: F401

        return _ChromaSchemaRetriever()
    except ImportError:
        logger.warning("ChromaDB/sentence-transformers not installed; using keyword retriever.")
        return _KeywordSchemaRetriever()
