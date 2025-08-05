# app/api/v1/modules/SMatBom/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from . import models, schemas, validations
from app.core.database import get_db
from typing import Optional, List
from .service import MatBOMService

router = APIRouter(tags=["SMatBOM"])

# Dependencia común para validaciones
async def validate_matbom_data(
    matbom_data: schemas.SMatBOMBase, 
    db: Session = Depends(get_db)
):
    await validations.validate_numparte_exists(db, matbom_data.NUMPARTE)
    await validations.validate_numparte_exists(db, matbom_data.NUMPARTEBOM)
    await validations.validate_unimed_exists(db, matbom_data.UNIMED)
    if matbom_data.UMEQUIVALENTE:
        await validations.validate_unimed_exists(db, matbom_data.UMEQUIVALENTE)
    return matbom_data

# CREATE
@router.post(
    "/", 
    response_model=schemas.SMatBOM,
    status_code=status.HTTP_201_CREATED
)
async def create_matbom(
    validated_data: schemas.SMatBOMCreate = Depends(validate_matbom_data),
    db: Session = Depends(get_db)
):
    try:
        return MatBOMService.create_matbom(db, validated_data)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating SMatBOM: {str(e)}"
        )

# READ (Search)
@router.get("/", response_model=List[schemas.SMatBOM])
async def search_matbom(
    consecutivo: Optional[int] = Query(
        None, 
        description="Filtrar por CONSECUTIVO específico",
        ge=1
    ),
    numparte: Optional[str] = Query(
        None, 
        description="Filtrar por NUMPARTE",
        max_length=70
    ),
    numpartebom: Optional[str] = Query(None, description="Filtrar por NUMPARTEBOM"),
    skip: int = Query(0, description="Número de registros a saltar", ge=0),
    limit: int = Query(100, description="Límite de registros por página", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    try:
        return MatBOMService.get_matbom(
            db,
            consecutivo=consecutivo,
            numparte=numparte,
            numpartebom=numpartebom,
            skip=skip,
            limit=limit
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la búsqueda: {str(e)}"
        )

# UPDATE
@router.patch("/{consecutivo}", response_model=schemas.SMatBOM)
async def update_matbom(
    consecutivo: int,
    matbom_update: schemas.SMatBOMUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Validar datos de entrada
        await validate_matbom_data(matbom_update, db)
        return MatBOMService.update_matbom(db, consecutivo, matbom_update)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating SMatBOM: {str(e)}"
        )

# DELETE
@router.delete("/{consecutivo}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_matbom(consecutivo: int, db: Session = Depends(get_db)):
    try:
        MatBOMService.delete_matbom(db, consecutivo)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting SMatBOM: {str(e)}"
        )