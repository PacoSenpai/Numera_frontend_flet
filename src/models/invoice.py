# models/invoice.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class FacturaListItem(BaseModel):
    id_factura: int
    nombre: str
    ind_computable: int
    cantidad_ctm: int
    fecha_emision_factura: Optional[date] = None
    id_emisor: Optional[int] = None
    id_beneficiario: Optional[int] = None
    id_movimiento_economico: int
    cod_factura_externo: Optional[str] = None
    fecha_creacion: datetime
    usuaio_creacion: int  # Note: this has a typo in the API
    
    @property
    def amount_euros(self) -> float:
        """Convert cents to euros for display"""
        return self.cantidad_ctm / 100

class FacturaCreate(BaseModel):
    id_movimiento_economico: int = Field(..., description="ID del movimiento económico asociado")
    nombre: str = Field(..., description="nombre de la operación")
    ind_computable: int = Field(..., description="10 para computa, 11 para no computa")
    cantidad_ctm: int = Field(..., ge=0, description="Cantidad en céntimos")
    fecha_emision_factura: Optional[str] = Field(None, description="Fecha de emisión de la factura")
    id_emisor: Optional[int] = Field(None, description="ID de la organización emisora")
    id_beneficiario: Optional[int] = Field(None, description="ID de la organización beneficiaria")
    cod_factura_externo: Optional[str] = Field(None, description="Código externo de la factura")

class FacturaUpdate(BaseModel):
    ind_computable: Optional[int] = Field(None, description="10 para computa, 11 para no computa")
    nombre: Optional[str] = Field(..., description="nombre de la operación")
    cantidad_ctm: Optional[int] = Field(None, ge=0, description="Cantidad en céntimos")
    fecha_emision_factura: Optional[str] = Field(None, description="Fecha de emisión de la factura")
    id_emisor: Optional[int] = Field(None, description="ID de la organización emisora")
    id_beneficiario: Optional[int] = Field(None, description="ID de la organización beneficiaria")
    cod_factura_externo: Optional[str] = Field(None, description="Código externo de la factura")