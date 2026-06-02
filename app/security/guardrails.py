import sqlglot
from sqlglot import exp

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

BLOCKED_NODES = (exp.Update, exp.Delete, exp.Insert, exp.Drop, exp.Alter, exp.TruncateTable, exp.Create)


class SQLGuardrail:
    @staticmethod
    def clean_sql(sql_query: str) -> str:
        return sql_query.replace("```sql", "").replace("```", "").strip().rstrip(";")

    @classmethod
    def validate_and_sanitize(cls, sql_query: str) -> tuple[bool, str, str | None]:
        cleaned = cls.clean_sql(sql_query)
        try:
            parsed = sqlglot.parse(cleaned, read=settings.sql_dialect)
            if not parsed:
                return False, cleaned, "Could not parse SQL."

            for expression in parsed:
                if not isinstance(expression, exp.Select) and not (
                    isinstance(expression, exp.Union) and expression.find(exp.Select)
                ):
                    return False, cleaned, "Only SELECT queries are permitted."

                for node in expression.walk():
                    if isinstance(node, BLOCKED_NODES):
                        return False, cleaned, f"Blocked operation: {type(node).__name__}"

            return True, cleaned, None
        except Exception as exc:
            logger.warning("SQL guardrail parse error: %s", exc)
            return False, cleaned, str(exc)
