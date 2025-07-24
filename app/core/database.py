from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

connection_string = (
    f"mssql+pyodbc://{settings.SQL_USER}:{settings.SQL_PASSWORD}@{settings.SQL_SERVER}/{settings.SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
