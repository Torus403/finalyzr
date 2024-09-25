from fastapi import APIRouter

from app.api.routes import login, users, portfolios, trades, cash_actions

api_router = APIRouter()

# User routes
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(trades.router, prefix="/portfolio/{portfolio_id}/trades", tags=["trades"])
api_router.include_router(cash_actions.router, prefix="/portfolio/{portfolio_id}/cash_actions", tags=["cash actions"])

# Superuser routes
api_router.include_router(login.superuser_router, prefix="/admin", tags=["admin"])
api_router.include_router(users.superuser_router, prefix="/admin/users", tags=["admin"])
