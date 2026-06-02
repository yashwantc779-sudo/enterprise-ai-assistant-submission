import datetime

from sqlalchemy import func, select

from app.db.database import AsyncSessionLocal
from app.db.models import (
    AccountsPayable,
    AccountsReceivable,
    Contract,
    Customer,
    Department,
    Employee,
    FiscalPeriod,
    Invoice,
    InvoiceLineItem,
    Payment,
    PurchaseOrder,
    Vendor,
    VendorPayment,
)


async def seed_if_empty() -> None:
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(func.count()).select_from(Customer))
        if count and count > 0:
            return

        q4_2025 = FiscalPeriod(
            fiscal_period_id=1,
            period_name="Q4 2025",
            quarter=4,
            year=2025,
            start_date=datetime.date(2025, 10, 1),
            end_date=datetime.date(2025, 12, 31),
        )
        q1_2026 = FiscalPeriod(
            fiscal_period_id=2,
            period_name="Q1 2026",
            quarter=1,
            year=2026,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 3, 31),
        )
        session.add_all([q4_2025, q1_2026])

        customers = [
            Customer(customer_id=1, company_name="Tata Consultancy Services", outstanding_balance=1250000.0, region="West", created_at=datetime.date(2024, 1, 10)),
            Customer(customer_id=2, company_name="Reliance Industries", outstanding_balance=450000.0, region="West", created_at=datetime.date(2024, 3, 15)),
            Customer(customer_id=3, company_name="Infosys Technologies", outstanding_balance=890000.0, region="South", created_at=datetime.date(2024, 6, 1)),
            Customer(customer_id=4, company_name="Wipro Limited", outstanding_balance=320000.0, region="South", created_at=datetime.date(2025, 1, 20)),
            Customer(customer_id=5, company_name="HDFC Bank", outstanding_balance=2100000.0, region="West", created_at=datetime.date(2023, 11, 5)),
        ]
        session.add_all(customers)

        vendors = [
            Vendor(vendor_id=1, vendor_name="Hardware Dynamics Ltd", payment_delays_days=45, category="IT Hardware"),
            Vendor(vendor_id=2, vendor_name="Global Cloud Solutions Inc", payment_delays_days=12, category="Cloud"),
            Vendor(vendor_id=3, vendor_name="Elite Security Networks", payment_delays_days=31, category="Security"),
            Vendor(vendor_id=4, vendor_name="Prime Logistics Partners", payment_delays_days=22, category="Logistics"),
            Vendor(vendor_id=5, vendor_name="Apex Office Supplies", payment_delays_days=8, category="Supplies"),
            Vendor(vendor_id=6, vendor_name="Zenith Data Centers", payment_delays_days=55, category="Infrastructure"),
            Vendor(vendor_id=7, vendor_name="Swift Courier Services", payment_delays_days=18, category="Logistics"),
            Vendor(vendor_id=8, vendor_name="Nova Software Licensing", payment_delays_days=5, category="Software"),
            Vendor(vendor_id=9, vendor_name="Sterling Facilities Mgmt", payment_delays_days=38, category="Facilities"),
            Vendor(vendor_id=10, vendor_name="BluePeak Consulting", payment_delays_days=27, category="Consulting"),
        ]
        session.add_all(vendors)

        invoices = [
            Invoice(invoice_id=101, customer_id=1, amount=650000.0, status="UNPAID", due_date=datetime.date(2026, 2, 10), invoice_date=datetime.date(2025, 11, 15), fiscal_period_id=1),
            Invoice(invoice_id=102, customer_id=2, amount=120000.0, status="PAID", due_date=datetime.date(2026, 3, 20), invoice_date=datetime.date(2025, 12, 1), fiscal_period_id=1),
            Invoice(invoice_id=103, customer_id=3, amount=720000.0, status="UNPAID", due_date=datetime.date(2026, 1, 15), invoice_date=datetime.date(2025, 10, 20), fiscal_period_id=1),
            Invoice(invoice_id=104, customer_id=5, amount=580000.0, status="UNPAID", due_date=datetime.date(2026, 4, 1), invoice_date=datetime.date(2025, 11, 28), fiscal_period_id=1),
            Invoice(invoice_id=105, customer_id=1, amount=950000.0, status="UNPAID", due_date=datetime.date(2026, 5, 10), invoice_date=datetime.date(2026, 1, 5), fiscal_period_id=2),
            Invoice(invoice_id=106, customer_id=4, amount=210000.0, status="PAID", due_date=datetime.date(2026, 2, 1), invoice_date=datetime.date(2026, 2, 10), fiscal_period_id=2),
        ]
        session.add_all(invoices)

        session.add_all(
            [
                InvoiceLineItem(line_id=1, invoice_id=101, description="Enterprise license renewal", line_amount=650000.0),
                InvoiceLineItem(line_id=2, invoice_id=103, description="Professional services", line_amount=720000.0),
                InvoiceLineItem(line_id=3, invoice_id=105, description="Infrastructure rollout", line_amount=950000.0),
            ]
        )

        session.add(
            Payment(payment_id=1, invoice_id=102, amount=120000.0, payment_date=datetime.date(2026, 3, 18))
        )

        vendor_payments = [
            VendorPayment(vendor_payment_id=1, vendor_id=1, amount=200000.0, payment_date=datetime.date(2025, 12, 1), delay_days=45),
            VendorPayment(vendor_payment_id=2, vendor_id=2, amount=150000.0, payment_date=datetime.date(2026, 1, 10), delay_days=12),
            VendorPayment(vendor_payment_id=3, vendor_id=3, amount=90000.0, payment_date=datetime.date(2026, 1, 20), delay_days=31),
            VendorPayment(vendor_payment_id=4, vendor_id=6, amount=500000.0, payment_date=datetime.date(2025, 11, 5), delay_days=55),
            VendorPayment(vendor_payment_id=5, vendor_id=4, amount=75000.0, payment_date=datetime.date(2026, 2, 1), delay_days=22),
            VendorPayment(vendor_payment_id=6, vendor_id=7, amount=40000.0, payment_date=datetime.date(2026, 2, 15), delay_days=18),
            VendorPayment(vendor_payment_id=7, vendor_id=8, amount=120000.0, payment_date=datetime.date(2026, 1, 5), delay_days=5),
            VendorPayment(vendor_payment_id=8, vendor_id=9, amount=180000.0, payment_date=datetime.date(2025, 12, 20), delay_days=38),
            VendorPayment(vendor_payment_id=9, vendor_id=10, amount=95000.0, payment_date=datetime.date(2026, 2, 28), delay_days=27),
            VendorPayment(vendor_payment_id=10, vendor_id=5, amount=30000.0, payment_date=datetime.date(2026, 3, 1), delay_days=8),
        ]
        session.add_all(vendor_payments)

        session.add_all(
            [
                PurchaseOrder(po_id=1, vendor_id=1, amount=250000.0, status="OPEN", order_date=datetime.date(2026, 1, 1)),
                PurchaseOrder(po_id=2, vendor_id=6, amount=800000.0, status="CLOSED", order_date=datetime.date(2025, 9, 1)),
            ]
        )

        session.add_all(
            [
                AccountsReceivable(ar_id=1, customer_id=1, balance=1250000.0, as_of_date=datetime.date(2026, 6, 1)),
                AccountsReceivable(ar_id=2, customer_id=3, balance=890000.0, as_of_date=datetime.date(2026, 6, 1)),
                AccountsReceivable(ar_id=3, customer_id=5, balance=2100000.0, as_of_date=datetime.date(2026, 6, 1)),
            ]
        )
        session.add_all(
            [
                AccountsPayable(ap_id=1, vendor_id=1, balance=180000.0, as_of_date=datetime.date(2026, 6, 1)),
                AccountsPayable(ap_id=2, vendor_id=6, balance=420000.0, as_of_date=datetime.date(2026, 6, 1)),
            ]
        )

        session.add_all(
            [
                Department(department_id=1, department_name="Finance"),
                Department(department_id=2, department_name="Engineering"),
                Department(department_id=3, department_name="Sales"),
            ]
        )
        session.add_all(
            [
                Employee(employee_id=1, full_name="Priya Sharma", department_id=1),
                Employee(employee_id=2, full_name="Rahul Mehta", department_id=2),
                Employee(employee_id=3, full_name="Anita Desai", department_id=3),
            ]
        )
        session.add(
            Contract(
                contract_id=1,
                party_type="CUSTOMER",
                party_id=1,
                contract_value=5000000.0,
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2027, 12, 31),
            )
        )

        await session.commit()
