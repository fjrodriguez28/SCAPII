from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.core.database import engine
from app.utils.responses import standard_response
from app.api.v1.router import api_router

app = FastAPI(title="API con FastAPI y SQL Server", version="1.0.0")

# Incluir el router principal de la API v1
app.include_router(api_router, prefix="/api/v1")