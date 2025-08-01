from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from .models import SPartes
from .schemas import SPartesCreate, SPartesUpdate

class SPartesService:
    # Campos válidos para ordenamiento basados en el modelo
    VALID_ORDER_FIELDS = ["NUMPARTE", "NOMBRE", "NIVELSEG", "PUESTO", "LOGIN"]
    
    def get(self, db: Session, skip: int = 0, limit: int = 100, order_by: str = "USUARIO", numero_parte: str = None) -> List[SPartes]:
        """Obtener usuarios con filtros opcionales - puede devolver uno o múltiples"""
        # Construir query base
        query = select(SPartes)
        
        # Si se especifica un usuario exacto, buscarlo
        if numero_parte:
            query = query.where(SPartes.NUMPARTE == numero_parte)
        
        # Validar que el campo está en la lista de campos válidos
        if order_by in self.VALID_ORDER_FIELDS:
            order_field = getattr(SPartes, order_by)
        else:
            order_field = SPartes.NUMPARTE  # Campo por defecto
        
        # Aplicar ordenamiento y paginación (solo si no es búsqueda específica)
        query = query.order_by(order_field)
        if not numero_parte:  # Solo aplicar paginación si no es búsqueda específica
            query = query.offset(skip).limit(limit)
        
        return db.scalars(query).all()
    
    def create(self, db: Session, obj_in: SPartesCreate) -> SPartes:
        """Crear un nuevo numero de parte"""
        db_obj = SPartes(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: SPartes, obj_in: SPartesUpdate) -> SPartes:
        """Actualizar un numero de parte existente"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, numero_parte: str) -> Optional[SPartes]:
        """Eliminar un numero de parte"""
        partes = self.get(db, numero_parte=numero_parte)
        if numero_parte:
            db_obj = numero_parte[0]  # Tomar el primer resultado
            db.delete(db_obj)
            db.commit()
            return db_obj
        return None
    def count_all(self, db: Session, numero_parte: str = None) -> int:
        """Count total number of partes, optionally filtered by numero_parte"""
        query = select(func.count()).select_from(SPartes)
        
        if numero_parte:
            query = query.where(SPartes.NUMPARTE == numero_parte)
            
        return db.scalar(query)
# Instancia del CRUD
spartes_service = SPartesService()
