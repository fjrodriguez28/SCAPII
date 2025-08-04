# app/api/v1/endpoints/monitor.py
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.core.celery import celery_app
from app.schemas.task import TaskStatusResponse
from app.core.database import SessionLocal
from app.models.task import TaskStatus

router = APIRouter()

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    # Obtener estado de Celery
    celery_task = AsyncResult(task_id, app=celery_app)
    
    # Obtener estado de base de datos
    db = SessionLocal()
    try:
        task_record = db.query(TaskStatus).filter(TaskStatus.celery_task_id == task_id).first()
        if not task_record:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        
        # Construir respuesta combinada
        response = {
            "task_id": task_id,
            "status": celery_task.status,
            "start_time": task_record.start_time,
            "end_time": task_record.end_time,
            "duration": task_record.duration,
            "warnings": task_record.warnings or []
        }
        
        if celery_task.status == "PROGRESS":
            # Usar datos en vivo de Celery
            progress_data = celery_task.result
            response.update({
                "progress": progress_data.get("progress"),
                "table_status": progress_data.get("stats", {}).get("table_details", {})
            })
        elif celery_task.status == "SUCCESS":
            # Usar datos finales de la base de datos
            response.update({
                "progress": 100,
                "result": task_record.result,
                "table_status": task_record.result.get("table_details", {}) if task_record.result else {}
            })
        elif celery_task.status == "FAILURE":
            response.update({
                "error": str(celery_task.result),
                "table_status": task_record.errors
            })
        
        return response
    finally:
        db.close()