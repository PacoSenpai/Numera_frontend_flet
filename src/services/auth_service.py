# services/auth_service.py
from typing import Optional
from models.auth import Token, UserLogin, ChangePasswordRequest
from models.user import UserProfile
from .api_client import APIClient

class AuthService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def login(self, credentials: UserLogin) -> Token:
        """Authenticate user and return token"""
        response = self.api.request(
            "POST",
            "/auth/login",
            json_data=credentials,
            requires_auth=False
        )
        return Token(**response.json())
    
    def get_current_user(self) -> UserProfile:
        """Get current user profile"""
        response = self.api.request("GET", "/user/me")
        return UserProfile(**response.json())
    
    def change_password(self, password_data: ChangePasswordRequest) -> bool:
        """Change user password"""
        response = self.api.request(
            "POST",
            "/user/change_password",
            json_data=password_data
        )
        return response.status_code == 200