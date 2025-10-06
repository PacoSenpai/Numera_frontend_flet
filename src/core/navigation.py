# core/navigation.py
import flet as ft
from config.constants import Routes, Permissions

class NavigationMixin:
    """Mixin to provide navigation functionality to views"""
    
    def setup_navigation(self, title: str):
        """Setup AppBar and Navigation Drawer"""
        self.page.appbar = ft.AppBar(
            title=ft.Text(title),
            leading=ft.IconButton(
                ft.Icons.MENU,
                on_click=lambda e: self.page.open(self.page.drawer)
            ),
            center_title=True,
        )
        
        # Definir elementos de navegación con sus permisos requeridos
        nav_items = [
            {
                "label": "Inicio",
                "icon": ft.Icons.HOME,
                "selected_icon": ft.Icons.HOME,
                "route": Routes.HOME,
                "permission": Permissions.HOME
            },
            {
                "label": "Perfil", 
                "icon": ft.Icons.PERSON,
                "selected_icon": ft.Icons.PERSON,
                "route": Routes.PROFILE,
                "permission": Permissions.PROFILE
            },
            {
                "label": "Economía",
                "icon": ft.Icons.MONETIZATION_ON,
                "selected_icon": ft.Icons.MONETIZATION_ON,
                "route": Routes.ECONOMY,
                "permission": Permissions.MOVEMENTS_READ
            },
            {
                "label": "Usuarios",
                "icon": ft.Icons.PEOPLE,
                "selected_icon": ft.Icons.PEOPLE,
                "route": Routes.USERS,
                "permission": Permissions.USERS_LIST
            },
            {
                "label": "Organizaciones",
                "icon": ft.Icons.APARTMENT,
                "selected_icon": ft.Icons.APARTMENT,
                "route": Routes.ORGANIZATIONS,
                "permission": Permissions.ORGANIZATION_LIST
            },
            {
                "label": "Eventos",
                "icon": ft.Icons.EVENT,
                "selected_icon": ft.Icons.EVENT,
                "route": Routes.EVENTS,
                "permission": Permissions.EVENTS_LIST
            },
        ]
        
        # Filtrar elementos basados en permisos
        controls = [ft.Container(height=12)]
        for item in nav_items:
            if (not item["permission"] or 
                self.services.permissions.has_permission(item["permission"].value)):
                controls.append(
                    ft.NavigationDrawerDestination(
                        label=item["label"],
                        icon=item["icon"],
                        selected_icon=item["selected_icon"]
                    )
                )
        
        controls.extend([
            ft.Divider(),
            ft.NavigationDrawerDestination(
                label="Cerrar Sesión",
                icon=ft.Icons.LOGOUT,
                selected_icon=ft.Icons.LOGOUT
            ),
        ])
        
        self.page.drawer = ft.NavigationDrawer(
            controls=controls,
            on_change=self._handle_navigation
        )
    
    def _handle_navigation(self, e):
        """Handle navigation drawer selections"""
        # Reconstruir la lista de rutas filtradas
        nav_items = [
            {"route": Routes.HOME, "permission": Permissions.HOME},
            {"route": Routes.PROFILE, "permission": Permissions.PROFILE},
            {"route": Routes.ECONOMY, "permission": Permissions.MOVEMENTS_READ},
            {"route": Routes.USERS, "permission": Permissions.USERS_LIST},
            {"route": Routes.ORGANIZATIONS, "permission": Permissions.ORGANIZATION_LIST},
            {"route": Routes.EVENTS, "permission": Permissions.EVENTS_LIST},
            None,  # Divider
            Routes.LOGOUT
        ]
        
        # Filtrar rutas basadas en permisos
        filtered_routes = []
        for item in nav_items:
            if item is None:
                filtered_routes.append(None)
            elif item == Routes.LOGOUT:
                filtered_routes.append(Routes.LOGOUT)
            elif (isinstance(item, dict) and self.services.permissions.has_permission(item["permission"].value)):
                filtered_routes.append(item["route"])
        
        selected_index = e.control.selected_index
        if selected_index < len(filtered_routes) and filtered_routes[selected_index]:
            self.router.navigate_to(filtered_routes[selected_index])
