"""Enterprise schema catalog — core tables plus simulated 800+ metadata entries."""

from __future__ import annotations

# Tables that exist in the sample database (executable)
EXECUTABLE_TABLES = frozenset(
    {
        "customers",
        "vendors",
        "invoices",
        "invoice_line_items",
        "payments",
        "vendor_payments",
        "fiscal_periods",
        "departments",
        "employees",
        "contracts",
        "purchase_orders",
        "accounts_receivable",
        "accounts_payable",
    }
)

CORE_SCHEMA_ENTRIES: list[dict] = [
    {
        "table_name": "customers",
        "description": "Corporate client master data with company name and outstanding balance in INR.",
        "schema_ddl": (
            "CREATE TABLE customers ("
            "customer_id INTEGER PRIMARY KEY, "
            "company_name VARCHAR(255) NOT NULL, "
            "outstanding_balance REAL DEFAULT 0, "
            "region VARCHAR(50), "
            "created_at DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "vendors",
        "description": "Supplier master records with vendor name and average payment delay in days.",
        "schema_ddl": (
            "CREATE TABLE vendors ("
            "vendor_id INTEGER PRIMARY KEY, "
            "vendor_name VARCHAR(255) NOT NULL, "
            "payment_delays_days INTEGER DEFAULT 0, "
            "category VARCHAR(100));"
        ),
        "executable": True,
    },
    {
        "table_name": "invoices",
        "description": "Customer billing transactions with amount, status PAID/UNPAID, due_date, fiscal_period_id.",
        "schema_ddl": (
            "CREATE TABLE invoices ("
            "invoice_id INTEGER PRIMARY KEY, "
            "customer_id INTEGER REFERENCES customers(customer_id), "
            "amount REAL NOT NULL, "
            "status VARCHAR(20) DEFAULT 'UNPAID', "
            "due_date DATE, "
            "invoice_date DATE, "
            "fiscal_period_id INTEGER);"
        ),
        "executable": True,
    },
    {
        "table_name": "invoice_line_items",
        "description": "Line-level invoice detail with product description and line amount.",
        "schema_ddl": (
            "CREATE TABLE invoice_line_items ("
            "line_id INTEGER PRIMARY KEY, "
            "invoice_id INTEGER REFERENCES invoices(invoice_id), "
            "description VARCHAR(500), "
            "line_amount REAL);"
        ),
        "executable": True,
    },
    {
        "table_name": "payments",
        "description": "Customer payment receipts linked to invoices with payment_date and amount.",
        "schema_ddl": (
            "CREATE TABLE payments ("
            "payment_id INTEGER PRIMARY KEY, "
            "invoice_id INTEGER REFERENCES invoices(invoice_id), "
            "amount REAL, "
            "payment_date DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "vendor_payments",
        "description": "Outbound vendor disbursements with delay_days and payment_date for AP analytics.",
        "schema_ddl": (
            "CREATE TABLE vendor_payments ("
            "vendor_payment_id INTEGER PRIMARY KEY, "
            "vendor_id INTEGER REFERENCES vendors(vendor_id), "
            "amount REAL, "
            "payment_date DATE, "
            "delay_days INTEGER);"
        ),
        "executable": True,
    },
    {
        "table_name": "fiscal_periods",
        "description": "Accounting quarters and fiscal years for period-based reporting.",
        "schema_ddl": (
            "CREATE TABLE fiscal_periods ("
            "fiscal_period_id INTEGER PRIMARY KEY, "
            "period_name VARCHAR(50), "
            "quarter INTEGER, "
            "year INTEGER, "
            "start_date DATE, "
            "end_date DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "purchase_orders",
        "description": "Procurement orders placed with vendors including PO amount and status.",
        "schema_ddl": (
            "CREATE TABLE purchase_orders ("
            "po_id INTEGER PRIMARY KEY, "
            "vendor_id INTEGER REFERENCES vendors(vendor_id), "
            "amount REAL, "
            "status VARCHAR(30), "
            "order_date DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "accounts_receivable",
        "description": "AR ledger balances per customer for outstanding receivables analysis.",
        "schema_ddl": (
            "CREATE TABLE accounts_receivable ("
            "ar_id INTEGER PRIMARY KEY, "
            "customer_id INTEGER REFERENCES customers(customer_id), "
            "balance REAL, "
            "as_of_date DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "accounts_payable",
        "description": "AP ledger balances per vendor for payables and delay tracking.",
        "schema_ddl": (
            "CREATE TABLE accounts_payable ("
            "ap_id INTEGER PRIMARY KEY, "
            "vendor_id INTEGER REFERENCES vendors(vendor_id), "
            "balance REAL, "
            "as_of_date DATE);"
        ),
        "executable": True,
    },
    {
        "table_name": "departments",
        "description": "Organizational departments for cost center allocation.",
        "schema_ddl": (
            "CREATE TABLE departments ("
            "department_id INTEGER PRIMARY KEY, "
            "department_name VARCHAR(100));"
        ),
        "executable": True,
    },
    {
        "table_name": "employees",
        "description": "Employee roster linked to departments.",
        "schema_ddl": (
            "CREATE TABLE employees ("
            "employee_id INTEGER PRIMARY KEY, "
            "full_name VARCHAR(150), "
            "department_id INTEGER REFERENCES departments(department_id));"
        ),
        "executable": True,
    },
    {
        "table_name": "contracts",
        "description": "Customer and vendor contracts with start/end dates and contract value.",
        "schema_ddl": (
            "CREATE TABLE contracts ("
            "contract_id INTEGER PRIMARY KEY, "
            "party_type VARCHAR(20), "
            "party_id INTEGER, "
            "contract_value REAL, "
            "start_date DATE, "
            "end_date DATE);"
        ),
        "executable": True,
    },
]

_DOMAINS = [
    ("finance", "General ledger, journal entries, and financial reporting"),
    ("hr", "Human resources, payroll, and workforce management"),
    ("inventory", "Stock levels, warehouses, and SKU master data"),
    ("crm", "Sales pipeline, leads, and customer engagement"),
    ("procurement", "Sourcing, RFQ, and supplier onboarding"),
    ("compliance", "Audit trails, regulatory filings, and controls"),
    ("analytics", "Data mart aggregates and KPI snapshots"),
    ("operations", "Manufacturing, logistics, and plant operations"),
]


def _synthetic_entries(target_total: int = 820) -> list[dict]:
    entries = list(CORE_SCHEMA_ENTRIES)
    idx = 0
    while len(entries) < target_total:
        domain, domain_desc = _DOMAINS[idx % len(_DOMAINS)]
        table_num = idx + 1
        table_name = f"{domain}_dim_{table_num:04d}"
        entries.append(
            {
                "table_name": table_name,
                "description": (
                    f"Enterprise {domain} dimensional table ({domain_desc}). "
                    f"Contains surrogate keys and slowly changing attributes for {domain} analytics."
                ),
                "schema_ddl": (
                    f"CREATE TABLE {table_name} ("
                    f"id INTEGER PRIMARY KEY, "
                    f"entity_code VARCHAR(50), "
                    f"effective_from DATE, "
                    f"effective_to DATE, "
                    f"is_active BOOLEAN);"
                ),
                "executable": False,
            }
        )
        idx += 1
    return entries


SCHEMA_CATALOG: list[dict] = _synthetic_entries(820)


def get_executable_catalog() -> list[dict]:
    return [e for e in SCHEMA_CATALOG if e.get("executable")]


def catalog_table_count() -> int:
    return len(SCHEMA_CATALOG)
