# core/router.py
from typing import Dict, Type, Any, Optional
import flet as ft
from config.constants import Routes
from .session_manager import SessionManager
from services.service_container import ServiceContainer
from config.constants import ROUTE_PERMISSIONS, Permissions


class Router:
    """Enhanced router with dependency injection and session management"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.session_manager = SessionManager(page)
        self.services = ServiceContainer()
        self.services.set_session_manager(self.session_manager)
        
        self.routes: Dict[str, Type] = {}
        self.current_view: Optional[Any] = None
        self._register_routes()
    
    def _register_routes(self):
        """Register all application routes"""
        # Import views here to avoid circular imports
        from views.auth.login_view import LoginView
        from views.main.home_view import HomeView
        from views.main.profile_view import ProfileView
        from views.economy.economy_dashboard import EconomyDashboard
        from views.economy.movements_list import MovementsListView
        from views.economy.movement_detail import MovementDetailView
        from views.economy.movement_create import MovementCreateView
        from views.users.users_list import UsersListView
        from views.users.user_detail import UserDetailView
        from views.users.user_form import UserFormView
        from views.organization.organization_list import OrganizationsListView
        from views.organization.organization_detail import OrganizationDetailView
        from views.organization.organization_form import OrganizationFormView
        from views.event.events_list import EventsListView
        from views.event.event_detail import EventDetailView
        from views.event.event_form import EventFormView
        
        self.routes = {
            Routes.LOGIN: LoginView,
            Routes.HOME: HomeView,
            Routes.PROFILE: ProfileView,
            Routes.ECONOMY: EconomyDashboard,
            Routes.ECONOMY_MOVEMENTS: MovementsListView,
            Routes.ECONOMY_MOVEMENT_DETAIL: MovementDetailView,
            Routes.ECONOMY_MOVEMENT_CREATE: MovementCreateView,
            Routes.USERS: UsersListView,
            Routes.USER_DETAIL: UserDetailView,
            Routes.USER_CREATE: UserFormView,
            Routes.ORGANIZATIONS: OrganizationsListView,
            Routes.ORGANIZATION_DETAIL: OrganizationDetailView,
            Routes.ORGANIZATION_CREATE: OrganizationFormView,
            Routes.EVENTS: EventsListView,
            Routes.EVENT_DETAIL: EventDetailView,
            Routes.EVENT_CREATE: EventFormView,
        }
    
    def navigate_to(self, route: str, **kwargs):
        """Navigate to a specific route with optional parameters"""
        # Handle logout
        if route == Routes.LOGOUT:
            self._handle_logout()
            return
        
        # Check authentication for protected routes
        if route != Routes.LOGIN and not self.session_manager.is_authenticated():
            self.navigate_to(Routes.LOGIN)
            return
    
         # Check permissions for the route
        if route != Routes.LOGIN and not self._check_route_permissions(route):
            self._show_error("No tienes permisos para acceder a esta página.")
            return
        
        # Navigate to route
        if route in self.routes:
            self._show_view(route, **kwargs)
        else:
            self._show_error(f"Route not found: {route}")
    
    def _check_route_permissions(self, route: str) -> bool:
        """Check if user has required permissions for the route"""
        if route not in ROUTE_PERMISSIONS:
            return True  # Si la ruta no tiene permisos definidos, permitir acceso
        
        required_permissions = ROUTE_PERMISSIONS[route]
        return self.services.permissions.has_any_permission(
            [perm.value for perm in required_permissions]
        )
    
    def _show_view(self, route: str, **kwargs):
        """Show the specified view"""
        try:
            # Clear current page
            self.page.clean()
            
            # Create and show new view
            view_class = self.routes[route]
            self.current_view = view_class(
                page=self.page,
                router=self,
                services=self.services,
                session_manager=self.session_manager,
                **kwargs
            )
            
            if hasattr(self.current_view, 'show'):
                self.current_view.show()
                    
        except Exception as e:
            self._show_error(f"Error loading view: {str(e)}")
    
    def _handle_logout(self):
        """Handle user logout"""
        self.session_manager.clear_session()
        self.services.api_client.clear_token()
        self.services.permissions.clear_permissions()
        self.page.clean()
        self.navigate_to(Routes.LOGIN)
    
    def _show_error(self, message: str):
        """Show error message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700,
        )
        self.page.open(self.page.snack_bar)
        self.page.update()
    
    def get_current_route(self) -> Optional[str]:
        """Get current active route"""
        if self.current_view:
            return getattr(self.current_view, 'route', None)
        return None
