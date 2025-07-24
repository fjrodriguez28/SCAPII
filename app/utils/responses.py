from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

# Schema para respuesta estándar
class StandardResponse(BaseModel):
    success: bool
    generatedAt: Optional[str] = None
    message: str
    data: Optional[Any] = None
    hasMore: Optional[int] = None
    totalRecords: Optional[int] = None

# Modelos de respuesta para documentación en Swagger
class BaseResponse(BaseModel):
    success: bool
    generatedAt: str
    message: str

class DataResponse(BaseResponse):
    """Respuesta con datos simples"""
    data: Optional[Any] = None

class PaginatedResponse(BaseResponse):
    """Respuesta paginada con datos"""
    data: List[Any]
    hasMore: int
    totalRecords: int

class ErrorResponse(BaseResponse):
    """Respuesta de error"""
    success: bool = False

class CreateResponse(BaseResponse):
    """Respuesta de creación exitosa"""
    data: Optional[Any] = None
    success: bool = True

class UpdateResponse(BaseResponse):
    """Respuesta de actualización exitosa"""
    data: Optional[Any] = None
    success: bool = True

class DeleteResponse(BaseResponse):
    """Respuesta de eliminación exitosa"""
    data: Optional[Any] = None
    success: bool = True

def standard_response(data: Optional[Any] = None, message: str = "OK", success: bool = True, hasMore: Optional[int] = None, totalRecords: Optional[int] = None, generatedAt: Optional[datetime] = None) -> dict:
    """
    Función para crear respuestas estándar de la API
    
    Args:
        data: Datos a devolver (opcional)
        message: Mensaje descriptivo
        success: Indica si la operación fue exitosa
        hasMore: Indica si hay más registros disponibles
        totalRecords: Total de registros encontrados
        generatedAt: Timestamp de generación (se auto-genera si es None)
    
    Returns:
        dict: Respuesta estándar con formato consistente
    """
    if generatedAt is None:
        generatedAt = datetime.now()
    
    response = {
        "success": success,
        "generatedAt": generatedAt.isoformat(),
        "message": message
    }
    
    # Solo agregar campos opcionales si no son None
    if data is not None:
        # Si data es un objeto SQLAlchemy, convertirlo a dict
        if hasattr(data, '__dict__') and hasattr(data, '__table__'):
            # Es un modelo SQLAlchemy, convertir a dict
            from sqlalchemy.inspection import inspect
            mapper = inspect(data.__class__)
            data_dict = {}
            for column in mapper.columns:
                data_dict[column.key] = getattr(data, column.key)
            response["data"] = data_dict
        elif isinstance(data, list) and data and hasattr(data[0], '__dict__') and hasattr(data[0], '__table__'):
            # Es una lista de modelos SQLAlchemy
            from sqlalchemy.inspection import inspect
            data_list = []
            for item in data:
                mapper = inspect(item.__class__)
                item_dict = {}
                for column in mapper.columns:
                    item_dict[column.key] = getattr(item, column.key)
                data_list.append(item_dict)
            response["data"] = data_list
        else:
            response["data"] = data
    
    if hasMore is not None:
        response["hasMore"] = hasMore
        
    if totalRecords is not None:
        response["totalRecords"] = totalRecords
    
    return response

# Funciones helper adicionales
def success_response(data: Optional[Any] = None, message: str = "Operación exitosa"):
    return standard_response(data=data, message=message, success=True)

def error_response(message: str = "Error en la operación", data: Optional[Any] = None):
    return standard_response(data=data, message=message, success=False)

# Función específica para respuestas paginadas
def paginated_response(data: Any, total_records: int, has_more: bool = False, message: str = "Datos obtenidos exitosamente"):
    return standard_response(
        data=data, 
        message=message, 
        hasMore=1 if has_more else 0,
        totalRecords=total_records
    )