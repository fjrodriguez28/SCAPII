from typing import Optional
from pydantic import BaseModel

# Schema base para GUsuarios
class GUsuariosBase(BaseModel):
    NOMBRE: Optional[str] = None
    NIVELSEG: Optional[str] = None
    PUESTO: Optional[str] = None
    LOGIN: Optional[str] = None
    CLAVE_ACCESO: Optional[str] = None

# Schema para crear usuario
class GUsuariosCreate(GUsuariosBase):
    USUARIO: str

# Schema para actualizar usuario
class GUsuariosUpdate(GUsuariosBase):
    pass

# Schema para respuesta (lo que devuelve la API)
class GUsuarios(GUsuariosBase):
    USUARIO: str
    
    class Config:
        from_attributes = True
