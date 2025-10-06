# core/session_manager.py
import jwt
from datetime import datetime
from typing import Optional
import flet as ft

class SessionManager:
    """Manages user session and authentication state"""
    
    def __init__(self, page: ft.Page):
        self.page = page
    
    def set_session(self, token_data: dict, decoded_token: dict):
        """Store session data"""
        self.page.session.set("access_token", token_data['access_token'])
        self.page.session.set("token_type", token_data['token_type'])
        self.page.session.set("token_exp", decoded_token['exp'])
        self.page.session.set("user_id", decoded_token['sub'])
        self.page.session.set("user_name", f"{decoded_token['nombre']} {decoded_token['apellidos']}")
    
    def get_token(self) -> Optional[str]:
        """Get current authentication token"""
        return self.page.session.get("access_token")
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID"""
        return self.page.session.get("user_id")
    
    def get_user_name(self) -> Optional[str]:
        """Get current user name"""
        return self.page.session.get("user_name")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is valid"""
        token = self.get_token()
        if not token:
            return False
        
        # Check token expiration
        token_exp = self.page.session.get("token_exp")
        if token_exp and datetime.now().timestamp() > token_exp:
            self.clear_session()
            return False
        
        return True
    
    def clear_session(self):
        """Clear all session data"""
        keys_to_clear = ["access_token", "token_type", "token_exp", "user_id", "user_name"]
        for key in keys_to_clear:
            if self.page.session.contains_key(key):
                self.page.session.remove(key)
    
    def decode_token(self, token: str) -> dict:
        """Decode JWT token (without verification for simplicity)"""
        return jwt.decode(token, options={"verify_signature": False})