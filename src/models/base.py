# models/base.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseDBModel(BaseModel):
    """Base model for database entities"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True
