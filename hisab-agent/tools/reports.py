from fastmcp import FastMCP
from pydantic import BaseModel

router = FastMCP(name="reports")


class Transaction(BaseModel):
    description: str
    amount: float
    category: str
    type: str  # "income" or "expense"


@router.tool()
def generate_summary_report(transactions: list[Transaction]) -> dict:
    """Generate a financial summary report: totals by category, net income, and top categories."""
    total_income = 0.0
    total_expenses = 0.0
    by_category: dict[str, float] = {}

    for tx in transactions:
        if tx.type == "income":
            total_income += tx.amount
        else:
            total_expenses += tx.amount
        by_category[tx.category] = by_category.get(tx.category, 0.0) + tx.amount

    net = total_income - total_expenses
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_income": round(net, 2),
        "profitable": net >= 0,
        "transaction_count": len(transactions),
        "categories": {k: round(v, 2) for k, v in sorted_cats},
        "top_category": sorted_cats[0][0] if sorted_cats else None,
    }


@router.tool()
def calculate_budget_variance(
    budget: dict[str, float],
    actual: dict[str, float],
) -> dict:
    """Compare budgeted vs actual spending per category and flag over-budget items."""
    results = {}
    total_budget = 0.0
    total_actual = 0.0

    all_categories = set(budget) | set(actual)
    for cat in all_categories:
        b = budget.get(cat, 0.0)
        a = actual.get(cat, 0.0)
        variance = a - b
        pct = (variance / b * 100) if b else None
        results[cat] = {
            "budget": round(b, 2),
            "actual": round(a, 2),
            "variance": round(variance, 2),
            "variance_percent": round(pct, 1) if pct is not None else None,
            "over_budget": variance > 0,
        }
        total_budget += b
        total_actual += a

    return {
        "categories": results,
        "total_budget": round(total_budget, 2),
        "total_actual": round(total_actual, 2),
        "total_variance": round(total_actual - total_budget, 2),
        "over_budget_categories": [c for c, v in results.items() if v["over_budget"]],
    }


@router.tool()
def calculate_financial_ratios(
    current_assets: float,
    current_liabilities: float,
    total_assets: float,
    total_liabilities: float,
    net_income: float,
    revenue: float,
    equity: float,
) -> dict:
    """Calculate key financial ratios: liquidity, solvency, and profitability."""
    current_ratio = current_assets / current_liabilities if current_liabilities else None
    debt_ratio = total_liabilities / total_assets if total_assets else None
    roe = net_income / equity * 100 if equity else None
    roa = net_income / total_assets * 100 if total_assets else None
    net_margin = net_income / revenue * 100 if revenue else None

    def fmt(v):
        return round(v, 4) if v is not None else None

    return {
        "liquidity": {
            "current_ratio": fmt(current_ratio),
            "note": "≥ 2 is healthy; < 1 means more short-term debt than assets",
        },
        "solvency": {
            "debt_ratio": fmt(debt_ratio),
            "note": "< 0.5 is conservative; > 1 means insolvent",
        },
        "profitability": {
            "return_on_equity_percent": fmt(roe),
            "return_on_assets_percent": fmt(roa),
            "net_profit_margin_percent": fmt(net_margin),
        },
    }
