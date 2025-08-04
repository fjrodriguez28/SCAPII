from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List, Optional

class TransferTaskResponse(BaseModel):
    task_id: str = Field(..., description="ID único de la tarea Celery")
    status: str = Field(..., description="Estado inicial de la tarea")
    monitor_url: str = Field(..., description="URL para monitorear el progreso")
    details: Dict[str, Any] = Field(..., description="Detalles adicionales de la tarea")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha/hora de creación")
    
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str = Field(..., description="Estado actual (PENDING, PROGRESS, SUCCESS, FAILURE)")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Porcentaje de completado")
    table_status: Dict[str, Dict[str, Any]] = Field({}, description="Estado por tabla")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado final cuando está completo")
    error: Optional[str] = Field(None, description="Mensaje de error si falló")
    start_time: Optional[datetime] = Field(None, description="Hora de inicio de procesamiento")
    end_time: Optional[datetime] = Field(None, description="Hora de finalización")
    duration: Optional[float] = Field(None, description="Duración en segundos")
    warnings: List[str] = Field([], description="Advertencias durante el proceso")