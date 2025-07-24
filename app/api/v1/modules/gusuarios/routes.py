from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from .crud import gusuarios_crud
from .schemas import GUsuarios, GUsuariosCreate, GUsuariosUpdate
from .enums import GUsuariosOrderBy

router = APIRouter()

@router.get("/", response_model=List[GUsuarios])
def read_usuarios(
    skip: int = 0,
    limit: int = 100,
    order_by: GUsuariosOrderBy = GUsuariosOrderBy.USUARIO,
    usuario: str = None,  # Parámetro opcional para buscar usuario específico
    nombre: str = None,   # Filtro por nombre
    nivelseg: str = None, # Filtro por nivel de seguridad
    db: Session = Depends(get_db)
):
    """Obtener usuarios con filtros opcionales"""
    usuarios = gusuarios_crud.get(
        db, 
        usuario=usuario,
        skip=skip, 
        limit=limit, 
        order_by=order_by.value,
        nombre=nombre,
        nivelseg=nivelseg
    )
    
    if usuario and not usuarios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuarios

@router.post("/", response_model=GUsuarios)
def create_usuario(
    usuario_in: GUsuariosCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo usuario"""
    # Verificar si el usuario ya existe
    usuarios_existentes = gusuarios_crud.get(db, usuario=usuario_in.USUARIO)
    if usuarios_existentes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    return gusuarios_crud.create(db, obj_in=usuario_in)

@router.put("/{usuario}", response_model=GUsuarios)
def update_usuario(
    usuario: str,
    usuario_in: GUsuariosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un usuario"""
    usuarios = gusuarios_crud.get(db, usuario=usuario)
    if not usuarios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return gusuarios_crud.update(db, db_obj=usuarios[0], obj_in=usuario_in)

@router.delete("/{usuario}", response_model=GUsuarios)
def delete_usuario(
    usuario: str,
    db: Session = Depends(get_db)
):
    """Eliminar un usuario"""
    db_usuario = gusuarios_crud.delete(db, usuario=usuario)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_usuario
