# app/api/v1/router.py
from fastapi import APIRouter
from .modules import gusuarios_router, gaaduanal_router, spartes_router

api_router = APIRouter()
api_router.include_router(gaaduanal_router, prefix="/gaaduanal", tags=["GAAduanal"])
api_router.include_router(gusuarios_router, prefix="/gusuarios", tags=["GUsuarios"])
api_router.include_router(spartes_router, prefix="/spartes", tags=["SPartes"])