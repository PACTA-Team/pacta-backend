"""
API v1 router - includes all endpoints
"""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, users

router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(auth.router)
router.include_router(users.router)
