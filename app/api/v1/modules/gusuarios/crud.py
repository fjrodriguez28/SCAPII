from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import GUsuarios
from .schemas import GUsuariosCreate, GUsuariosUpdate

class GUsuariosCRUD:
    # Campos válidos para ordenamiento basados en el modelo
    VALID_ORDER_FIELDS = ["USUARIO", "NOMBRE", "NIVELSEG", "PUESTO", "LOGIN"]
    
    def get(self, db: Session, usuario: str = None, skip: int = 0, limit: int = 100, order_by: str = "USUARIO", nombre: str = None, nivelseg: str = None) -> List[GUsuarios]:
        """Obtener usuarios con filtros opcionales - puede devolver uno o múltiples"""
        # Construir query base
        query = select(GUsuarios)
        
        # Si se especifica un usuario exacto, buscarlo
        if usuario:
            query = query.where(GUsuarios.USUARIO == usuario)
        
        # Aplicar otros filtros si se proporcionan
        if nombre:
            query = query.where(GUsuarios.NOMBRE.ilike(f"%{nombre}%"))
        if nivelseg:
            query = query.where(GUsuarios.NIVELSEG == nivelseg)
        
        # Validar que el campo está en la lista de campos válidos
        if order_by in self.VALID_ORDER_FIELDS:
            order_field = getattr(GUsuarios, order_by)
        else:
            order_field = GUsuarios.USUARIO  # Campo por defecto
        
        # Aplicar ordenamiento y paginación (solo si no es búsqueda específica)
        query = query.order_by(order_field)
        if not usuario:  # Solo aplicar paginación si no es búsqueda específica
            query = query.offset(skip).limit(limit)
        
        return db.scalars(query).all()
    
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
        usuarios = self.get(db, usuario=usuario)
        if usuarios:
            db_obj = usuarios[0]  # Tomar el primer resultado
            db.delete(db_obj)
            db.commit()
            return db_obj
        return None

# Instancia del CRUD
gusuarios_crud = GUsuariosCRUD()
