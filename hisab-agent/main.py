from fastmcp import FastMCP
from tools.accounting import router as accounting_router
from tools.invoices import router as invoices_router
from tools.reports import router as reports_router
from tools.school_cost_study import router as school_router

mcp = FastMCP(
    name="hisab-agent",
    instructions=(
        "You are Hisab, a financial accounting assistant. "
        "You help with invoices, expense tracking, profit/loss calculations, "
        "tax computation, and financial reports."
    ),
)

mcp.mount(accounting_router, namespace="accounting")
mcp.mount(invoices_router, namespace="invoices")
mcp.mount(reports_router, namespace="reports")
mcp.mount(school_router, namespace="school")

if __name__ == "__main__":
    mcp.run()
