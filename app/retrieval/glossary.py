"""Business glossary — maps business terms to schema hints."""

from __future__ import annotations

GLOSSARY: dict[str, str] = {
    "lakhs": "1 lakh = 100,000 INR. Use amount > 500000 for '5 lakhs'.",
    "crore": "1 crore = 10,000,000 INR.",
    "last quarter": "Filter fiscal_periods.quarter or invoice_date in the previous calendar quarter.",
    "unpaid": "Invoice status = 'UNPAID'.",
    "outstanding balance": "customers.outstanding_balance or accounts_receivable.balance.",
    "payment delays": "vendors.payment_delays_days or vendor_payments.delay_days.",
    "top 10": "Use ORDER BY ... DESC LIMIT 10.",
    "vendor": "Table vendors; payments in vendor_payments.",
    "customer": "Table customers; billing in invoices.",
    "invoice": "Table invoices; line detail in invoice_line_items.",
    "this month": "Filter dates where strftime('%Y-%m', date_col) = strftime('%Y-%m', 'now') for SQLite.",
}


def expand_question_with_glossary(question: str) -> str:
    hints: list[str] = []
    lower = question.lower()
    for term, definition in GLOSSARY.items():
        if term in lower:
            hints.append(f"- {term}: {definition}")
    if not hints:
        return question
    glossary_block = "\n".join(hints)
    return f"{question}\n\nBusiness glossary hints:\n{glossary_block}"
