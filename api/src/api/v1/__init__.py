"""
API v1 router - includes all endpoints
"""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, users, clients, suppliers, signatories, contracts, supplements

router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(clients.router)
router.include_router(suppliers.router)
router.include_router(signatories.router)
router.include_router(contracts.router)
router.include_router(supplements.router)

