from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

async def validate_numparte_exists(db: Session, numparte: str):
    if numparte:
        result = db.execute(text(
            "SELECT COUNT(*) AS cantidad FROM SPartes WHERE NUMPARTE = :numparte"), 
            {"numparte": numparte}
        )
        count = result.scalar()
        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El NUMPARTE {numparte} no existe en el catálogo de partes."
            )

async def validate_unimed_exists(db: Session, unimed: str):
    if unimed:
        result = db.execute(text(
            "SELECT COUNT(*) AS cantidad FROM GUniMedida WHERE ClaveUni = :unimed"), 
            {"unimed": unimed}
        )
        count = result.scalar()
        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La unidad de medida {unimed} no existe en el catálogo."
            )