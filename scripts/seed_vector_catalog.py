"""Re-seed ChromaDB schema catalog."""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.retrieval.vector_store import SchemaRetriever

if __name__ == "__main__":
    r = SchemaRetriever()
    r.seed_catalog(force=True)
    print("Seeded", r._collection.count(), "entries")
