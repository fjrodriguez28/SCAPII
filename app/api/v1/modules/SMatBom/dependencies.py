# dependencies.py
from fastapi import Depends
from . import validations
from .schemas import SMatBOMCreate
from sqlalchemy.orm import Session

from app.core.database import get_db
async def validate_matbom_data(matbom_data: SMatBOMCreate, db: Session = Depends(get_db)):
    await validations.validate_numparte_exists(db, matbom_data.NUMPARTE)
    await validations.validate_numparte_exists(db, matbom_data.NUMPARTEBOM)  # Misma tabla para partes
    await validations.validate_unimed_exists(db, matbom_data.UNIMED)
    await validations.validate_unimed_exists(db, matbom_data.UMEQUIVALENTE)
    return matbom_data