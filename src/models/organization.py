# models/organization.py
from pydantic import BaseModel, Field
from typing import Optional

class OrganizationShortView(BaseModel):
    id_organizacion: int
    nif: str
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None

class OrganizationDetail(BaseModel):
    id_organizacion: int
    nif: str
    nombre: str
    descripcion: Optional[str] = None
    iban: Optional[str] = None
    direccion: str
    poblacion: str
    codigo_postal: str
    provincia: Optional[str] = None
    pais: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

class OrganizationCreate(BaseModel):
    nif: str = Field(..., max_length=255)
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    iban: Optional[str] = Field(..., max_length=255)
    direccion: str = Field(..., max_length=255)
    poblacion: str = Field(..., max_length=255)
    codigo_postal: str = Field(..., max_length=10)
    provincia: Optional[str] = Field(None, max_length=255)
    pais: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=50)

class OrganizationUpdate(BaseModel):
    id_organizacion: int
    nif: Optional[str] = Field(None, max_length=255)
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    iban: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = Field(None, max_length=255)
    poblacion: Optional[str] = Field(None, max_length=255)
    codigo_postal: Optional[str] = Field(None, max_length=10)
    provincia: Optional[str] = Field(None, max_length=255)
    pais: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=50)
