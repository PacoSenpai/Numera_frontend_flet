# utils/helpers.py
from datetime import datetime, date
from typing import Any, Dict, List, Optional
import flet as ft
from config.constants import Permissions
from services.service_container import ServiceContainer

def format_currency(amount_cents: int) -> str:
    """Format amount in cents to currency string"""
    euros = amount_cents / 100
    return f"{euros:.2f}€"

def format_date(date_obj: Optional[date]) -> str:
    """Format date object to string"""
    if date_obj is None:
        return ""
    return date_obj.strftime("%d/%m/%Y")

def format_datetime(datetime_obj: Optional[datetime]) -> str:
    """Format datetime object to string"""
    if datetime_obj is None:
        return ""
    return datetime_obj.strftime("%d/%m/%Y %H:%M")

def is_mobile(page: ft.Page) -> bool:
    """Check if current device is mobile based on screen width"""
    return page.width < 768 if page.width else False

def is_tablet(page: ft.Page) -> bool:
    """Check if current device is tablet based on screen width"""
    return 768 <= (page.width or 0) < 1024

def create_responsive_columns(mobile_cols: int, tablet_cols: int, desktop_cols: int) -> Dict[str, int]:
    """Create responsive column configuration for Flet"""
    return {
        "xs": mobile_cols,
        "sm": mobile_cols,
        "md": tablet_cols,
        "lg": desktop_cols,
        "xl": desktop_cols
    }

def show_success_message(page: ft.Page, message: str):
    """Show success snack bar"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_700,
    )
    page.open(page.snack_bar)
    page.update()

def show_error_message(page: ft.Page, message: str):
    """Show error snack bar"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_700,
    )
    page.open(page.snack_bar)
    page.update()

def show_info_message(page: ft.Page, message: str):
    """Show info snack bar"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_700,
    )
    page.open(page.snack_bar)
    page.update()


def check_permission(services: ServiceContainer, permission: Permissions) -> bool:
    """Verificar si el usuario tiene un permiso específico"""
    return services.permissions.has_permission(permission.value)

def check_any_permission(services: ServiceContainer, permissions: List[Permissions]) -> bool:
    """Verificar si el usuario tiene al menos uno de los permisos"""
    return services.permissions.has_any_permission([perm.value for perm in permissions])

def check_all_permissions(services: ServiceContainer, permissions: List[Permissions]) -> bool:
    """Verificar si el usuario tiene todos los permisos"""
    return services.permissions.has_all_permissions([perm.value for perm in permissions])

""" Ejemplo:
# En cualquier vista donde necesites verificar permisos
from utils.permission_helpers import check_permission, check_any_permission
from config.permissions import Permissions

class UsersListView(BaseView):
    def _setup_fab(self):
        "Setup floating action button solo si tiene permiso"
        if check_permission(self.services, Permissions.USERS_MANAGE):
            self.page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                tooltip="Crear nuevo usuario",
                on_click=lambda e: self.router.navigate_to(Routes.USER_CREATE)
            )

"""