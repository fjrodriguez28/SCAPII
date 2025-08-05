# from sqlalchemy import create_engine, exc, text
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings
# from typing import Dict, Any
# from sqlalchemy.engine import URL

# import logging

# logger = logging.getLogger(__name__)
# connection_string = (
#     f"mssql+pyodbc://{settings.SQL_USER}:{settings.SQL_PASSWORD}@{settings.SQL_SERVER}/{settings.SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
# )

# engine = create_engine(connection_string,pool_size=5,max_overflow=10,pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     """Dependencia para obtener la sesión de base de datos"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def create_unified_engine(db_config: Dict) -> create_engine:
#     """
#     Función unificada para crear motores SQLAlchemy tanto para API como para Celery
#     Usa la misma configuración que funciona en el endpoint de prueba
#     """
#     try:
#         logger.info(f"Creando conexión a: {db_config['server']}:{db_config['port']}/{db_config['database']}")
        
#         # Construir cadena de conexión usando la misma lógica exitosa
#         connection_url = URL.create(
#             "mssql+pyodbc",
#             username=db_config["username"],
#             password=db_config["password"],
#             host=db_config["server"],
#             port=db_config.get("port", 1438),  # Asegurar que el puerto esté incluido
#             database=db_config["database"],
#             query={
#                 "driver": "ODBC Driver 17 for SQL Server",
#                 "Encrypt": "no",  # Mismo que la función exitosa
#                 "TrustServerCertificate": "Yes",  # Mismo que la función exitosa
#                 "Connection Timeout": "30",  # Timeout más largo
#                 "Login Timeout": "30",  # Timeout de login más largo
#                 "ConnectRetryCount": "3",  # Reintentos de conexión
#                 "ConnectRetryInterval": "10"  # Interval entre reintentos
#             }
#         )
        
#         # Configuración de pool optimizada para contenedores
#         engine = create_engine(
#             connection_url,
#             pool_size=3,  # Menor para contenedores
#             max_overflow=10,
#             pool_timeout=60,  # Timeout más largo
#             pool_pre_ping=True,  # Verificar conexiones antes de usar
#             pool_recycle=3600,  # Reciclar conexiones cada hora
#             echo=False,  # Cambiar a True para debug
#             connect_args={
#                 "timeout": 30,  # Timeout a nivel de driver
#                 "autocommit": False
#             }
#         )
        
#         logger.info("Motor SQLAlchemy creado exitosamente")
#         return engine
        
#     except Exception as e:
#         logger.error(f"Error creando motor SQLAlchemy: {str(e)}")
#         raise ConnectionError(f"Error creando motor: {str(e)}")

# # Mantener compatibilidad con código existente
# def create_temp_engine(db_config: Dict) -> create_engine:
#     """Wrapper para mantener compatibilidad - usa la función unificada"""
#     return create_unified_engine(db_config)

# def create_db_engine(db_config: dict) -> create_engine:
#     """Wrapper para mantener compatibilidad - usa la función unificada"""
#     return create_unified_engine(db_config)

# def parse_sqlalchemy_error(e: Exception) -> Dict[str, Any]:
#     """Analiza errores de SQLAlchemy para dar información detallada"""
#     try:
#         error_info = {
#             "success": False,
#             "message": str(e.orig) if hasattr(e, 'orig') else str(e),
#             "type": type(e).__name__
#         }
        
#         # Detectar errores comunes de MSSQL
#         if isinstance(e, exc.DBAPIError) and e.orig:
#             orig_error = e.orig
#             error_info["code"] = getattr(orig_error, 'args', [None])[0]
#             error_info["sqlstate"] = getattr(orig_error, 'args', [None, None])[1]
            
#             # Detalles específicos de errores
#             message = error_info["message"].lower()
#             if "login timeout expired" in message:
#                 error_info["diagnosis"] = "Timeout de conexión - verificar conectividad de red y configuración de firewall"
#                 error_info["suggestions"] = [
#                     "Verificar que el puerto 1433 esté abierto",
#                     "Confirmar que SQL Server acepta conexiones TCP/IP",
#                     "Revisar configuración de red del contenedor Docker"
#                 ]
#             elif "invalid column name" in message:
#                 error_info["diagnosis"] = "Columna inválida en la consulta"
#             elif "invalid object name" in message:
#                 error_info["diagnosis"] = "Tabla o vista no encontrada"
#             elif "incorrect syntax" in message:
#                 error_info["diagnosis"] = "Error de sintaxis SQL"
#             elif "permission denied" in message:
#                 error_info["diagnosis"] = "Permisos insuficientes"
#             elif "18456" in str(error_info.get("code", "")):
#                 error_info["diagnosis"] = "Error de autenticación"
        
#         return error_info
#     except Exception as parse_error:
#         return {
#             "success": False,
#             "message": f"Error original: {str(e)} | Error en parseo: {str(parse_error)}",
#             "type": "parse_error"
#         }

# def test_connection(db_config: Dict) -> Dict[str, Any]:
#     """
#     Función para probar conexión antes de usar en transferencias
#     """
#     try:
#         engine = create_unified_engine(db_config)
#         with engine.connect() as conn:
#             result = conn.execute(text("SELECT 1 as test"))
#             row = result.fetchone()
            
#         return {
#             "success": True,
#             "message": "Conexión exitosa",
#             "server": f"{db_config['server']}:{db_config.get('port', 1433)}",
#             "database": db_config['database']
#         }
#     except Exception as e:
#         error_info = parse_sqlalchemy_error(e)
#         return {
#             "success": False,
#             "error": error_info,
#             "server": f"{db_config['server']}:{db_config.get('port', 1433)}",
#             "database": db_config['database']
#         }

from sqlalchemy import create_engine, exc, event, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Dict, Any
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

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

def create_unified_engine(db_config: Dict) -> create_engine:
    """
    Función unificada corregida para problemas ODBC específicos
    """
    try:
        logger.info(f"Creando conexión a: {db_config['server']}:{db_config.get('port', 1433)}/{db_config['database']}")
        
        # Construir cadena de conexión con configuraciones específicas para ODBC
        connection_url = URL.create(
            "mssql+pyodbc",
            username=db_config["username"],
            password=db_config["password"],
            host=db_config["server"],
            port=db_config.get("port", 1433),
            database=db_config["database"],
            query={
                "driver": "ODBC Driver 17 for SQL Server",
                "Encrypt": "no",
                "TrustServerCertificate": "Yes",
                "Connection Timeout": "60",  # Timeout más largo
                "Login Timeout": "60",       # Login timeout más largo
                "ConnectRetryCount": "3",
                "ConnectRetryInterval": "10",
                # Configuraciones específicas para evitar problemas ODBC
                "MARS_Connection": "yes",    # Multiple Active Result Sets
                "autocommit": "false",       # Control manual de transacciones
                "AnsiNPW": "yes",           # ANSI null, padding, warnings
            }
        )
        
        # Configuración de engine optimizada para evitar problemas de cursor
        engine = create_engine(
            connection_url,
            pool_size=2,           # Pool más pequeño para evitar problemas
            max_overflow=5,        # Menos conexiones simultáneas
            pool_timeout=120,      # Timeout más largo para obtener conexión
            pool_pre_ping=True,    # Verificar conexiones antes de usar
            pool_recycle=1800,     # Reciclar conexiones cada 30 minutos
            echo=False,
            # Configuraciones específicas para ODBC
            connect_args={
                "timeout": 60,
                "autocommit": False,
                # Configuraciones adicionales de ODBC
                "TrustServerCertificate": "yes",
                "Encrypt": "no"
            },
            # Configuraciones de ejecución
            execution_options={
                "isolation_level": "READ_COMMITTED",
                "autocommit": False
            }
        )
        
        # Event listeners para manejo robusto de conexiones
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Configurar la conexión cuando se establece"""
            try:
                # Configuraciones específicas de sesión SQL Server
                cursor = dbapi_connection.cursor()
                cursor.execute("SET ANSI_NULLS ON")
                cursor.execute("SET ANSI_PADDING ON") 
                cursor.execute("SET ANSI_WARNINGS ON")
                cursor.execute("SET CONCAT_NULL_YIELDS_NULL ON")
                cursor.execute("SET QUOTED_IDENTIFIER ON")
                cursor.execute("SET NUMERIC_ROUNDABORT OFF")
                cursor.execute("SET ARITHABORT ON")
                cursor.close()
                logger.debug("Configuraciones de sesión SQL Server aplicadas")
            except Exception as e:
                logger.warning(f"Error configurando sesión SQL Server: {e}")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Verificar conexión cuando se obtiene del pool"""
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
            except Exception as e:
                logger.warning(f"Conexión inválida detectada en checkout: {e}")
                # Invalidar la conexión para que sea recreada
                connection_record.invalidate(e)
                raise exc.DisconnectionError("Conexión inválida") from e
        
        logger.info("Motor SQLAlchemy creado exitosamente")
        return engine
        
    except Exception as e:
        logger.error(f"Error creando motor SQLAlchemy: {str(e)}")
        raise ConnectionError(f"Error creando motor: {str(e)}")

# Mantener compatibilidad con código existente
def create_temp_engine(db_config: Dict) -> create_engine:
    """Wrapper para mantener compatibilidad - usa la función unificada"""
    return create_unified_engine(db_config)

def create_db_engine(db_config: dict) -> create_engine:
    """Wrapper para mantener compatibilidad - usa la función unificada"""
    return create_unified_engine(db_config)

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
            if "function sequence error" in message or "hy010" in message:
                error_info["diagnosis"] = "Error de secuencia de función ODBC - problema con cursores"
                error_info["suggestions"] = [
                    "Verificar que no haya consultas concurrentes en la misma conexión",
                    "Asegurar que los cursores se cierren correctamente",
                    "Revisar configuración MARS (Multiple Active Result Sets)"
                ]
            elif "login timeout expired" in message:
                error_info["diagnosis"] = "Timeout de conexión - verificar conectividad de red y configuración de firewall"
                error_info["suggestions"] = [
                    "Verificar que el puerto esté abierto",
                    "Confirmar que SQL Server acepta conexiones TCP/IP",
                    "Revisar configuración de red del contenedor Docker",
                    "Aumentar timeout de conexión"
                ]
            elif "invalid column name" in message:
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

def test_connection(db_config: Dict) -> Dict[str, Any]:
    """
    Función para probar conexión antes de usar en transferencias
    """
    try:
        engine = create_unified_engine(db_config)
        
        # Probar conexión con manejo específico de cursores
        with engine.connect() as conn:
            # Usar transacción explícita para evitar problemas de cursor
            trans = conn.begin()
            try:
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                result.close()  # Cerrar resultado explícitamente
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise
        
        engine.dispose()
        return {
            "success": True,
            "message": "Conexión exitosa",
            "server": f"{db_config['server']}:{db_config.get('port', 1438)}",
            "database": db_config['database']
        }
    except Exception as e:
        error_info = parse_sqlalchemy_error(e)
        return {
            "success": False,
            "error": error_info,
            "server": f"{db_config['server']}:{db_config.get('port', 1438)}",
            "database": db_config['database']
        }