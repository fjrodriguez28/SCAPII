# app/api/v1/endpoints/transfer.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.schemas.transfer import TransferRequest
from app.schemas.task import TransferTaskResponse
from app.schemas.test import DatabaseTestRequest
from app.tasks.transfer_tasks import start_transfer
from app.core.celery import celery_app
from app.models.task import TaskStatus
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from app.core.database import get_db
from datetime import datetime
import re
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
router = APIRouter(tags=["proceso_51"])

@router.post("/transfer", response_model=TransferTaskResponse, status_code=202)
async def create_transfer_task(
    request: TransferRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Validación básica
    if not request.tables:
        raise HTTPException(status_code=400, detail="Debe especificar al menos una tabla")
    
    # Crear registro en base de datos
    task_record = TaskStatus(
        status="PENDING",
        request_config=request.model_dump(),
        created_at=datetime.now()
    )
    db.add(task_record)
    db.commit()
    db.refresh(task_record)
    
    # Iniciar tarea asíncrona con Celery
    try:
        celery_task = start_transfer.delay(request.dict(), task_record.id)
    except Exception as e:
        db.delete(task_record)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando tarea Celery: {str(e)}"
        )
    
    # Actualizar registro con ID de Celery
    task_record.celery_task_id = celery_task.id
    db.commit()
    
    return TransferTaskResponse(
        task_id=celery_task.id,
        status="PENDING",
        monitor_url=f"/api/v1/tasks/{celery_task.id}",
        details={
            "tables_count": len(request.tables),
            "tables": [t.source_table for t in request.tables],
            "chunk_size": request.chunk_size,
            "db_task_id": task_record.id
        },
        created_at=datetime.now()
    )

from app.core.database import SessionLocal, create_db_engine,create_temp_engine, get_db
def create_temp_engine2(config: dict):
    """Crea un motor temporal usando SQLAlchemy"""
    conn_str = (
        f"mssql+pyodbc://{config['username']}:{config['password']}"
        f"@{config['server']}:{config['port']}/{config['database']}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    return create_engine(conn_str, pool_pre_ping=True, connect_args={
        "timeout": 10,
        "login_timeout": 5
    })

@router.post("/test-connection-sqlalchemy")
async def test_db_connection_sqlalchemy(request: DatabaseTestRequest):
    """Endpoint para probar conexión usando SQLAlchemy con consulta personalizada"""
    try:
        # Crear motor temporal
        engine = create_db_engine(request.model_dump())
        
        # Usar la consulta de prueba del request
        test_query = request.test_query
        
        # Probar conexión directamente con el motor
        with engine.connect() as connection:
            result = connection.execute(text(test_query))
            
            # Si la consulta devuelve resultados, los tomamos
            if result.returns_rows:
                rows = result.fetchall()
                columns = result.keys()
                
                # Convertir resultados a formato JSON
                result_data = [
                    {column: value for column, value in zip(columns, row)}
                    for row in rows
                ]
            else:
                result_data = {"message": "Query executed successfully"}
        
        return {
            "success": True,
            "message": "Conexión exitosa",
            "query": test_query,
            "result": result_data
        }
    except (SQLAlchemyError, DBAPIError) as e:
        error_info = parse_sqlalchemy_error(e)
        raise HTTPException(status_code=400, detail=error_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "message": f"Error inesperado: {str(e)}",
            "type": "unexpected_error"
        })

def parse_sqlalchemy_error(e: Exception) -> Dict[str, Any]:
    """Analiza errores de SQLAlchemy para dar información detallada"""
    try:
        if isinstance(e, DBAPIError):
            orig_error = e.orig
            error_info = {
                "success": False,
                "message": str(orig_error),
                "type": "DBAPIError",
                "code": getattr(orig_error, 'args', [None])[0],
                "sqlstate": getattr(orig_error, 'args', [None, None])[1]
            }
        else:
            error_info = {
                "success": False,
                "message": str(e),
                "type": type(e).__name__
            }
        
        # Detectar errores comunes
        message = error_info["message"].lower()
        if "invalid column name" in message:
            error_info["diagnosis"] = "Columna inválida en la consulta"
        elif "invalid object name" in message:
            error_info["diagnosis"] = "Tabla o vista no encontrada"
        elif "incorrect syntax" in message:
            error_info["diagnosis"] = "Error de sintaxis SQL"
        elif "permission denied" in message:
            error_info["diagnosis"] = "Permisos insuficientes"
        elif "adaptive server is unavailable" in message:
            error_info["diagnosis"] = "El servidor no está disponible"
        elif "login failed" in message:
            error_info["diagnosis"] = "Credenciales inválidas"
        elif "could not open a connection" in message:
            error_info["diagnosis"] = "Problemas de red o firewall"
        elif "odbc driver" in message:
            error_info["diagnosis"] = "Driver ODBC no instalado"
        elif "connection string" in message:
            error_info["diagnosis"] = "Cadena de conexión inválida"
        
        # Detectar errores específicos de MSSQL
        if "18456" in error_info.get("code", ""):
            error_info["diagnosis"] = "Error de autenticación"
            state_match = re.search(r"State: (\d+)", error_info["message"])
            if state_match:
                error_info["diagnosis"] += f" (Estado: {state_match.group(1)})"
        
        return error_info
    except Exception as parse_error:
        return {
            "success": False,
            "message": f"Error original: {str(e)} | Error en parseo: {str(parse_error)}",
            "type": "parse_error"
        }