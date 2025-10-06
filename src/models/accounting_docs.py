# models/accounting_docs.py
from pydantic import BaseModel, Field
from typing import Optional

class DocsContablesListItem(BaseModel):
    """Modelo para listar documentos contables"""
    id_docs_contables: int
    nombre: str
    path: str
    id_movimiento_economico: int

class DocsContablesUpdate(BaseModel):
    """Modelo para actualización de documentos contables"""
    nombre: Optional[str] = Field(None, description="Nuevo nombre del documento contable")