class SecurityViolationError(Exception):
    """Raised when generated SQL fails safety validation."""


class SchemaRetrievalError(Exception):
    """Raised when schema context cannot be built."""


class QueryExecutionError(Exception):
    """Raised when SQL execution fails after all retries."""
