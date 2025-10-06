# views/main/home_view.py
import flet as ft
from views.base.base_view import BaseView
from views.base.mixins import FilterMixin
from models.common import Notifications
from utils.helpers import format_datetime
from config.constants import Routes

def create_responsive_columns(sm=12, md=6, lg=4, xl=3):
    """
    Create responsive column configuration for different screen sizes.
    """
    return {
        "xs": 12,
        "sm": sm,
        "md": md,
        "lg": lg,
        "xl": xl
    }


class HomeView(BaseView, FilterMixin):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.notifications = []
        self.reminders = [
            "Revisar movimientos pendientes de aprobación",
            "Actualizar datos de contacto de usuarios",
            "Generar informe mensual de ingresos y gastos"
        ]
    
    def show(self):
        """Show home view"""
        self.setup_page_config("Inicio")
        self._load_data()
        self._setup_content()
    
    def _load_data(self):
        """Load notifications from API"""
        result = self.safe_api_call(
            lambda: self.services.home.get_notifications(),
            loading_message="Cargando notificaciones..."
        )
        
        if result:
            self.notifications = [
                {"id": i, "message": msg}
                for i, msg in enumerate(result.notifications)
            ]
        else:
            self.notifications = [
                {"id": 1, "message": "Error al cargar notificaciones del servidor"}
            ]
    
    def _setup_content(self):
        """Setup home content"""
        # Welcome message
        user_name = self.session_manager.get_user_name() or "Usuario"
        welcome_text = ft.Text(
            f"¡Bienvenido, {user_name}!",
            size=24,
            weight=ft.FontWeight.BOLD
        )
        
        # Notifications section
        notifications_section = self._create_notifications_section()
        
        # Reminders section
        reminders_section = self._create_reminders_section()
        
        # Quick actions section
        quick_actions_section = self._create_quick_actions_section()
        
        # Main content
        content = ft.Column(
            controls=[
                welcome_text,
                ft.Divider(),
                notifications_section,
                ft.Divider(),
                reminders_section,
                ft.Divider(),
                quick_actions_section,
            ],
            spacing=20,
            expand=True
        )
        
        # Add to page in scrollable container
        self.page.add(
            ft.Container(
                content=content,
                padding=20,
                expand=True
            )
        )
        self.page.update()
    
    def _create_notifications_section(self):
        """Create notifications section"""
        notification_cards = []
        
        for notif in self.notifications:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.BLUE),
                        ft.Text(notif["message"], expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e, nid=notif["id"]: self._remove_notification(nid),
                            tooltip="Cerrar notificación"
                        )
                    ]),
                    padding=10
                ),
                elevation=2
            )
            notification_cards.append(card)
        
        if not notification_cards:
            notification_cards.append(
                ft.Text("No hay notificaciones", italic=True, color=ft.Colors.GREY)
            )
        
        return ft.Column([
            ft.Text("Notificaciones", size=18, weight=ft.FontWeight.BOLD),
            *notification_cards
        ])
    
    def _create_reminders_section(self):
        """Create reminders section"""
        reminder_tiles = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.TASK_ALT),
                title=ft.Text(reminder),
                dense=True
            )
            for reminder in self.reminders
        ]
        
        return ft.Column([
            ft.Text("Recordatorios", size=18, weight=ft.FontWeight.BOLD),
            *reminder_tiles
        ])
    
    def _create_quick_actions_section(self):
        """Create quick actions section"""
        actions = [
            {
                "title": "Ver Movimientos",
                "icon": ft.Icons.MONETIZATION_ON,
                "route": Routes.ECONOMY_MOVEMENTS,
                "color": ft.Colors.GREEN
            },
            {
                "title": "Gestionar Usuarios",
                "icon": ft.Icons.PEOPLE,
                "route": Routes.USERS,
                "color": ft.Colors.BLUE
            },
            {
                "title": "Ver Economía",
                "icon": ft.Icons.ANALYTICS,
                "route": Routes.ECONOMY,
                "color": ft.Colors.ORANGE
            },
            {
                "title": "Organizaciones",
                "icon": ft.Icons.APARTMENT,
                "route": Routes.ORGANIZATIONS,
                "color": ft.Colors.PURPLE
            }
        ]
        
        action_buttons = []
        for action in actions:
            button = ft.ElevatedButton(
                content=ft.Column([
                    ft.Icon(action["icon"], size=32, color=action["color"]),
                    ft.Text(action["title"], size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                width=120,
                height=80,
                on_click=lambda e, route=action["route"]: self.router.navigate_to(route)
            )
            action_buttons.append(button)
        
        return ft.Column([
            ft.Text("Acciones Rápidas", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(button, col=create_responsive_columns(6, 4, 3))
                for button in action_buttons
            ])
        ])
    
    def _remove_notification(self, notif_id: int):
        """Remove notification by ID"""
        self.notifications = [n for n in self.notifications if n["id"] != notif_id]
        # Rebuild the page content
        self.page.clean()
        self.setup_page_config("Inicio")
        self._setup_content()