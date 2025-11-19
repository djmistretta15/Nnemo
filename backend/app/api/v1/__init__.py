"""
API v1 package - REST API endpoints.
"""

from fastapi import APIRouter
from app.api.v1 import auth, nodes, telemetry, model_profiles, placement, public

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(nodes.router)
api_router.include_router(telemetry.router)
api_router.include_router(model_profiles.router)
api_router.include_router(placement.router)
api_router.include_router(public.router)
