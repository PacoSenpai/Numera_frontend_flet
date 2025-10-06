# models/economic.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from .base import BaseDBModel

class EconomicMovementListItem(BaseModel):
    id_movimiento_economico: int
    ind_estado: int
    id_evento: int
    concepto: str
    cantidad_total_ctm: int  # Amount in cents
    imputable_subvencion: bool
    ano_ejercicio: int
    categorias_subvencion_id: int
    usuario_creacion: int
    fecha_creacion: datetime
    usuario_actualizacion: int
    fecha_actualizacion: datetime
    consideraciones: Optional[str] = None
    ind_movimiento: int
    ind_mov_caja: int
    
    @property
    def amount_euros(self) -> float:
        """Convert cents to euros for display"""
        return self.cantidad_total_ctm / 100

class EconomicMovementDetail(EconomicMovementListItem):
    """Same as list item but can be extended with additional detail fields"""
    pass

class EconomicMovementCreate(BaseModel):
    id_evento: int = Field(..., description="ID del evento asociado")
    concepto: str = Field(..., max_length=45, description="Concepto del movimiento")
    cantidad_total_ctm: int = Field(..., ge=0, description="Cantidad total del movimiento en céntimos")
    imputable_subvencion: bool = False
    ano_ejercicio: int = Field(..., gt=0, description="Año del ejercicio")
    categorias_subvencion_id: int = Field(..., gt=0, description="ID de la categoría de subvención")
    consideraciones: Optional[str] = Field(None, max_length=1024, description="Consideraciones adicionales")
    ind_movimiento: int = Field(..., description="12 para entrada, 13 para salida")
    ind_mov_caja: int = Field(15, description="14 para existe en caja, 15 para no existe en caja")

class EconomicMovementUpdate(BaseModel):
    id_evento: Optional[int] = Field(None, description="ID del evento asociado")
    concepto: Optional[str] = Field(None, max_length=45, description="Concepto del movimiento")
    cantidad_total_ctm: Optional[int] = Field(None, ge=0, description="Cantidad total del movimiento en céntimos")
    imputable_subvencion: Optional[bool] = Field(None, description="Imputable a subvención")
    ano_ejercicio: Optional[int] = Field(None, gt=0, description="Año del ejercicio")
    categorias_subvencion_id: Optional[int] = Field(None, gt=0, description="ID de la categoría de subvención")
    consideraciones: Optional[str] = Field(None, max_length=1024, description="Consideraciones adicionales")
    ind_movimiento: Optional[int] = Field(None, description="12 para entrada, 13 para salida")
    ind_estado: Optional[int] = Field(None, description="Estado del movimiento (7, 8, 9)")
    ind_mov_caja: Optional[int] = Field(None, description="14 para existe en caja, 15 para no existe en caja")

class CategoriaSubvencion(BaseModel):
    id_categorias_subvencion: int
    categoria: str
    descripcion: Optional[str] = None
    tipo_categoria: str

# Filters for economic movements
class EconomicMovementFilters(BaseModel):
    fecha_creacion_from: str = Field(..., description="Fecha de creación desde (YYYY-MM-DD)")
    fecha_creacion_to: Optional[str] = Field(None, description="Fecha de creación hasta (YYYY-MM-DD)")
    ind_estado: Optional[int] = Field(None, description="Filtrar por estado (7, 8 o 9)")
    imputable_subvencion: Optional[bool] = Field(None, description="Filtrar por imputable a subvención")
    usuario_actualizacion: Optional[int] = Field(None, description="Filtrar por usuario de actualización")
    id_evento: Optional[int] = Field(None, description="Filtrar por ID de evento")
