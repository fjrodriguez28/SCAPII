from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Esquema base común
class SMatBOMBase(BaseModel):
    NUMPARTE: Optional[str] = Field(None, max_length=70)
    NUMPARTEBOM: Optional[str] = Field(None, max_length=70)
    CANTIDAD: Optional[Decimal] = None
    UNIMED: Optional[str] = Field(None, max_length=5)
    PROCEDENCIA: Optional[str] = Field(None, max_length=3)
    CANTMP: Optional[Decimal] = None
    CANTDESP: Optional[Decimal] = None
    CANTMERMA: Optional[Decimal] = None
    CANTEQUIVALENTE: Optional[Decimal] = None
    UMEQUIVALENTE: Optional[str] = Field(None, max_length=5)
    CANTDESPEQUI: Optional[Decimal] = None
    CANTMERMAEQUI: Optional[Decimal] = None
    DESCDESPAPARTADO: Optional[int] = None
    PORCENTAJEMP: Optional[Decimal] = None
    PORCENTAJEDESP: Optional[Decimal] = None
    PORCENTAJEMERMA: Optional[Decimal] = None
    TIPODESPMERMA: Optional[str] = Field(None, max_length=19)

# Esquema para creación (sin CONSECUTIVO ya que probablemente es autoincremental)
class SMatBOMCreate(SMatBOMBase):
    pass

# Esquema para actualización (todos los campos opcionales)
class SMatBOMUpdate(SMatBOMBase):
    pass

# Esquema para respuesta (incluye todos los campos)
class SMatBOM(SMatBOMBase):
    CONSECUTIVO: int
    
    class Config:
        from_attributes = True  # Esto permite la conversión desde ORM (antes 'orm_mode')