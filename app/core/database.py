from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Dict, Any
from sqlalchemy.engine import URL
connection_string = (
    f"mssql+pyodbc://{settings.SQL_USER}:{settings.SQL_PASSWORD}@{settings.SQL_SERVER}/{settings.SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(connection_string,pool_size=5,max_overflow=10,pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_temp_engine(db_config: Dict) -> create_engine:
    """Crea un motor SQLAlchemy temporal para conexiones MSSQL"""
    try:
        # Construir cadena de conexión para MSSQL
        connection_url = URL.create(
            "mssql+pyodbc",
            username=db_config["username"],
            password=db_config["password"],
            host=db_config["server"],
            database=db_config["database"],
            query={
                "driver": "ODBC Driver 17 for SQL Server",
                "Encrypt": "yes",
                "TrustServerCertificate": "no",
                "Connection Timeout": "30"
            }
        )
        
        return create_engine(
            connection_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True
        )
    except Exception as e:
        raise ConnectionError(f"Error creando motor: {str(e)}")

def parse_sqlalchemy_error(e: Exception) -> Dict[str, Any]:
    """Analiza errores de SQLAlchemy para dar información detallada"""
    try:
        error_info = {
            "success": False,
            "message": str(e.orig) if hasattr(e, 'orig') else str(e),
            "type": type(e).__name__
        }
        
        # Detectar errores comunes de MSSQL
        if isinstance(e, exc.DBAPIError) and e.orig:
            orig_error = e.orig
            error_info["code"] = getattr(orig_error, 'args', [None])[0]
            error_info["sqlstate"] = getattr(orig_error, 'args', [None, None])[1]
            
            # Detalles específicos de errores
            message = error_info["message"].lower()
            if "invalid column name" in message:
                error_info["diagnosis"] = "Columna inválida en la consulta"
            elif "invalid object name" in message:
                error_info["diagnosis"] = "Tabla o vista no encontrada"
            elif "incorrect syntax" in message:
                error_info["diagnosis"] = "Error de sintaxis SQL"
            elif "permission denied" in message:
                error_info["diagnosis"] = "Permisos insuficientes"
            elif "18456" in str(error_info.get("code", "")):
                error_info["diagnosis"] = "Error de autenticación"
        
        return error_info
    except Exception as parse_error:
        return {
            "success": False,
            "message": f"Error original: {str(e)} | Error en parseo: {str(parse_error)}",
            "type": "parse_error"
        }
    
def create_db_engine(db_config: dict) -> create_engine:
    """Crea un motor SQLAlchemy para MSSQL usando la misma lógica en API y Celery"""
    try:
        # Construir cadena de conexión compatible con API y Celery
        connection_url = URL.create(
            "mssql+pyodbc",
            username=db_config["username"],
            password=db_config["password"],
            host=db_config["server"],
            database=db_config["database"],
            query={
                "driver": "ODBC Driver 17 for SQL Server",
                "Encrypt": "no",
                "TrustServerCertificate": "Yes",                
            }
        )
        
        return create_engine(
            connection_url,
            pool_size=5,
            max_overflow=30,
            pool_pre_ping=True,
            echo=False  # Desactivar en producción
        )
    except Exception as e:
        raise ConnectionError(f"Error creando motor: {str(e)}")