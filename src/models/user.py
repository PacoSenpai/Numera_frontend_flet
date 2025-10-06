# models/user.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from .base import BaseDBModel

class UserProfile(BaseModel):
    name: str
    surname: str
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str
    nif_nie: str
    birth_date: date
    signup_date: date
    address: Optional[str] = None
    city: Optional[str] = None
    social_security: Optional[str] = None
    account_holder: str
    iban: str
    parent1_name: Optional[str] = None
    parent2_name: Optional[str] = None
    parent1_id: Optional[str] = None
    parent2_id: Optional[str] = None
    parent1_phone: Optional[str] = None
    parent2_phone: Optional[str] = None
    parent1_email: Optional[str] = None
    parent2_email: Optional[str] = None
    notes: Optional[str] = None

class UserShortView(BaseModel):
    id_user: int
    name: str
    surname: str
    nif_nie: str
    email: str
    phone: str
    ind_estado: str
    ind_cre: Optional[str] = None
    ind_rgcre: Optional[str] = None
    parent1_id: Optional[str] = None
    parent2_id: Optional[str] = None

class UserDetail(UserProfile):
    id_user: int
    ind_estado: str
    ind_cre: str
    ind_rgcre: str
    direct_debit_reference: str
    created_by: int
    creation_date: datetime
    updated_by: int
    update_date: datetime

class UserCreate(BaseModel):
    nombre: str = Field(..., max_length=64)
    apellidos: str = Field(..., max_length=255)
    nif_nie: str = Field(..., max_length=45)
    password: str
    fecha_nacimiento: str
    domicilio: Optional[str] = Field(None, max_length=255)
    poblacion: Optional[str] = Field(None, max_length=255)
    telefono: str = Field(..., max_length=45)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    titular_cuenta: str = Field(..., max_length=255)
    iban: str = Field(..., max_length=45)
    numero_ss: Optional[str] = Field(None, max_length=45)
    nombre_progenitor1: Optional[str] = Field(None, max_length=255)
    nombre_progenitor2: Optional[str] = Field(None, max_length=255)
    nif_nie_progenitor1: Optional[str] = Field(None, max_length=45)
    nif_nie_progenitor2: Optional[str] = Field(None, max_length=45)
    telefono_progenitor1: Optional[str] = Field(None, max_length=45)
    telefono_progenitor2: Optional[str] = Field(None, max_length=45)
    email_progenitor1: Optional[str] = None
    email_progenitor2: Optional[str] = None
    path_derechos_imagen: Optional[str] = Field(None, max_length=1024)
    consideraciones: Optional[str] = Field(None, max_length=1024)
    ind_cre: int = Field(1, ge=0)
    ind_rgcre: int = Field(1, ge=0)
    ind_estado: int = Field(1, ge=0)

class UserUpdate(BaseModel):
    id_usuario: int
    nombre: Optional[str] = Field(None, max_length=64)
    apellidos: Optional[str] = Field(None, max_length=255)
    nif_nie: Optional[str] = Field(None, max_length=45)
    ind_estado: Optional[int] = Field(None, ge=0)
    ind_cre: Optional[int] = Field(None, ge=0)
    ind_rgcre: Optional[int] = Field(None, ge=0)
    fecha_nacimiento: Optional[date] = None
    domicilio: Optional[str] = Field(None, max_length=255)
    poblacion: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=45)
    email: Optional[str] = None
    numero_ss: Optional[str] = Field(None, max_length=45)
    titular_cuenta: Optional[str] = Field(None, max_length=255)
    iban: Optional[str] = Field(None, max_length=45)
    nombre_progenitor1: Optional[str] = Field(None, max_length=255)
    nombre_progenitor2: Optional[str] = Field(None, max_length=255)
    nif_nie_progenitor1: Optional[str] = Field(None, max_length=45)
    nif_nie_progenitor2: Optional[str] = Field(None, max_length=45)
    telefono_progenitor1: Optional[str] = Field(None, max_length=45)
    telefono_progenitor2: Optional[str] = Field(None, max_length=45)
    email_progenitor1: Optional[str] = None
    email_progenitor2: Optional[str] = None
    consideraciones: Optional[str] = Field(None, max_length=1024)

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=128, description="Current password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")
