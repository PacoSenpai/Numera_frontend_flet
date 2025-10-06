# services/home_service.py
from models.common import Notifications
from .api_client import APIClient

class HomeService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_notifications(self) -> Notifications:
        """Get home notifications"""
        response = self.api.request("GET", "/home/notifications")
        return Notifications(**response.json())
