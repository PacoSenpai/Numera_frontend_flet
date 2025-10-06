# models/common.py
from pydantic import BaseModel
from typing import List

class Notifications(BaseModel):
    notifications: List[str]