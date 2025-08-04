from sqlalchemy import Index, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, DECIMAL, DateTime, Index, Integer, PrimaryKeyConstraint, String, Table
from typing import Optional
from sqlalchemy.dialects.mssql import TINYINT
import decimal

class Base(DeclarativeBase):
    pass
class SMatBOM(Base):
    __tablename__ = 'SMatBOM'
    __table_args__ = (
        PrimaryKeyConstraint('CONSECUTIVO', name='MatBOM_PKConsecutivo'),
        Index('MatBOM_FKNumParteConsec', 'NUMPARTE', 'CONSECUTIVO', unique=True),
        Index('MatBOM_FKNumParteParteBOM', 'NUMPARTE', 'NUMPARTEBOM'),
        Index('MatBOM_FKParteBOM', 'NUMPARTEBOM')
    )

    CONSECUTIVO: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        autoincrement=False  # Importante!
    )
    NUMPARTE: Mapped[Optional[str]] = mapped_column(String(70, 'Modern_Spanish_CI_AS'))
    NUMPARTEBOM: Mapped[Optional[str]] = mapped_column(String(70, 'Modern_Spanish_CI_AS'))
    CANTIDAD: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    UNIMED: Mapped[Optional[str]] = mapped_column(String(5, 'Modern_Spanish_CI_AS'))
    PROCEDENCIA: Mapped[Optional[str]] = mapped_column(String(3, 'Modern_Spanish_CI_AS'))
    CANTMP: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    CANTDESP: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    CANTMERMA: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    CANTEQUIVALENTE: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    UMEQUIVALENTE: Mapped[Optional[str]] = mapped_column(String(5, 'Modern_Spanish_CI_AS'))
    CANTDESPEQUI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    CANTMERMAEQUI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(19, 8))
    DESCDESPAPARTADO: Mapped[Optional[int]] = mapped_column(TINYINT)
    PORCENTAJEMP: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(7, 2))
    PORCENTAJEDESP: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(7, 2))
    PORCENTAJEMERMA: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(7, 2))
    TIPODESPMERMA: Mapped[Optional[str]] = mapped_column(String(19, 'Modern_Spanish_CI_AS'))