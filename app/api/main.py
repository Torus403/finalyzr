from fastapi import APIRouter

from app.api.routes import login, users, portfolios, trades, cash_actions
from app.api.routes.metrics import overview, positions

api_router = APIRouter()

# User routes
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(
    trades.router, prefix="/portfolios/{portfolio_id}/trades", tags=["trades"]
)
api_router.include_router(
    cash_actions.router,
    prefix="/portfolios/{portfolio_id}/cash_actions",
    tags=["cash actions"],
)
api_router.include_router(
    overview.router,
    prefix="/portfolios/{portfolio_id}/metrics/overview",
    tags=["metrics"],
)
api_router.include_router(
    positions.router,
    prefix="/portfolios/{portfolio_id}/metrics/positions",
    tags=["metrics"],
)

# Superuser routes
api_router.include_router(login.superuser_router, prefix="/admin", tags=["admin"])
api_router.include_router(users.superuser_router, prefix="/admin/users", tags=["admin"])
