# app/worker/database_worker.py
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from contextlib import contextmanager
from fastapi import Depends
from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine, CursorResult
from app.core.database import SessionLocal, create_unified_engine, get_db, parse_sqlalchemy_error, test_connection
from app.models.task import TaskStatus
from sqlalchemy.orm import Session

# Configurar logging
logger = logging.getLogger(__name__)

class DataTransferWorker:
    def __init__(self, transfer_config: Dict, db_task_id: int, celery_task: Any):
        self.config = transfer_config
        self.db_task_id = db_task_id
        self.celery_task = celery_task
        self.source_engine: Optional[Engine] = None
        self.target_engine: Optional[Engine] = None
        self.stats = {
            "total_tables": len(transfer_config["tables"]),
            "completed_tables": 0,
            "total_rows": 0,
            "transferred_rows": 0,
            "errors": [],
            "warnings": [],
            "table_details": {},
            "start_time": datetime.now(),
            "end_time": None
        }
        self.current_table = None

    def connect_databases(self):
        """Conecta a las bases de datos usando la función unificada con validación"""
        try:
            logger.info("Iniciando conexiones a bases de datos...")
            
            # Probar conexión source antes de crear el engine
            source_test = test_connection(self.config["source"])
            if not source_test["success"]:
                raise ConnectionError(f"Error conectando a BD origen: {source_test['error']}")
            
            # Probar conexión target antes de crear el engine
            target_test = test_connection(self.config["target"])
            if not target_test["success"]:
                raise ConnectionError(f"Error conectando a BD destino: {target_test['error']}")
            
            # Crear engines usando la función unificada
            self.source_engine = create_unified_engine(self.config["source"])
            self.target_engine = create_unified_engine(self.config["target"])
            
            # Verificar conexiones con consultas simples y manejo robusto
            self._verify_connection(self.source_engine, "source")
            self._verify_connection(self.target_engine, "target")
            
            logger.info("Conexiones establecidas correctamente")
            
        except Exception as e:
            logger.error(f"Error estableciendo conexiones: {str(e)}")
            # Limpiar recursos si hay error
            self.disconnect()
            raise

    def _verify_connection(self, engine: Engine, connection_name: str):
        """Verificar conexión individual con manejo robusto"""
        try:
            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    result = conn.execute(text("SELECT 1 as test"))
                    test_value = result.scalar()
                    result.close()
                    trans.commit()
                    logger.debug(f"Conexión {connection_name} verificada: {test_value}")
                except Exception as e:
                    trans.rollback()
                    raise
        except Exception as e:
            logger.error(f"Error verificando conexión {connection_name}: {str(e)}")
            raise

    def disconnect(self):
        """Cierra las conexiones a las bases de datos"""
        try:
            if self.source_engine:
                self.source_engine.dispose()
                logger.info("Conexión source cerrada")
            if self.target_engine:
                self.target_engine.dispose()
                logger.info("Conexión target cerrada")
        except Exception as e:
            logger.warning(f"Error cerrando conexiones: {str(e)}")

    @contextmanager
    def safe_connection(self, engine: Engine):
        """Context manager para manejo seguro de conexiones"""
        conn = None
        trans = None
        try:
            conn = engine.connect()
            trans = conn.begin()
            yield conn
            trans.commit()
        except Exception as e:
            if trans:
                trans.rollback()
            logger.error(f"Error en conexión: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query_safe(self, engine: Engine, query: str, params: dict = None) -> Any:
        """Ejecuta una consulta con manejo seguro de cursores"""
        logger.debug(f"Ejecutando query: {query[:100]}...")
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with self.safe_connection(engine) as conn:
                    result = conn.execute(text(query), params or {})
                    
                    # Si es una consulta SELECT, obtener el resultado inmediatamente
                    if query.strip().upper().startswith('SELECT'):
                        if 'COUNT(' in query.upper():
                            # Para COUNT, obtener el scalar
                            value = result.scalar()
                            result.close()
                            return value
                        else:
                            # Para otras SELECT, obtener todas las filas
                            rows = result.fetchall()
                            columns = result.keys()
                            result.close()
                            return {"rows": rows, "columns": list(columns)}
                    else:
                        # Para INSERT/UPDATE/DELETE, obtener rowcount
                        rowcount = result.rowcount
                        result.close()
                        return rowcount
                        
            except exc.DisconnectionError as e:
                logger.warning(f"Desconexión detectada (intento {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    # Recrear engine si es necesario
                    try:
                        engine.dispose()
                        time.sleep(1)
                    except:
                        pass
                    continue
                else:
                    raise
            except exc.DBAPIError as e:
                error_detail = parse_sqlalchemy_error(e)
                logger.error(f"Error en consulta SQL: {error_detail}")
                
                # Si es un error de secuencia de función, reintentar una vez
                if "function sequence error" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning("Error de secuencia de función, reintentando...")
                    time.sleep(retry_delay)
                    continue
                    
                raise
            except Exception as e:
                logger.error(f"Error inesperado en query: {str(e)}")
                raise

    def build_select_query(self, table_config: Dict) -> str:
        """Construye la consulta SELECT para la tabla de origen"""
        logger.debug("Construyendo consulta SELECT")
        
        # Determinar columnas a seleccionar
        columns = table_config.get("selected_columns")
        columns_str = ", ".join(columns) if columns else "*"
        
        # Construir consulta base
        query = f"SELECT {columns_str} FROM {table_config['source_table']}"
        
        # Aplicar WHERE si existe
        if table_config.get("where_clause"):
            query += f" WHERE {table_config['where_clause']}"
        
        # Aplicar ORDER BY si existe
        if table_config.get("order_by"):
            query += f" ORDER BY {table_config['order_by']}"
        
        # Aplicar TOP (límite de filas) si existe (MSSQL específico)
        if table_config.get("row_limit"):
            query = f"SELECT TOP {table_config['row_limit']} * FROM ({query}) AS limited_query"
        
        return query

    def get_table_columns(self, table_config: Dict) -> List[str]:
        """Obtener columnas de la tabla de forma segura"""
        try:
            # Consulta para obtener solo los nombres de columnas
            column_query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_config['source_table']}'
            ORDER BY ORDINAL_POSITION
            """
            
            result_data = self.execute_query_safe(self.source_engine, column_query)
            columns = [row[0] for row in result_data["rows"]]
            
            if not columns:
                # Fallback: usar consulta con LIMIT 0
                select_query = self.build_select_query(table_config)
                limited_query = f"SELECT TOP 0 * FROM ({select_query}) AS column_check"
                result_data = self.execute_query_safe(self.source_engine, limited_query)
                columns = result_data["columns"]
            
            return columns
            
        except Exception as e:
            logger.error(f"Error obteniendo columnas: {str(e)}")
            raise

    def transfer_table_data(self, table_config: Dict):
        """Transferencia completa para una tabla individual con manejo robusto"""
        table_name = table_config["source_table"]
        self.current_table = table_name
        logger.info(f"Procesando tabla: {table_name}")
        
        # Inicializar estadísticas de la tabla
        self.stats["table_details"][table_name] = {
            "status": "PROCESSING",
            "total_rows": 0,
            "transferred": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "errors": 0
        }
        table_stats = self.stats["table_details"][table_name]
        
        try:
            # Construir consulta SELECT
            select_query = self.build_select_query(table_config)
            logger.debug(f"Query SELECT: {select_query}")
            
            # Obtener total de filas de forma segura
            count_query = f"SELECT COUNT(*) FROM ({select_query}) AS total_rows"
            total_rows = self.execute_query_safe(self.source_engine, count_query)
            
            table_stats["total_rows"] = total_rows
            self.stats["total_rows"] += total_rows
            logger.info(f"Tabla {table_name}: {total_rows} filas a transferir")
            
            if total_rows == 0:
                logger.info(f"Tabla {table_name} está vacía, omitiendo transferencia")
                table_stats["status"] = "COMPLETED"
                self.stats["completed_tables"] += 1
                return
            
            # Obtener columnas de forma segura
            source_columns = self.get_table_columns(table_config)
            logger.debug(f"Columnas detectadas: {source_columns}")
            
            # Transferir datos por chunks
            chunk_size = self.config["chunk_size"]
            transferred = 0
            start_time = time.time()
            
            # Procesar en chunks con OFFSET/FETCH
            for offset in range(0, total_rows, chunk_size):
                try:
                    chunk_query = f"""
                    SELECT * FROM (
                        {select_query}
                    ) AS src
                    ORDER BY (SELECT NULL)
                    OFFSET {offset} ROWS
                    FETCH NEXT {chunk_size} ROWS ONLY
                    """
                    
                    # Obtener chunk de datos
                    chunk_result = self.execute_query_safe(self.source_engine, chunk_query)
                    chunk_rows = chunk_result["rows"]
                    
                    if not chunk_rows:
                        logger.info(f"No hay más datos en offset {offset}")
                        break
                    
                    # Convertir a formato para inserción
                    chunk_data = []
                    for row in chunk_rows:
                        row_dict = {col: val for col, val in zip(source_columns, row)}
                        chunk_data.append(row_dict)
                    
                    # Insertar chunk en destino
                    self.insert_chunk_safe(table_config, source_columns, chunk_data)
                    
                    # Actualizar estadísticas
                    transferred += len(chunk_data)
                    table_stats["transferred"] = transferred
                    self.stats["transferred_rows"] += len(chunk_data)
                    
                    # Calcular rendimiento
                    elapsed = time.time() - start_time
                    rows_per_sec = transferred / elapsed if elapsed > 0 else 0
                    
                    if transferred % (chunk_size * 5) == 0:  # Log cada 5 chunks
                        logger.info(f"{table_name}: {transferred}/{total_rows} filas ({rows_per_sec:.1f} filas/seg)")
                    
                    # Actualizar progreso
                    self._update_progress()
                    
                except Exception as e:
                    error_detail = parse_sqlalchemy_error(e) if isinstance(e, exc.SQLAlchemyError) else {"message": str(e)}
                    
                    if self.config.get("skip_errors", False):
                        logger.warning(f"Error en chunk {offset//chunk_size}: {error_detail['message']}")
                        table_stats["errors"] += len(chunk_data) if 'chunk_data' in locals() else chunk_size
                        self.stats["warnings"].append({
                            "table": table_name,
                            "chunk": offset // chunk_size,
                            "error": error_detail
                        })
                        continue
                    else:
                        raise
            
            # Finalización exitosa
            table_stats["status"] = "COMPLETED"
            self.stats["completed_tables"] += 1
            logger.info(f"Tabla {table_name} completada: {transferred}/{total_rows} filas")
            
        except Exception as e:
            # Manejo de errores para la tabla
            error_detail = parse_sqlalchemy_error(e) if isinstance(e, exc.SQLAlchemyError) else {"message": str(e)}
            error_msg = f"Error en tabla {table_name}: {error_detail.get('message', str(e))}"
            logger.error(error_msg)
            
            table_stats["status"] = "FAILED"
            table_stats["error"] = error_detail
            self.stats["errors"].append({
                "table": table_name,
                "error": error_detail
            })
            
            if not self.config.get("skip_errors", False):
                raise
            else:
                self.stats["completed_tables"] += 1
                logger.warning(f"Tabla {table_name} omitida debido a errores")
        
        finally:
            table_stats["end_time"] = datetime.now()
            self._update_progress()

    def insert_chunk_safe(self, table_config: Dict, columns: List[str], chunk_data: List[Dict]):
        """Insertar chunk de datos de forma segura"""
        target_table = table_config.get("target_table", table_config['source_table'])
        
        # Aplicar mapeo de columnas si existe
        column_mappings = table_config.get("column_mappings", {})
        logger.info('column_mappings',column_mappings)
        dest_columns = [column_mappings.get(col, col) for col in columns]
        
        # Construir consulta INSERT
        placeholders = ", ".join([f":{col}" for col in columns])
        columns_str = ", ".join(dest_columns)
        insert_query = f"INSERT INTO {target_table} ({columns_str}) VALUES ({placeholders})"
        
        # Ejecutar inserción con manejo de transacción
        try:
            with self.safe_connection(self.target_engine) as conn:
                conn.execute(text(insert_query), chunk_data)
                
        except Exception as e:
            logger.error(f"Error insertando chunk: {str(e)}")
            raise

    def execute_transfer(self) -> Dict:
        """Ejecuta el proceso completo de transferencia"""
        try:
            logger.info(f"Iniciando transferencia para tarea {self.db_task_id}")
            
            # Conectar bases de datos con verificación
            self.connect_databases()
            # self.update_db_status_safe("STARTED", 0)
            
            # Ejecutar transferencia para cada tabla
            for table_config in self.config["tables"]:
                try:
                    self.transfer_table_data(table_config)
                except Exception as e:
                    if not self.config.get("skip_errors", False):
                        raise
                    else:
                        logger.warning(f"Tabla {table_config['source_table']} omitida: {str(e)}")
            
            # Finalización exitosa
            self.stats["end_time"] = datetime.now()
            self.stats["status"] = "COMPLETED"
            # self.update_db_status_safe("SUCCESS", 100)
            
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            logger.info(f"Transferencia completada en {duration:.2f}s: {self.stats['transferred_rows']} filas")
            
            return self.stats
            
        except Exception as e:
            # Manejo de errores globales
            error_detail = parse_sqlalchemy_error(e) if isinstance(e, exc.SQLAlchemyError) else {"message": str(e)}
            error_msg = f"Error en transferencia: {error_detail.get('message', str(e))}"
            logger.exception(error_msg)
            
            self.stats["end_time"] = datetime.now()
            self.stats["status"] = "FAILED"
            self.stats["errors"].append({
                "global_error": error_detail
            })
            # self.update_db_status_safe("FAILURE", error=error_detail)
            raise
        
        finally:
            # Siempre limpiar recursos
            self.disconnect()
            logger.info("Proceso de transferencia finalizado")

    def update_db_status_safe(self, status: str, progress: Optional[float] = None, error: Optional[Dict] = None):
        """Actualiza el estado de la tarea en la base de datos con manejo de errores"""
        try:
            self.update_db_status(status, progress, error)
        except Exception as e:
            logger.error(f"Error actualizando estado en BD: {str(e)}")
            # No re-lanzar el error para no interrumpir el proceso principal

    def update_db_status(self,status: str, progress: Optional[float] = None, error: Optional[Dict] = None):
        """Actualiza el estado de la tarea en la base de datos"""
        #db = get_db#SessionLocal()
        db= Depends(get_db)
        try:
            task = db.query(TaskStatus).get(self.db_task_id)
            if task:
                task.status = status
                if progress is not None:
                    task.progress = progress
                task.result = self.stats
                
                if status == "FAILURE" and error:
                    if not task.errors:
                        task.errors = []
                    task.errors.append(error)
                
                if status == "SUCCESS":
                    task.end_time = datetime.utcnow()
                
                db.commit()
                logger.debug(f"Estado actualizado en BD: {status}")
        except Exception as e:
            logger.error(f"Error actualizando estado en BD: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    def _update_progress(self):
        """Actualiza el progreso en la base de datos y en Celery"""
        # Calcular progreso general
        progress = (self.stats["completed_tables"] / self.stats["total_tables"]) * 100
        
        # Actualizar base de datos de forma segura
        # self.update_db_status_safe("PROGRESS", progress)
        
        # Actualizar estado de Celery
        try:
            self.celery_task.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'stats': self.stats,
                    'current_table': self.current_table,
                }
            )
        except Exception as e:
            logger.error(f"Error actualizando estado Celery: {str(e)}")