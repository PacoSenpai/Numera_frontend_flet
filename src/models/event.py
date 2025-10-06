# models/event.py
# models/event.py
from pydantic import BaseModel, Field
from typing import Optional

class EventShortView(BaseModel):
    """Short view of events for listings"""
    event_id: int
    name: str
    description: str
    year: int
    month: Optional[int] = None
    day: Optional[int] = None

class EventDetail(BaseModel):
    """Detailed view of an event"""
    event_id: int
    name: str
    description: str
    year: int
    month: Optional[int] = None
    day: Optional[int] = None

class EventCreate(BaseModel):
    """Model for event creation"""
    name: str = Field(..., max_length=45)
    description: str = Field(..., max_length=45)
    year: int = Field(..., gt=0)
    month: Optional[int] = Field(None, ge=1, le=12)
    day: Optional[int] = Field(None, ge=1, le=31)

class EventUpdate(BaseModel):
    """Model for event updates"""
    event_id: int
    name: Optional[str] = Field(None, max_length=45)
    description: Optional[str] = Field(None, max_length=45)
    year: Optional[int] = Field(None, gt=0)
    month: Optional[int] = Field(None, ge=1, le=12)
    day: Optional[int] = Field(None, ge=1, le=31)