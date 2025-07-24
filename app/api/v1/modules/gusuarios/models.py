from typing import Optional
from sqlalchemy import Index, PrimaryKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class GUsuarios(Base):
    __tablename__ = 'GUsuarios'
    __table_args__ = (
        PrimaryKeyConstraint('USUARIO', name='USU_PKUsuario'),
        Index('USU_FKNivelSeg', 'NIVELSEG')
    )

    USUARIO: Mapped[str] = mapped_column(String(20, 'Modern_Spanish_CI_AS'), primary_key=True)
    NOMBRE: Mapped[Optional[str]] = mapped_column(String(100, 'Modern_Spanish_CI_AS'))
    NIVELSEG: Mapped[Optional[str]] = mapped_column(String(15, 'Modern_Spanish_CI_AS'))
    PUESTO: Mapped[Optional[str]] = mapped_column(String(30, 'Modern_Spanish_CI_AS'))
    LOGIN: Mapped[Optional[str]] = mapped_column(String(20, 'Modern_Spanish_CI_AS'))
    CLAVE_ACCESO: Mapped[Optional[str]] = mapped_column(String(10, 'Modern_Spanish_CI_AS'))
