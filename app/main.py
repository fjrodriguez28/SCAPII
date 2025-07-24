from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.core.database import engine
from app.utils.helpers import standard_response
from app.api.v1.router import api_router

app = FastAPI(title="API con FastAPI y SQL Server", version="1.0.0")

@app.get("/ping", tags=["Test"])
def ping():
    """Endpoint de prueba para verificar que la API está activa."""
    return standard_response(message="pong")

@app.get("/version", tags=["DB"])
def get_sql_version():
    """Devuelve la versión de SQL Server conectada."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION AS version"))
            version = result.scalar()
            return standard_response(data={"sql_server_version": version})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Incluir el router principal de la API v1
app.include_router(api_router, prefix="/api/v1")