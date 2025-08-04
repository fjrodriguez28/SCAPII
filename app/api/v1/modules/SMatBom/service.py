from sqlalchemy import func,select
from .models import SMatBOM
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import SMatBOM

def get_next_consecutivo(db: Session) -> int:
    # Buscar el máximo CONSECUTIVO actual
    max_consecutivo = db.query(func.max(SMatBOM.CONSECUTIVO)).scalar()
    # Si no hay registros, empezar en 1
    return max_consecutivo + 1 if max_consecutivo is not None else 1



# app/api/v1/modules/SMatBom/services.py
from sqlalchemy.orm import Session
from . import models
from .schemas import SMatBOMCreate, SMatBOMUpdate
from sqlalchemy import func
from fastapi import HTTPException, status

class MatBOMService:
    @staticmethod
    def get_next_consecutivo(db: Session) -> int:
        max_consecutivo = db.query(func.max(models.SMatBOM.CONSECUTIVO)).scalar()
        return max_consecutivo + 1 if max_consecutivo is not None else 1

    @staticmethod
    def create_matbom(db: Session, data: SMatBOMCreate):
        next_consecutivo = MatBOMService.get_next_consecutivo(db)
        db_matbom = models.SMatBOM(CONSECUTIVO=next_consecutivo, **data.model_dump())
        db.add(db_matbom)
        db.commit()
        db.refresh(db_matbom)
        return db_matbom

    @staticmethod
    def get_matbom(
        db: Session,
        consecutivo: int | None = None,
        numparte: str | None = None,
        numpartebom: str | None = None,
        skip: int = 0,
        limit: int = 100
    ):
        query = db.query(models.SMatBOM).order_by(models.SMatBOM.CONSECUTIVO)
        
        if consecutivo is not None:
            query = query.filter(models.SMatBOM.CONSECUTIVO == consecutivo)
        if numparte is not None:
            query = query.filter(models.SMatBOM.NUMPARTE == numparte)
        if numpartebom is not None:
            query = query.filter(models.SMatBOM.NUMPARTEBOM == numpartebom)
            
        results = query.offset(skip).limit(limit).all()
        
        if consecutivo is not None and not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con CONSECUTIVO {consecutivo} no encontrado"
            )
            
        return results

    @staticmethod
    def update_matbom(db: Session, consecutivo: int, data: SMatBOMUpdate):
        db_matbom = db.query(models.SMatBOM).filter(
            models.SMatBOM.CONSECUTIVO == consecutivo
        ).first()
        
        if not db_matbom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con CONSECUTIVO {consecutivo} no encontrado"
            )
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_matbom, key, value)
        
        db.commit()
        db.refresh(db_matbom)
        return db_matbom

    @staticmethod
    def delete_matbom(db: Session, consecutivo: int):
        db_matbom = db.query(models.SMatBOM).filter(
            models.SMatBOM.CONSECUTIVO == consecutivo
        ).first()
        
        if not db_matbom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con CONSECUTIVO {consecutivo} no encontrado"
            )
        
        db.delete(db_matbom)
        db.commit()
        return True
        
