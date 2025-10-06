# views/economy/economy_dashboard.py
import flet as ft
from views.base.base_view import BaseView
from config.constants import Routes
from utils.helpers import format_currency, create_responsive_columns


class EconomyDashboard(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.summary_data = None
    
    def show(self):
        """Show economy dashboard"""
        self.setup_page_config("Economía")
        self._load_summary_data()
        self._setup_content()
    
    def _load_summary_data(self):
        """Load summary data (mock data since endpoint not implemented)"""
        # This would normally call an API endpoint for annual summary
        # For now, we'll create mock data
        self.summary_data = {
            "year": 2024,
            "total_income": 50000,  # in cents
            "total_expenses": 35000,  # in cents
            "balance": 15000,  # in cents
            "movements_count": 156,
            "pending_approval": 8,
            "subvention_income": 25000,  # in cents
            "subvention_expenses": 20000  # in cents
        }
    
    def _setup_content(self):
        """Setup dashboard content"""
        # Summary cards
        summary_section = self._create_summary_section()
        
        # Quick actions
        actions_section = self._create_actions_section()
        
        # Recent activity (would load from API)
        activity_section = self._create_recent_activity_section()
        
        # Main layout
        content = ft.Column([
            ft.Text(f"Resumen Anual {self.summary_data['year']}", 
                   style="headlineMedium", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            summary_section,
            ft.Divider(),
            actions_section,
            ft.Divider(),
            activity_section
        ], spacing=20)
        
        self.page.add(
            ft.Container(
                content=ft.ListView(controls=[content], expand=True),
                padding=20,
                expand=True
            )
        )
        self.page.update()
    
    def _create_summary_section(self):
        """Create summary cards section"""
        cards = [
            self._create_summary_card(
                "Ingresos Totales",
                format_currency(self.summary_data['total_income']),
                ft.Icons.TRENDING_UP,
                ft.Colors.GREEN
            ),
            self._create_summary_card(
                "Gastos Totales",
                format_currency(self.summary_data['total_expenses']),
                ft.Icons.TRENDING_DOWN,
                ft.Colors.RED
            ),
            self._create_summary_card(
                "Balance",
                format_currency(self.summary_data['balance']),
                ft.Icons.ACCOUNT_BALANCE,
                ft.Colors.BLUE
            ),
            self._create_summary_card(
                "Movimientos",
                str(self.summary_data['movements_count']),
                ft.Icons.LIST_ALT,
                ft.Colors.PURPLE
            )
        ]
        
        return ft.ResponsiveRow([
            ft.Container(card, col=create_responsive_columns(12, 6, 3))
            for card in cards
        ])
    
    def _create_summary_card(self, title: str, value: str, icon, color):
        """Create a summary card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=32, color=color),
                        ft.Column([
                            ft.Text(title, size=14, color=ft.Colors.GREY_600),
                            ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color)
                        ], spacing=2, expand=True)
                    ], spacing=15)
                ]),
                padding=20
            ),
            elevation=3
        )
    
    def _create_actions_section(self):
        """Create quick actions section"""
        actions = [
            {
                "title": "Ver Movimientos",
                "subtitle": "Gestionar movimientos económicos",
                "icon": ft.Icons.LIST,
                "route": Routes.ECONOMY_MOVEMENTS,
                "color": ft.Colors.BLUE
            },
            {
                "title": "Estadísticas",
                "subtitle": "Ver informes y gráficos",
                "icon": ft.Icons.ANALYTICS,
                "route": Routes.ECONOMY_STATISTICS,
                "color": ft.Colors.ORANGE
            },
            {
                "title": "Crear Movimiento",
                "subtitle": "Nuevo ingreso o gasto",
                "icon": ft.Icons.ADD_CIRCLE,
                "route": Routes.ECONOMY_MOVEMENT_CREATE,
                "color": ft.Colors.GREEN
            }
        ]
        
        action_cards = []
        for action in actions:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(action["icon"], size=40, color=action["color"]),
                            ft.Column([
                                ft.Text(action["title"], weight=ft.FontWeight.BOLD),
                                ft.Text(action["subtitle"], size=12, color=ft.Colors.GREY_600)
                            ], expand=True)
                        ]),
                        ft.ElevatedButton(
                            "Acceder",
                            on_click=lambda e, route=action["route"]: self.router.navigate_to(route),
                            width=float("inf")
                        )
                    ], spacing=15),
                    padding=20
                ),
                elevation=2
            )
            action_cards.append(card)
        
        return ft.Column([
            ft.Text("Acciones Rápidas", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(card, col=create_responsive_columns(12, 6, 4))
                for card in action_cards
            ])
        ])
    
    def _create_recent_activity_section(self):
        """Create recent activity section"""
        # Mock recent activities
        activities = [
            "Movimiento 'Pago proveedor material' creado",
            "Factura asociada al movimiento #123",
            "Movimiento 'Subvención recibida' confirmado",
            "Usuario Juan Pérez actualizado"
        ]
        
        activity_tiles = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.BLUE),
                title=ft.Text(activity, size=14),
                dense=True
            )
            for activity in activities
        ]
        
        return ft.Column([
            ft.Text("Actividad Reciente", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(activity_tiles),
                    padding=10
                ),
                elevation=2
            )
        ])