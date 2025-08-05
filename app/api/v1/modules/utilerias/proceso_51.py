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
from app.core.database import get_db, create_unified_engine, test_connection, parse_sqlalchemy_error
from datetime import datetime
import re
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["proceso_51"])

@router.post("/transfer", response_model=TransferTaskResponse, status_code=202)
async def create_transfer_task(
    request: TransferRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crear tarea de transferencia con validación previa de conexiones"""
    
    # Validación básica
    if not request.tables:
        raise HTTPException(status_code=400, detail="Debe especificar al menos una tabla")
    
    # Validar conexiones antes de crear la tarea
    logger.info("Validando conexiones antes de crear tarea...")
    
    # Probar conexión origen
    source_test = test_connection(request.source.model_dump())
    if not source_test["success"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Error conectando a base de datos origen",
                "error": source_test["error"],
                "server": source_test["server"]
            }
        )
    
    # Probar conexión destino
    target_test = test_connection(request.target.model_dump())
    if not target_test["success"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Error conectando a base de datos destino", 
                "error": target_test["error"],
                "server": target_test["server"]
            }
        )
    
    logger.info("Conexiones validadas exitosamente")
    
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
        celery_task = start_transfer.delay(request.model_dump(), task_record.id)
        logger.info(f"Tarea Celery creada: {celery_task.id}")
    except Exception as e:
        logger.error(f"Error iniciando tarea Celery: {str(e)}")
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
            "db_task_id": task_record.id,
            "source_server": f"{request.source.server}:{request.source.port}",
            "target_server": f"{request.target.server}:{request.target.port}"
        },
        created_at=datetime.now()
    )

@router.post("/test-connection")
async def test_database_connection(request: DatabaseTestRequest):
    """Endpoint mejorado para probar conexión usando la función unificada"""
    try:
        logger.info(f"Probando conexión a {request.server}:{request.port}/{request.database}")
        
        # Usar función unificada para crear engine
        engine = create_unified_engine(request.model_dump())
        
        # Probar con la consulta personalizada
        test_query = request.test_query
        
        # Ejecutar consulta con timeout
        with engine.connect() as connection:
            result = connection.execute(text(test_query))
            
            # Procesar resultados
            if result.returns_rows:
                rows = result.fetchall()
                columns = list(result.keys())
                
                # Convertir a formato JSON (limitar resultados para evitar respuestas muy grandes)
                result_data = [
                    {column: value for column, value in zip(columns, row)}
                    for row in rows[:100]  # Limitar a 100 filas
                ]
                
                if len(rows) > 100:
                    result_data.append({"_note": f"Se muestran las primeras 100 filas de {len(rows)} total"})
            else:
                result_data = {"message": "Query executed successfully", "rows_affected": result.rowcount}
        
        # Limpiar recursos
        engine.dispose()
        
        return {
            "success": True,
            "message": "Conexión exitosa",
            "server": f"{request.server}:{request.port}",
            "database": request.database,
            "query": test_query,
            "result": result_data,
            "connection_test": "PASSED"
        }
        
    except (SQLAlchemyError, DBAPIError) as e:
        error_info = parse_sqlalchemy_error(e)
        logger.error(f"Error de conexión SQL: {error_info}")
        raise HTTPException(status_code=400, detail=error_info)
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "message": f"Error inesperado: {str(e)}",
            "type": "unexpected_error",
            "connection_test": "FAILED"
        })

@router.post("/validate-transfer-config")
async def validate_transfer_config(request: TransferRequest):
    """Validar configuración de transferencia sin ejecutarla"""
    try:
        validation_results = {
            "valid": True,
            "source_connection": None,
            "target_connection": None,
            "tables_validation": [],
            "warnings": [],
            "errors": []
        }
        
        # Validar conexión origen
        source_test = test_connection(request.source.model_dump())
        validation_results["source_connection"] = source_test
        if not source_test["success"]:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Conexión origen falló: {source_test['error']['message']}")
        
        # Validar conexión destino
        target_test = test_connection(request.target.model_dump())
        validation_results["target_connection"] = target_test
        if not target_test["success"]:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Conexión destino falló: {target_test['error']['message']}")
        
        # Si las conexiones funcionan, validar tablas
        if source_test["success"] and target_test["success"]:
            source_engine = create_unified_engine(request.source.model_dump())
            target_engine = create_unified_engine(request.target.model_dump())
            
            try:
                for table_config in request.tables:
                    table_validation = {
                        "table": table_config.source_table,
                        "exists_in_source": False,
                        "exists_in_target": False,
                        "estimated_rows": 0,
                        "warnings": []
                    }
                    
                    # Verificar existencia en origen
                    try:
                        with source_engine.connect() as conn:
                            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_config.source_table}"))
                            table_validation["estimated_rows"] = result.scalar()
                            table_validation["exists_in_source"] = True
                    except Exception as e:
                        table_validation["warnings"].append(f"Error verificando tabla origen: {str(e)}")
                    
                    # Verificar existencia en destino
                    target_table = table_config.target_table or table_config.source_table
                    try:
                        with target_engine.connect() as conn:
                            conn.execute(text(f"SELECT TOP 1 * FROM {target_table}"))
                            table_validation["exists_in_target"] = True
                    except Exception as e:
                        table_validation["warnings"].append(f"Tabla destino podría no existir: {str(e)}")
                    
                    validation_results["tables_validation"].append(table_validation)
                
            finally:
                source_engine.dispose()
                target_engine.dispose()
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error en validación: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "valid": False,
            "error": f"Error durante validación: {str(e)}"
        })

@router.get("/connection-diagnostics")
async def connection_diagnostics():
    """Endpoint para diagnosticar problemas de conectividad"""
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {},
        "network_tests": {},
        "recommendations": []
    }
    
    try:
        import platform
        import socket
        
        # Información del sistema
        diagnostics["system_info"] = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname(),
            "container_check": "Docker container detected" if "/.dockerenv" in str(platform.platform()) else "Native environment"
        }
        
        # Pruebas de red básicas
        try:
            # Probar conectividad a puertos comunes de SQL Server
            common_ports = [1433, 1434]
            for port in common_ports:
                try:
                    sock = socket.create_connection(("host.docker.internal", port), timeout=5)
                    sock.close()
                    diagnostics["network_tests"][f"port_{port}"] = "OPEN"
                except:
                    diagnostics["network_tests"][f"port_{port}"] = "CLOSED/FILTERED"
        except Exception as e:
            diagnostics["network_tests"]["error"] = str(e)
        
        # Recomendaciones
        diagnostics["recommendations"] = [
            "Verificar que SQL Server esté configurado para aceptar conexiones TCP/IP",
            "Confirmar que el puerto 1433 esté abierto en el firewall",
            "Validar que las credenciales sean correctas",
            "Comprobar la configuración de red del contenedor Docker"
        ]
        
        return diagnostics
        
    except Exception as e:
        return {
            "error": f"Error generando diagnósticos: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }