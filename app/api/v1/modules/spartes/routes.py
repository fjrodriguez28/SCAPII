from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from .service import spartes_service
from .schemas import SPartes, SPartesCreate, SPartesUpdate
from .enmus import SPartesOrderBy
from app.utils.responses import (
    paginated_response, success_response, error_response,
    PaginatedResponse, CreateResponse, UpdateResponse, DeleteResponse, ErrorResponse
)

router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Obtener números de parte",
    description="Obtiene una lista paginada de números de parte con filtros opcionales",
    responses={
        200: {"model": PaginatedResponse, "description": "Lista de partes obtenida exitosamente"},
        404: {"model": ErrorResponse, "description": "Parte no encontrada"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
def read_numparte(
    skip: int = 0,
    limit: int = 100,
    order_by: SPartesOrderBy = SPartesOrderBy.NUMPARTE,
    numero_parte: str = None,  # Parámetro opcional para buscar parte específico
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """Obtener numeros de parte con filtros opcionales"""
    try:
        partes = spartes_service.get(
            db, 
            numero_parte=numero_parte,
            skip=skip, 
            limit=limit, 
            order_by=order_by.value,
        )
        
        if numero_parte and not partes:
            response.status_code = status.HTTP_404_NOT_FOUND
            return error_response(message="Parte no encontrada")
        
        # Obtener el total de registros para paginación
        total_count = spartes_service.count_all(db, numero_parte=numero_parte)
        has_more = (skip + limit) < total_count
        
        # Convertir datos a esquemas Pydantic
        partes_schema = [SPartes.model_validate(parte) for parte in partes]
        
        return paginated_response(
            data=partes_schema,
            total_records=total_count,
            has_more=has_more,
            message="Partes obtenidas exitosamente"
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error_response(message=f"Error al obtener partes: {str(e)}")

@router.post(
    "/",
    response_model=CreateResponse,
    summary="Crear número de parte",
    description="Crea un nuevo número de parte en el sistema",
    responses={
        201: {"model": CreateResponse, "description": "Número de parte creado exitosamente"},
        400: {"model": ErrorResponse, "description": "El número de parte ya existe"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
def create_numparte(
    numparte_in: SPartesCreate,
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """Crear un nuevo numero de parte"""
    try:
        # Verificar si la parte ya existe
        partes_existentes = spartes_service.get(db, numero_parte=numparte_in.NUMPARTE)
        if partes_existentes:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return error_response(message="El número de parte ya existe")
        
        nueva_parte = spartes_service.create(db, obj_in=numparte_in)
        response.status_code = status.HTTP_201_CREATED
        
        # Convertir a esquema Pydantic antes de retornar
        nueva_parte_schema = SPartes.model_validate(nueva_parte)
        return success_response(
            data=nueva_parte_schema, 
            message="Número de parte creado exitosamente"
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error_response(message=f"Error al crear parte: {str(e)}")

@router.put(
    "/{numparte}",
    response_model=UpdateResponse,
    summary="Actualizar número de parte",
    description="Actualiza un número de parte existente en el sistema",
    responses={
        200: {"model": UpdateResponse, "description": "Número de parte actualizado exitosamente"},
        404: {"model": ErrorResponse, "description": "Número de parte no encontrado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
def update_numparte(
    numparte: str,
    numparte_in: SPartesUpdate,
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """Actualizar un numero de parte"""
    try:
        partes = spartes_service.get(db, numero_parte=numparte)
        if not partes:
            response.status_code = status.HTTP_404_NOT_FOUND
            return error_response(message="Número de parte no encontrado")
        
        updated_parte = spartes_service.update(db, db_obj=partes[0], obj_in=numparte_in)
        
        # Convertir a esquema Pydantic antes de retornar
        updated_parte_schema = SPartes.model_validate(updated_parte)
        return success_response(
            data=updated_parte_schema,
            message="Número de parte actualizado exitosamente"
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error_response(message=f"Error al actualizar parte: {str(e)}")

@router.delete(
    "/{numparte}",
    response_model=DeleteResponse,
    summary="Eliminar número de parte",
    description="Elimina un número de parte del sistema",
    responses={
        200: {"model": DeleteResponse, "description": "Número de parte eliminado exitosamente"},
        404: {"model": ErrorResponse, "description": "Número de parte no encontrado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
def delete_numparte(
    numparte: str,
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """Eliminar un numero de parte"""
    try:
        # First, get the part to verify it exists
        partes = spartes_service.get(db, numero_parte=numparte)
        if not partes:
            response.status_code = status.HTTP_404_NOT_FOUND
            return error_response(message="Número de parte no encontrado")
        
        # Store the part data before deletion for response
        parte_to_delete = partes[0]
        
        # Delete using the numero_parte parameter instead of the object
        spartes_service.delete(db, numero_parte=numparte)
        
        # Convertir a esquema Pydantic antes de retornar
        deleted_parte_schema = SPartes.model_validate(parte_to_delete)
        return success_response(
            data=deleted_parte_schema,
            message="Número de parte eliminado exitosamente"
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error_response(message=f"Error al eliminar parte: {str(e)}")
