# services/permission_service.py
from typing import List, Dict, Set, Optional
from .api_client import APIClient

class PermissionService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
        self._user_permissions: Set[str] = set()
        self._permissions_loaded = False
    
    def load_user_permissions(self) -> List[str]:
        """Cargar permisos del usuario desde el backend"""
        response = self.api.request(
            "GET",
            "/user/my_permissions"
        )
        permissions = response.json()
        self._user_permissions = set(permissions)
        self._permissions_loaded = True
        return permissions
    
    def has_permission(self, permission: str) -> bool:
        """Verificar si el usuario tiene un permiso específico"""
        if not self._permissions_loaded:
            # Cargar permisos si no están cargados
            self.load_user_permissions()
        return permission in self._user_permissions
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Verificar si el usuario tiene al menos uno de los permisos"""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Verificar si el usuario tiene todos los permisos"""
        return all(self.has_permission(perm) for perm in permissions)
    
    def get_user_permissions(self) -> Set[str]:
        """Obtener todos los permisos del usuario"""
        if not self._permissions_loaded:
            self.load_user_permissions()
        return self._user_permissions.copy()
    
    def clear_permissions(self):
        """Limpiar permisos (útil para logout)"""
        self._user_permissions.clear()
        self._permissions_loaded = False