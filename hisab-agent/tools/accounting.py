from fastmcp import FastMCP
from pydantic import BaseModel, Field

router = FastMCP(name="accounting")


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


@router.tool()
def calculate_totals(
    items: list[LineItem],
    tax_rate: float = Field(default=0.15, description="Tax rate as a decimal, e.g. 0.15 for 15%"),
    discount_percent: float = Field(default=0.0, description="Discount percentage, e.g. 10 for 10%"),
) -> dict:
    """Calculate subtotal, discount, tax, and grand total for a list of line items."""
    subtotal = sum(item.quantity * item.unit_price for item in items)
    discount_amount = subtotal * (discount_percent / 100)
    taxable = subtotal - discount_amount
    tax_amount = taxable * tax_rate
    total = taxable + tax_amount
    return {
        "subtotal": round(subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "taxable_amount": round(taxable, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
    }


@router.tool()
def calculate_profit_loss(
    revenue: float,
    cogs: float = Field(description="Cost of goods sold"),
    operating_expenses: float = 0.0,
) -> dict:
    """Calculate gross profit, operating profit, and profit margins."""
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue * 100) if revenue else 0
    operating_profit = gross_profit - operating_expenses
    net_margin = (operating_profit / revenue * 100) if revenue else 0
    return {
        "revenue": round(revenue, 2),
        "cogs": round(cogs, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_margin_percent": round(gross_margin, 2),
        "operating_expenses": round(operating_expenses, 2),
        "operating_profit": round(operating_profit, 2),
        "net_margin_percent": round(net_margin, 2),
    }


@router.tool()
def calculate_break_even(
    fixed_costs: float,
    price_per_unit: float,
    variable_cost_per_unit: float,
) -> dict:
    """Calculate the break-even point in units and revenue."""
    contribution_margin = price_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        return {"error": "Price per unit must exceed variable cost per unit."}
    break_even_units = fixed_costs / contribution_margin
    break_even_revenue = break_even_units * price_per_unit
    return {
        "contribution_margin_per_unit": round(contribution_margin, 2),
        "break_even_units": round(break_even_units, 2),
        "break_even_revenue": round(break_even_revenue, 2),
    }


@router.tool()
def calculate_depreciation(
    asset_cost: float,
    salvage_value: float,
    useful_life_years: int,
    method: str = Field(default="straight_line", description="'straight_line' or 'declining_balance'"),
) -> dict:
    """Calculate annual depreciation using straight-line or declining-balance method."""
    if method == "straight_line":
        annual = (asset_cost - salvage_value) / useful_life_years
        schedule = [round(annual, 2)] * useful_life_years
    elif method == "declining_balance":
        rate = 2 / useful_life_years  # double-declining
        book_value = asset_cost
        schedule = []
        for _ in range(useful_life_years):
            dep = min(book_value - salvage_value, book_value * rate)
            dep = max(dep, 0)
            schedule.append(round(dep, 2))
            book_value -= dep
    else:
        return {"error": f"Unknown method '{method}'. Use 'straight_line' or 'declining_balance'."}
    return {
        "method": method,
        "asset_cost": asset_cost,
        "salvage_value": salvage_value,
        "useful_life_years": useful_life_years,
        "annual_schedule": schedule,
        "total_depreciation": round(sum(schedule), 2),
    }
