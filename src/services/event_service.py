# services/event_service.py
from typing import List, Optional
from models.event import (
    EventShortView,
    EventDetail,
    EventCreate,
    EventUpdate
)
from .api_client import APIClient
from datetime import datetime

class EventService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_events_list(self, year: Optional[int] = None) -> List[EventShortView]:
        """Get list of events, optionally filtered by year"""
        # Si no se especifica año, usar el año actual por defecto
        if year is None:
            year = datetime.now().year
        
        response = self.api.request(
            "GET",
            "/event/events_list",
            query_params={"year": year}
        )
        return [EventShortView(**event) for event in response.json()]
    
    def get_event_details(self, event_id: int) -> EventDetail:
        """Get detailed information about a specific event"""
        response = self.api.request(
            "GET",
            "/event/event_details",
            query_params={"event_id": event_id}
        )
        return EventDetail(**response.json())
    
    def create_event(self, event_data: EventCreate) -> bool:
        """Create a new event"""
        response = self.api.request(
            "POST",
            "/event/create_event",
            json_data=event_data
        )
        return response.status_code == 201
    
    def update_event(self, event_data: EventUpdate) -> bool:
        """Update existing event"""
        response = self.api.request(
            "POST",
            "/event/update_event",
            json_data=event_data
        )
        return response.status_code == 200