import uuid
from datetime import date, timedelta
from fastmcp import FastMCP
from pydantic import BaseModel, Field

router = FastMCP(name="invoices")


class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


@router.tool()
def generate_invoice(
    client_name: str,
    items: list[InvoiceItem],
    tax_rate: float = Field(default=0.15, description="Tax rate as a decimal"),
    payment_due_days: int = Field(default=30, description="Days until payment is due"),
    currency: str = "SAR",
    notes: str = "",
) -> dict:
    """Generate a structured invoice with all totals, due date, and a unique invoice number."""
    invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
    issue_date = date.today()
    due_date = issue_date + timedelta(days=payment_due_days)

    line_items = []
    subtotal = 0.0
    for item in items:
        line_total = round(item.quantity * item.unit_price, 2)
        subtotal += line_total
        line_items.append({
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": line_total,
        })

    tax_amount = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax_amount, 2)

    return {
        "invoice_number": invoice_number,
        "client": client_name,
        "issue_date": issue_date.isoformat(),
        "due_date": due_date.isoformat(),
        "currency": currency,
        "line_items": line_items,
        "subtotal": round(subtotal, 2),
        "tax_rate_percent": tax_rate * 100,
        "tax_amount": tax_amount,
        "total": total,
        "notes": notes,
        "status": "unpaid",
    }


@router.tool()
def calculate_overdue_penalty(
    invoice_total: float,
    due_date: str = Field(description="Due date in YYYY-MM-DD format"),
    penalty_rate_per_day: float = Field(default=0.001, description="Daily penalty rate, e.g. 0.001 = 0.1%"),
) -> dict:
    """Calculate the late payment penalty for an overdue invoice."""
    due = date.fromisoformat(due_date)
    today = date.today()
    if today <= due:
        return {"overdue": False, "days_overdue": 0, "penalty": 0.0, "total_due": invoice_total}
    days_overdue = (today - due).days
    penalty = round(invoice_total * penalty_rate_per_day * days_overdue, 2)
    return {
        "overdue": True,
        "days_overdue": days_overdue,
        "daily_penalty_rate_percent": penalty_rate_per_day * 100,
        "penalty": penalty,
        "original_total": invoice_total,
        "total_due": round(invoice_total + penalty, 2),
    }
