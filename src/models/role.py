# models/role.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Role(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None

class UserRole(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    fecha_asignacion: datetime