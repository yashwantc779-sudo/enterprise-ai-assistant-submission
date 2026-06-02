from __future__ import annotations


def score_confidence(
    tables_used: list[str],
    sql_valid: bool,
    execution_ok: bool,
    retry_count: int,
) -> float:
    score = 0.5
    if sql_valid:
        score += 0.15
    if execution_ok:
        score += 0.25
    if tables_used:
        score += min(0.1, len(tables_used) * 0.02)
    score -= retry_count * 0.08
    return round(max(0.0, min(1.0, score)), 2)
