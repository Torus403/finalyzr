from fastapi import APIRouter

from app.api.routes import login
from app.api.routes import users
from app.api.routes import portfolios

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
# api_router.include_router(login.superuser_router, prefix="/admin", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(users.superuser_router, prefix="/admin/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
