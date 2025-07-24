# Rutas para GAAduanal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from .crud import gusuarios_crud
from .schemas import GUsuarios, GUsuariosCreate, GUsuariosUpdate

router = APIRouter()

@router.get("/", response_model=List[GUsuarios])
def read_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios"""
    usuarios = gusuarios_crud.get_multi(db, skip=skip, limit=limit)
    return usuarios

@router.post("/", response_model=GUsuarios)
def create_usuario(
    usuario_in: GUsuariosCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo usuario"""
    # Verificar si el usuario ya existe
    usuario = gusuarios_crud.get(db, usuario=usuario_in.USUARIO)
    if usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    return gusuarios_crud.create(db, obj_in=usuario_in)

@router.get("/{usuario}", response_model=GUsuarios)
def read_usuario(
    usuario: str,
    db: Session = Depends(get_db)
):
    """Obtener un usuario específico"""
    db_usuario = gusuarios_crud.get(db, usuario=usuario)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_usuario

@router.put("/{usuario}", response_model=GUsuarios)
def update_usuario(
    usuario: str,
    usuario_in: GUsuariosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un usuario"""
    db_usuario = gusuarios_crud.get(db, usuario=usuario)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return gusuarios_crud.update(db, db_obj=db_usuario, obj_in=usuario_in)

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
