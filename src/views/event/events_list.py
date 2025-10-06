# views/events/events_list.py
import flet as ft
from typing import List
from datetime import datetime
from views.base.base_view import BaseView
from views.base.mixins import FilterMixin, PaginationMixin
from models.event import EventShortView
from utils.helpers import create_responsive_columns
from config.constants import Routes


class EventsListView(BaseView, FilterMixin, PaginationMixin):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        FilterMixin.__init__(self)
        PaginationMixin.__init__(self)
        
        self.all_events: List[EventShortView] = []
        self.filtered_events: List[EventShortView] = []
        self.events_container = None
        self.current_year = datetime.now().year
    
    def show(self):
        """Show events list view"""
        self.setup_page_config("Gestión de Eventos")
        self._setup_fab()
        self._load_events(self.current_year)
        self._setup_content()
    
    def _setup_fab(self):
        """Setup floating action button for adding new events"""
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Crear nuevo evento",
            on_click=lambda e: self.router.navigate_to(Routes.EVENT_CREATE)
        )
    
    def _load_events(self, year: int):
        """Load events from API with year filter"""
        result = self.safe_api_call(
            lambda: self.services.events.get_events_list(year),
            loading_message=f"Cargando eventos del {year}..."
        )
        
        if result is not None:  # Asegurarse de que no es None (puede ser lista vacía)
            self.all_events = result
            self.filtered_events = result.copy()
            self.current_year = year
    
    def _setup_content(self):
        """Setup the main content"""
        # Search section
        search_section = self._create_search_section()
        
        # Events container
        self.events_container = ft.Column(spacing=10)
        
        # Main layout
        content = ft.Column([
            search_section,
            ft.Divider(),
            ft.Text(
                f"Eventos del {self.current_year} ({len(self.filtered_events)})",
                style="headlineSmall",
                weight=ft.FontWeight.BOLD
            ),
            ft.Container(
                content=self.events_container,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                padding=10,
                expand=True
            ),
        ], spacing=20, expand=True)
        
        self.page.add(ft.Container(content=content, padding=20, expand=True))
        self._update_events_display()
        self.page.update()
    
    def _create_search_section(self):
        """Create search section with year input and search button"""
        # Year input field
        self.year_input = ft.TextField(
            label="Año",
            value=str(self.current_year),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=120,
            on_submit=lambda e: self._search_events_by_year()
        )
        
        # Search button for year
        year_search_button = ft.ElevatedButton(
            text="Buscar por año",
            icon=ft.Icons.SEARCH,
            on_click=lambda e: self._search_events_by_year()
        )
        
        # Name filter (works locally)
        name_filter = self.create_text_filter(
            "name",
            "Filtrar por nombre",
            "Buscar dentro de los eventos cargados...",
            self._apply_name_filter
        )
        
        # Clear filters button
        clear_button = ft.ElevatedButton(
            text="Limpiar",
            icon=ft.Icons.CLEAR,
            on_click=lambda e: self._clear_filters()
        )
        
        # Responsive layout
        return ft.ResponsiveRow([
            ft.Container(
                ft.Row([
                    self.year_input,
                    year_search_button
                ], spacing=10),
                col={"xs": 12, "md": 6}
            ),
            ft.Container(name_filter, col={"xs": 12, "md": 4}),
            ft.Container(clear_button, col={"xs": 12, "md": 2}),
        ], spacing=10, alignment=ft.MainAxisAlignment.START)
    
    def _search_events_by_year(self):
        """Search events by year (calls API)"""
        year_text = self.year_input.value
        if year_text and year_text.isdigit():
            year = int(year_text)
            # Limpiar filtro de nombre antes de hacer la nueva búsqueda
            self.clear_filters()
            self._load_events(year)
            # No llamar a _apply_name_filter aquí, solo actualizar display
            self._update_events_display()
        else:
            # Si no es un año válido, mostrar error
            self.year_input.error_text = "Ingrese un año válido"
            self.page.update()
    
    def _apply_name_filter(self, filter_key: str = None, filter_value: str = None):
        """Apply name filter locally (no API call)"""
        name_filter = self.get_filter_value("name")
        if name_filter:
            self.filtered_events = [
                event for event in self.all_events
                if name_filter.lower() in event.name.lower()
            ]
        else:
            self.filtered_events = self.all_events.copy()
        
        self._update_events_display()
    
    def _clear_filters(self):
        """Clear all filters and reset to current year"""
        self.clear_filters()
        self.year_input.value = str(self.current_year)
        self.year_input.error_text = None
        # Recargar eventos del año actual
        self._load_events(self.current_year)
        self._update_events_display()
    
    def _update_events_display(self):
        """Update the events display based on current filters"""
        self.events_container.controls.clear()
        
        # Update title with current year and count
        title_text = f"Eventos del {self.current_year} ({len(self.filtered_events)})"
        
        if not self.filtered_events:
            # Determinar el mensaje apropiado
            if self.get_filter_value("name"):
                # Hay filtro de nombre aplicado pero no hay coincidencias
                message = "No se encontraron eventos que coincidan con la búsqueda"
                icon = ft.Icons.SEARCH_OFF
            elif not self.all_events:
                # La API devolvió una lista vacía (no hay eventos para este año)
                message = f"No hay eventos registrados para el año {self.current_year}"
                icon = ft.Icons.EVENT_BUSY
            else:
                # Hay eventos pero el filtro los eliminó todos (caso raro)
                message = "No hay eventos que mostrar"
                icon = ft.Icons.INFO_OUTLINE
            
            self.events_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(icon, size=48, color=ft.Colors.GREY_400),
                        ft.Text(
                            message,
                            style="bodyLarge",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            for event in self.filtered_events:
                event_card = self._create_event_card(event)
                self.events_container.controls.append(event_card)
        
        self.page.update()
    
    def _create_event_card(self, event: EventShortView) -> ft.Card:
        """Create an event card component"""
        # Format date
        date_parts = []
        if event.day:
            date_parts.append(str(event.day))
        if event.month:
            date_parts.append(str(event.month))
        date_parts.append(str(event.year))
        date_str = "/".join(date_parts) if date_parts else str(event.year)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header row with name and date
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.EVENT, color=ft.Colors.PRIMARY),
                            ft.Text(
                                event.name,
                                weight=ft.FontWeight.BOLD,
                                size=16
                            )
                        ], spacing=10),
                        ft.Text(f"Año: {event.year}", size=12, color=ft.Colors.GREY_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Description and date
                    ft.Row([
                        ft.Text(event.description, size=14, expand=True),
                        ft.Text(date_str, size=12, color=ft.Colors.GREY_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Action buttons
                    ft.Row([
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            height=32,
                            on_click=lambda e, ev=event: self._edit_event(ev)
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                    
                ], spacing=10),
                padding=15
            ),
            elevation=2,
            margin=ft.margin.only(bottom=10)
        )
    
    def _edit_event(self, event: EventShortView):
        """Navigate to event edit view"""
        self.page.session.set("selected_event_id", event.event_id)
        self.page.session.set("selected_event_data", event.dict())
        self.page.session.set("edit_mode", False)
        self.router.navigate_to(Routes.EVENT_DETAIL)