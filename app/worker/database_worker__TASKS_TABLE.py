# app/worker/database_worker.py
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from fastapi import Depends
from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine, CursorResult
from app.core.database import SessionLocal, create_db_engine,create_temp_engine, get_db,parse_sqlalchemy_error
from app.models.task import TaskStatus

from sqlalchemy.orm import Session
# Configurar logging
logger = logging.getLogger(__name__)

class DataTransferWorker:
    def __init__(self, transfer_config: Dict, db_task_id: int
                 , celery_task: Any
                 ):
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
        """Usa la misma función que la API para conexiones"""
        try:
            self.source_engine = create_temp_engine(self.config["source"])
            self.target_engine = create_temp_engine(self.config["target"])
            logger.info("Conexiones establecidas con la misma lógica que la API")
        except Exception as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise
    

    def execute_query(self, engine: Engine, query: str, params: dict = None) -> CursorResult:
        logger.info(f"execute_query: {query}")        
        try:
            with engine.begin() as conn:  # Maneja transacción automáticamente
                result = conn.execute(text(query), params or {})
                return result
        except exc.SQLAlchemyError as e:
            error_detail = parse_sqlalchemy_error(e)
            logger.error(f"Error en consulta: {query[:100]}... | {error_detail}")
            raise
        
    

    def build_select_query(self, table_config: Dict) -> str:
        """
        Construye la consulta SELECT para la tabla de origen
        considerando límites, filtros y selección de columnas
        """
        logger.info("build_select_query")
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

    def build_insert_query(self, table_config: Dict, columns: List[str]) -> str:
        """
        Construye la consulta INSERT para la tabla de destino
        considerando mapeo de columnas y modo de escritura
        """
        logger.info("build_select_query")
        target_table = table_config.get("target_table", table_config['source_table'])
        
        # Aplicar mapeo de columnas si existe
        column_mappings = table_config.get("column_mappings", {})
        dest_columns = [column_mappings.get(col, col) for col in columns]
        
        # Modos de escritura especiales
        write_mode = table_config.get("write_mode", "append")
        
        # TRUNCATE: Vaciar tabla antes de insertar
        if write_mode == "truncate":
            logger.info(f"Truncando tabla {target_table}")
            self.execute_query(self.target_engine, f"TRUNCATE TABLE {target_table}")
        
        # UPSERT: Preparar consulta MERGE
        if write_mode == "upsert" and table_config.get("upsert_key"):
            return self._build_merge_statement(table_config, columns, dest_columns)
        
        # INSERT estándar
        placeholders = ", ".join([f":{col}" for col in columns])
        columns_str = ", ".join(dest_columns)
        return f"INSERT INTO {target_table} ({columns_str}) VALUES ({placeholders})"

    def _build_merge_statement(self, table_config: Dict, 
                              source_cols: List[str], 
                              dest_cols: List[str]) -> str:
        """Construye consulta MERGE para UPSERT (MSSQL)"""
        target_table = table_config.get("target_table", table_config['source_table'])
        upsert_key = table_config["upsert_key"]
        
        # Mapear clave de upsert
        dest_key = table_config.get("column_mappings", {}).get(upsert_key, upsert_key)
        
        # Construir partes de la consulta
        source_cols_str = ", ".join(source_cols)
        dest_cols_str = ", ".join(dest_cols)
        update_set = ", ".join([f"target.{col} = source.{col}" for col in dest_cols])
        insert_cols = ", ".join([f"source.{col}" for col in dest_cols])
        
        return f"""
        MERGE INTO {target_table} AS target
        USING (VALUES ({', '.join([f':{col}' for col in source_cols])})) 
        AS source ({source_cols_str})
        ON target.{dest_key} = source.{upsert_key}
        WHEN MATCHED THEN
            UPDATE SET {update_set}
        WHEN NOT MATCHED THEN
            INSERT ({dest_cols_str}) VALUES ({insert_cols});
        """

    def fetch_data_in_chunks(self, query: str, chunk_size: int) -> List[Dict]:
        """Obtiene datos en chunks usando cursor server-side"""
        data = []
        try:
            with self.source_engine.connect() as conn:
                result = conn.execution_options(stream_results=True).execute(text(query))
                
                while True:
                    chunk = result.fetchmany(chunk_size)
                    if not chunk:
                        break
                    
                    # Convertir a lista de diccionarios
                    columns = result.keys()
                    data.extend([dict(zip(columns, row)) for row in chunk])
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error obteniendo datos: {parse_sqlalchemy_error(e)}")
            raise
        
        return data

    def transfer_table_data(self, table_config: Dict):
        """Transferencia completa para una tabla individual"""
        table_name = table_config["source_table"]
        self.current_table = table_name
        logger.info(f"Iniciando transferencia para tabla: {table_name}")
        
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
            logger.info(f"select_query: {select_query}")
            # Obtener total de filas
            count_query = f"SELECT COUNT(*) FROM ({select_query}) AS total_rows"
            total_rows = self.execute_query(
                self.source_engine, 
                count_query
            ).scalar()
            
            table_stats["total_rows"] = total_rows
            self.stats["total_rows"] += total_rows
            
            # Construir consulta de inserción
            # Primero necesitamos obtener los nombres de las columnas
            with self.source_engine.connect() as conn:
                sample_result = conn.execute(text(f"{select_query} WHERE 1=0"))
                source_columns = sample_result.keys()
            
            insert_query = self.build_insert_query(table_config, source_columns)
            
            # Transferir datos por chunks
            chunk_size = self.config["chunk_size"]
            transferred = 0
            start_time = time.time()
            
            # Obtener datos en chunks
            for offset in range(0, total_rows, chunk_size):
                chunk_query = f"""
                    SELECT * FROM (
                        {select_query}
                    ) AS src
                    ORDER BY (SELECT NULL)
                    OFFSET {offset} ROWS
                    FETCH NEXT {chunk_size} ROWS ONLY
                """
                
                try:
                    # Obtener chunk de datos
                    chunk_data = self.fetch_data_in_chunks(chunk_query, chunk_size)
                    if not chunk_data:
                        break
                    
                    # Insertar chunk
                    with self.target_engine.begin() as conn:  # Transacción automática
                        conn.execute(text(insert_query), chunk_data)
                    
                    # Actualizar estadísticas
                    transferred += len(chunk_data)
                    table_stats["transferred"] = transferred
                    self.stats["transferred_rows"] += len(chunk_data)
                    
                    # Calcular rendimiento
                    elapsed = time.time() - start_time
                    rows_per_sec = transferred / elapsed if elapsed > 0 else 0
                    logger.debug(f"{table_name}: {transferred}/{total_rows} filas ({rows_per_sec:.1f} filas/seg)")
                    
                except exc.SQLAlchemyError as e:
                    # Manejar errores según configuración
                    error_detail = parse_sqlalchemy_error(e)
                    if self.config["skip_errors"]:
                        logger.warning(f"Error en chunk: {error_detail['message']}")
                        table_stats["errors"] += len(chunk_data)
                        self.stats["warnings"].append({
                            "table": table_name,
                            "chunk": offset // chunk_size,
                            "error": error_detail
                        })
                    else:
                        raise
                
                # Actualizar progreso periódicamente
                if transferred % (chunk_size * 5) == 0:  # Actualizar cada 5 chunks
                    self._update_progress()
            
            # Finalización exitosa
            table_stats["status"] = "COMPLETED"
            self.stats["completed_tables"] += 1
            logger.info(f"Tabla {table_name} transferida: {transferred}/{total_rows} filas")
            
        except Exception as e:
            # Manejo de errores para la tabla
            error_detail = parse_sqlalchemy_error(e) if isinstance(e, exc.SQLAlchemyError) else {"message": str(e)}
            error_msg = f"Error en tabla {table_name}: {error_detail['message']}"
            logger.error(error_msg)
            table_stats["status"] = "FAILED"
            table_stats["error"] = error_detail
            self.stats["errors"].append({
                "table": table_name,
                "error": error_detail
            })
            
            if not self.config["skip_errors"]:
                raise
            else:
                self.stats["completed_tables"] += 1
                logger.warning(f"Tabla {table_name} omitida debido a errores")
        
        finally:
            table_stats["end_time"] = datetime.now()
            # Actualizar progreso final de la tabla
            self._update_progress()

    def execute_transfer(self) -> Dict:
        """Ejecuta el proceso completo de transferencia"""
        try:
            logger.info(f"Iniciando transferencia para tarea {self.db_task_id}")
            self.connect_databases()
            self.update_db_status("STARTED", 0)
            
            # Ejecutar transferencia para cada tabla
            for table_config in self.config["tables"]:
                self.transfer_table_data(table_config)
            
            # Finalización exitosa
            self.stats["end_time"] = datetime.now()
            self.stats["status"] = "COMPLETED"
            self.update_db_status("SUCCESS", 100)
            logger.info(f"Transferencia completada: {self.stats['transferred_rows']} filas transferidas")
            return self.stats
            
        except Exception as e:
            # Manejo de errores globales
            error_detail = parse_sqlalchemy_error(e) if isinstance(e, exc.SQLAlchemyError) else {"message": str(e)}
            error_msg = f"Error global: {error_detail['message']}"
            logger.exception(error_msg)
            self.stats["end_time"] = datetime.now()
            self.stats["status"] = "FAILED"
            self.stats["errors"].append({
                "global_error": error_detail
            })
            self.update_db_status("FAILURE", error=error_detail)
            raise
        
        finally:
            logger.info("Proceso de transferencia finalizado")

    def update_db_status(self, status: str, progress: Optional[float] = None, error: Optional[Dict] = None):
        """Actualiza el estado de la tarea en la base de datos"""
        db = SessionLocal()  # Crear sesión directamente
        try:
            task = db.query(TaskStatus).get(self.db_task_id)
            if task:
                task.status = status
                if progress is not None:
                    task.progress = progress
                task.result = self.stats  # Guardar estadísticas completas
                
                if status == "FAILURE" and error:
                    if not task.errors:
                        task.errors = []
                    task.errors.append(error)
                
                if status == "SUCCESS":
                    task.end_time = datetime.utcnow()  # Usar UTC para consistencia
                
                db.commit()
                logger.debug(f"Estado actualizado en BD: {status} - Progreso: {progress}%")
        except Exception as e:
            logger.error(f"Error actualizando estado en BD: {str(e)}")
            db.rollback()
        finally:
            db.close()

    def _update_progress(self):
        """Actualiza el progreso en la base de datos y en Celery"""
        # Calcular progreso general
        progress = (self.stats["completed_tables"] / self.stats["total_tables"]) * 100
        
        # Actualizar base de datos
        self.update_db_status("PROGRESS", progress)
        
        # Actualizar estado de Celery
        self.celery_task.update_state(
            state='PROGRESS',
            meta={
                'progress': progress,
                'stats': self.stats,
                'current_table': self.current_table,
            }
        )