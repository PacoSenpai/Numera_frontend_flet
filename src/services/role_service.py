# services/role_service.py
from typing import List, Dict, Any
from models.role import Role, UserRole
from .api_client import APIClient

class RoleService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_roles_list(self) -> List[Role]:
        """Get list of all available roles"""
        response = self.api.request("GET", "/roles/roles_list")
        return [Role(**role) for role in response.json()]
    
    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """Get roles assigned to a specific user"""
        response = self.api.request(
            "GET", 
            "/roles/get_user_roles",
            query_params={"user_id": user_id}
        )
        return [UserRole(**role) for role in response.json()]
    
    def add_role_to_user(self, user_id: int, role_id: int) -> bool:
        """Add a role to a user"""
        response = self.api.request(
            "POST",
            "/roles/add_role_to_user",
            json_data={
                "user_id": user_id,
                "role_id": role_id
            }
        )
        return response.status_code == 200
    
    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove a role from a user"""
        response = self.api.request(
            "DELETE",
            "/roles/remove_role_from_user",
            json_data={
                "user_id": user_id,
                "role_id": role_id
            }
        )
        return response.status_code == 200