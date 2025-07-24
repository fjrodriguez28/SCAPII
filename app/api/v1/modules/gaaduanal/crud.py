# CRUD para GAAduanal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import GUsuarios
from .schemas import GUsuariosCreate, GUsuariosUpdate

class GUsuariosCRUD:
    def get(self, db: Session, usuario: str) -> Optional[GUsuarios]:
        """Obtener un usuario por ID"""
        return db.scalar(select(GUsuarios).where(GUsuarios.USUARIO == usuario))
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[GUsuarios]:
        """Obtener lista de usuarios con paginación"""
        return db.scalars(select(GUsuarios).offset(skip).limit(limit)).all()
    
    def create(self, db: Session, obj_in: GUsuariosCreate) -> GUsuarios:
        """Crear un nuevo usuario"""
        db_obj = GUsuarios(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: GUsuarios, obj_in: GUsuariosUpdate) -> GUsuarios:
        """Actualizar un usuario existente"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, usuario: str) -> Optional[GUsuarios]:
        """Eliminar un usuario"""
        db_obj = self.get(db, usuario)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

# Instancia del CRUD
gusuarios_crud = GUsuariosCRUD()
