# app/schemas/transfer.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TableTransferConfig(BaseModel):
    source_table: str
    target_table: Optional[str] = None
    # Limitar filas a transferir
    row_limit: Optional[int] = Field(None, ge=1)
    # Filtrar filas específicas
    where_clause: Optional[str] = None
    # Seleccionar columnas específicas
    selected_columns: Optional[List[str]] = None
    # Transformaciones de columna
    column_mappings: Optional[Dict[str, str]] = None
    # Orden para transferencia consistente
    order_by: Optional[str] = None
    # Modo de escritura (append, truncate, upsert)
    write_mode: str = Field("append", pattern="append|truncate|upsert")
    # Clave para upsert
    upsert_key: Optional[str] = None

class DatabaseConfig(BaseModel):
    server: str
    database: str
    username: str
    password: str
    port: int = 1433

class TransferRequest(BaseModel):
    source: DatabaseConfig
    target: DatabaseConfig
    tables: List[TableTransferConfig]
    chunk_size: int = Field(1000, ge=100)
    max_workers: int = Field(1, ge=1)
    # Opciones avanzadas
    transaction_size: int = Field(1000, ge=1)
    skip_errors: bool = False
    # Callbacks para integración
    on_start: Optional[str] = None
    on_complete: Optional[str] = None
    on_error: Optional[str] = None