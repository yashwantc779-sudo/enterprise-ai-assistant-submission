-- Core executable tables (subset of 820-table enterprise catalog)
-- See app/retrieval/schema_catalog.py for full metadata catalog.

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    outstanding_balance REAL DEFAULT 0,
    region VARCHAR(50),
    created_at DATE
);

CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    payment_delays_days INTEGER DEFAULT 0,
    category VARCHAR(100)
);

CREATE TABLE fiscal_periods (
    fiscal_period_id INTEGER PRIMARY KEY,
    period_name VARCHAR(50),
    quarter INTEGER,
    year INTEGER,
    start_date DATE,
    end_date DATE
);

CREATE TABLE invoices (
    invoice_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    amount REAL NOT NULL,
    status VARCHAR(20) DEFAULT 'UNPAID',
    due_date DATE,
    invoice_date DATE,
    fiscal_period_id INTEGER REFERENCES fiscal_periods(fiscal_period_id)
);
