import datetime

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    outstanding_balance = Column(Float, default=0.0)
    region = Column(String(50))
    created_at = Column(Date)


class Vendor(Base):
    __tablename__ = "vendors"
    vendor_id = Column(Integer, primary_key=True)
    vendor_name = Column(String(255), nullable=False)
    payment_delays_days = Column(Integer, default=0)
    category = Column(String(100))


class FiscalPeriod(Base):
    __tablename__ = "fiscal_periods"
    fiscal_period_id = Column(Integer, primary_key=True)
    period_name = Column(String(50))
    quarter = Column(Integer)
    year = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)


class Invoice(Base):
    __tablename__ = "invoices"
    invoice_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="UNPAID")
    due_date = Column(Date)
    invoice_date = Column(Date)
    fiscal_period_id = Column(Integer, ForeignKey("fiscal_periods.fiscal_period_id"))


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    line_id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"))
    description = Column(String(500))
    line_amount = Column(Float)


class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"))
    amount = Column(Float)
    payment_date = Column(Date)


class VendorPayment(Base):
    __tablename__ = "vendor_payments"
    vendor_payment_id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    amount = Column(Float)
    payment_date = Column(Date)
    delay_days = Column(Integer)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    po_id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    amount = Column(Float)
    status = Column(String(30))
    order_date = Column(Date)


class AccountsReceivable(Base):
    __tablename__ = "accounts_receivable"
    ar_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    balance = Column(Float)
    as_of_date = Column(Date, default=datetime.date.today)


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"
    ap_id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    balance = Column(Float)
    as_of_date = Column(Date, default=datetime.date.today)


class Department(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String(100))


class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True)
    full_name = Column(String(150))
    department_id = Column(Integer, ForeignKey("departments.department_id"))


class Contract(Base):
    __tablename__ = "contracts"
    contract_id = Column(Integer, primary_key=True)
    party_type = Column(String(20))
    party_id = Column(Integer)
    contract_value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
