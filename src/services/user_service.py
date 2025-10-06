# services/user_service.py
from typing import List, Optional, Dict
from models.user import (
    UserShortView, 
    UserDetail, 
    UserCreate, 
    UserUpdate
)
from .api_client import APIClient

class UserService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_users_list(self) -> List[UserShortView]:
        """Get list of all users"""
        response = self.api.request("GET", "/user/users_list")
        return [UserShortView(**user) for user in response.json()]
    
    def get_user_details(self, user_id: int) -> UserDetail:
        """Get detailed information about a specific user"""
        response = self.api.request(
            "GET", 
            "/user/user_details",
            query_params={"user_request_id": user_id}
        )
        return UserDetail(**response.json())
    
    def create_user(self, user_data: UserCreate) -> bool:
        """Create a new user"""
        response = self.api.request(
            "POST",
            "/user/create_user",
            json_data=user_data
        )
        return response.status_code == 201
    
    def update_user(self, user_data: UserUpdate) -> bool:
        """Update existing user"""
        response = self.api.request(
            "POST",
            "/user/user_update",
            json_data=user_data
        )
        return response.status_code == 200
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (admin only)"""
        response = self.api.request(
            "DELETE",
            "/user/delete_user",
            query_params={"user_id_to_delete": user_id}
        )
        return response.status_code == 200
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user"""
        response = self.api.request(
            "POST",
            "/user/deactivate_user",
            query_params={"user_id_to_deactivate": user_id}
        )
        return response.status_code == 200
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user"""
        response = self.api.request(
            "POST",
            "/user/user_update",
            json_data={"ind_estado": 1, "id_usuario": user_id}
        )
        return response.status_code == 200
    
    def create_user_link(self) -> Dict[str, str]:
        """Generate invitation link for user registration"""
        response = self.api.request("POST", "/user/create_user_link")
        return response.json()