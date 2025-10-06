import flet as ft
from datetime import datetime, date
from typing import List, Optional
from views.base.base_view import BaseView
from views.base.mixins import FilterMixin, PaginationMixin
from models.economic import EconomicMovementListItem, EconomicMovementFilters
from config.constants import Routes, MovementType, MovementState, CashBoxState
from utils.helpers import format_currency, format_datetime, create_responsive_columns, show_error_message, show_success_message


class MovementsListView(BaseView, FilterMixin, PaginationMixin):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        FilterMixin.__init__(self)
        PaginationMixin.__init__(self)
        
        self.movements: List[EconomicMovementListItem] = []
        self.movements_table = None
        self.is_mobile = False
        self.events = []
        self.selected_year = datetime.now().year
        
        # Date pickers
        self.date_picker_desde = ft.DatePicker(
            first_date=date(2020, 1, 1),
            last_date=date(2030, 12, 31),
            on_change=self._on_date_desde_change
        )
        
        self.date_picker_hasta = ft.DatePicker(
            first_date=date(2020, 1, 1),
            last_date=date(2030, 12, 31),
            on_change=self._on_date_hasta_change
        )
        
        # Filter state
        self.filters = {
            "fecha_desde": date.today().replace(day=1),  # First day of current month
            "fecha_hasta": date.today(),
            "estado": None,
            "imputable": None,
            "usuario": None,
            "evento": None
        }
        
        # UI controls
        self.event_dropdown = None
        self.year_dropdown = None
    
    def show(self):
        """Show movements list view"""
        # Add date pickers to page overlay
        self.page.overlay.extend([self.date_picker_desde, self.date_picker_hasta])

            
        self.setup_page_config("Movimientos Económicos")
        self.is_mobile = self.page.width < 768 if self.page.width else False
        self._setup_fab()
        self._load_initial_data()
        self._load_events()
        self._setup_content()
    
    def _setup_fab(self):
        """Setup floating action button for creating new movements"""
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Crear nuevo movimiento",
            on_click=lambda e: self._create_new_movement()
        )
    
    def _load_initial_data(self):
        """Load initial movements data"""
        # Load recent movements by default
        result = self.safe_api_call(
            lambda: self.services.economic.get_last_movements(),
            loading_message="Cargando movimientos recientes..."
        )
        
        if result:
            self.movements = result
    
    def _load_events(self):
        """Load events for the selected year"""
        result = self.safe_api_call(
            lambda: self.services.events.get_events_list(self.selected_year),
            loading_message="Cargando eventos..."
        )
        
        self.events = result
        self._update_event_dropdown()
    
    def _update_event_dropdown(self):
        """Update event dropdown options"""
        if self.event_dropdown:
            # Clear existing options
            self.event_dropdown.options.clear()
            
            # Add "All" option
            self.event_dropdown.options.append(ft.dropdown.Option(key="0", text="Todos"))
            
            # Add events for selected year
            for event in self.events:
                event_date = f"{event.day}/{event.month}" if event.day and event.month else "Sin fecha"
                self.event_dropdown.options.append(
                    ft.dropdown.Option(
                        key=str(event.event_id), 
                        text=f"{event.name} ({event_date})"
                    )
                )
            
            # Reset selected value
            self.event_dropdown.value = self.filters["evento"] or "0"
            self.page.update()
    
    def _setup_content(self):
        """Setup the main content"""
        # Back button and title
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Volver al dashboard",
                on_click=lambda e: self.router.navigate_to(Routes.ECONOMY)
            ),
            ft.Text("Movimientos Económicos", style="headlineMedium", weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.START)
        
        # Filters section
        filters_section = self._create_filters_section()
        
        # Movements display
        if self.is_mobile:
            movements_display = self._create_mobile_cards()
        else:
            movements_display = self._create_desktop_table()
        
        # Main layout
        content = ft.Column([
            header,
            ft.Divider(),
            filters_section,
            ft.Divider(),
            ft.Row([
                ft.Text(
                    f"Lista de movimientos:",
                    style="titleSmall",
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Recargar",
                    on_click=lambda e: self._refresh_data()
                )
            ]),
            ft.Container(
                content=movements_display,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                padding=10,
                expand=True
            )
        ], spacing=20, expand=True)
        
        self.page.add(ft.Container(content=content, padding=20, expand=True))
        self.page.update()
    
    def _create_filters_section(self):
        """Create filters section with uniform dynamic width"""
        # Definir etiquetas usadas
        labels = [
            "Fecha desde",
            "Fecha hasta",
            "Estado",
            "Imputable a subvención",
            "Año eventos",
            "Evento",
            "Aplicar",
            "Limpiar"
        ]
        
        # Aproximación: ~9-10px por carácter + margen extra
        max_width = max(len(label) for label in labels) * 10 + 80
        FILTER_WIDTH = max_width

        # Date filters
        self.fecha_desde_btn = ft.ElevatedButton(
            text=f"Desde: {self.filters['fecha_desde'].strftime('%d-%m-%Y')}",
            icon=ft.Icons.CALENDAR_MONTH,
            width=FILTER_WIDTH,
            on_click=lambda e: self.page.open(self.date_picker_desde)
        )
        
        self.fecha_hasta_btn = ft.ElevatedButton(
            text=f"Hasta: {self.filters['fecha_hasta'].strftime('%d-%m-%Y')}",
            icon=ft.Icons.CALENDAR_MONTH,
            width=FILTER_WIDTH,
            on_click=lambda e: self.page.open(self.date_picker_hasta)
        )
        
        # Estado filter
        status_options = [
            ft.dropdown.Option(key="0", text="Todos"),
            ft.dropdown.Option(key=str(MovementState.DRAFT.value), text="Borrador"),
            ft.dropdown.Option(key=str(MovementState.PENDING_REVIEW.value), text="Pendiente Revisión"),
            ft.dropdown.Option(key=str(MovementState.REVIEWED.value), text="Revisado")
        ]
        
        estado = ft.Dropdown(
            label="Estado",
            options=status_options,
            value=self.filters["estado"] or "",
            width=FILTER_WIDTH,
            on_change=lambda e: self._update_filter("estado", e.control.value)
        )
        
        # Imputable filter
        imputable_options = [
            ft.dropdown.Option(key="0", text="Todos"),
            ft.dropdown.Option(key="true", text="Sí"),
            ft.dropdown.Option(key="false", text="No")
        ]
        
        imputable = ft.Dropdown(
            label="Imputable a subvención",
            options=imputable_options,
            value=self.filters["imputable"] or "",
            width=FILTER_WIDTH,
            on_change=lambda e: self._update_filter("imputable", e.control.value)
        )
        
        # Year selector
        current_year = datetime.now().year
        year_options = [ft.dropdown.Option(key=str(y), text=str(y)) for y in range(current_year - 5, current_year + 2)]
        
        self.year_dropdown = ft.Dropdown(
            label="Año eventos",
            value=str(self.selected_year),
            options=year_options,
            width=FILTER_WIDTH,
            on_change=self._on_year_change
        )
        
        # Event filter
        event_options = [ft.dropdown.Option(key="0", text="Todos")]
        for event in self.events:
            event_date = f"{event.day}/{event.month}" if event.day and event.month else "Sin fecha"
            event_options.append(
                ft.dropdown.Option(
                    key=str(event.event_id), 
                    text=f"{event.name} ({event_date})"
                )
            )
        
        self.event_dropdown = ft.Dropdown(
            label="Evento",
            options=event_options,
            value=self.filters["evento"] or "",
            width=FILTER_WIDTH,
            on_change=lambda e: self._update_filter("evento", e.control.value)
        )
        
        # Buttons
        search_button = ft.ElevatedButton(
            text="Aplicar",
            icon=ft.Icons.SEARCH,
            width=FILTER_WIDTH,
            on_click=self._apply_filters
        )
        
        clear_button = ft.ElevatedButton(
            text="Limpiar",
            icon=ft.Icons.CLEAR,
            width=FILTER_WIDTH,
            on_click=self._clear_filters
        )
        
        # Responsive layout
        return ft.ResponsiveRow([
            ft.Container(self.fecha_desde_btn, col=create_responsive_columns(6, 3, 2)),
            ft.Container(self.fecha_hasta_btn, col=create_responsive_columns(6, 3, 2)),
            ft.Container(estado, col=create_responsive_columns(6, 3, 2)),
            ft.Container(imputable, col=create_responsive_columns(6, 3, 2)),
            ft.Container(self.year_dropdown, col=create_responsive_columns(6, 3, 2)),
            ft.Container(self.event_dropdown, col=create_responsive_columns(6, 3, 3)),
            ft.Container(search_button, col=create_responsive_columns(6, 3, 2)),
            ft.Container(clear_button, col=create_responsive_columns(6, 3, 2)),
        ], spacing=10)
    
    def _on_date_desde_change(self, e):
        """Handle date desde change"""
        if self.date_picker_desde.value:
            self.filters["fecha_desde"] = self.date_picker_desde.value
            self.fecha_desde_btn.text = f"Desde: {self.filters["fecha_desde"].strftime("%d-%m-%Y")}"
            self.page.update()
    
    def _on_date_hasta_change(self, e):
        """Handle date hasta change"""
        if self.date_picker_hasta.value:
            self.filters["fecha_hasta"] = self.date_picker_hasta.value
            self.fecha_hasta_btn.text = f"Hasta: {self.filters["fecha_hasta"].strftime("%d-%m-%Y")}"
            self.page.update()
    
    def _create_desktop_table(self):
        """Create desktop data table with horizontal scroll"""
        self.movements_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Concepto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Año Ejercicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Imputable", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            show_checkbox_column=False,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )
        
        self._update_table_rows()
        
        return ft.Container(
            content=ft.Row(
                [self.movements_table],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            expand=True
        )

    
    def _create_mobile_cards(self):
        """Create mobile card layout"""
        cards_container = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)

        if not self.movements:
            self._show_no_movements_message(cards_container)
        else:
            for movement in self.movements:
                card = self._create_movement_card(movement)
                cards_container.controls.append(card)
        
        return cards_container
    
    def _create_movement_card(self, movement: EconomicMovementListItem) -> ft.Card:
        """Create a movement card for mobile view"""
        # Determine movement type and color
        is_income = movement.ind_movimiento == MovementType.INCOME_ID.value
        type_color = ft.Colors.GREEN if is_income else ft.Colors.RED
        type_text = "Ingreso" if is_income else "Gasto"
        type_icon = ft.Icons.ARROW_UPWARD if is_income else ft.Icons.ARROW_DOWNWARD

        # Determine status
        status_map = {
            MovementState.DRAFT.value: ("Borrador", ft.Colors.ORANGE),
            MovementState.PENDING_REVIEW.value: ("Pendiente Revisión", ft.Colors.BLUE),
            MovementState.REVIEWED.value: ("Revisado", ft.Colors.GREEN)
        }
        status_text, status_color = status_map.get(movement.ind_estado, ("Desconocido", ft.Colors.GREY))

        # Build card content
        content = ft.Column([
            # Header row
            ft.Row([
                ft.Row([
                    ft.Icon(type_icon, color=type_color, size=16),
                    ft.Text(f"ID: {movement.id_movimiento_economico}", 
                           weight=ft.FontWeight.BOLD, size=12)
                ]),
                ft.Container(
                    content=ft.Text(status_text, size=10, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.with_opacity(0.1, status_color),
                    border=ft.border.all(1, status_color),
                    border_radius=5,
                    padding=ft.padding.symmetric(horizontal=4, vertical=1)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            # Movement details
            ft.Text(movement.concepto, size=14, weight=ft.FontWeight.W_500, max_lines=2),
            ft.Row([
                ft.Text(f"{type_text}: {format_currency(movement.cantidad_total_ctm)}",
                        size=12, color=type_color, weight=ft.FontWeight.BOLD),
                ft.Text(format_datetime(movement.fecha_creacion), size=10, color=ft.Colors.GREY_600)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Additional details
            ft.Row([
                ft.Text(f"Año: {movement.ano_ejercicio}", size=10),
                ft.Text("Imputable: Sí" if movement.imputable_subvencion else "Imputable: No", 
                       size=10, color=ft.Colors.GREEN if movement.imputable_subvencion else ft.Colors.RED)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=5)

        # Action buttons (removed delete button)
        actions = ft.Row([
            ft.TextButton("Ver", on_click=lambda e, m=movement: self._view_movement_details(m)),
            ft.IconButton(ft.Icons.EDIT, icon_size=16, tooltip="Editar", 
                         on_click=lambda e, m=movement: self._edit_movement(m))
        ], alignment=ft.MainAxisAlignment.END)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([content, actions], spacing=8),
                padding=10
            ),
            elevation=1,
            margin=ft.margin.only(bottom=8)
        )
    
    def _show_no_movements_message(self, container: ft.Column):
        """Show a message when there are no movements to display"""
        # Determinar mensaje según filtros aplicados
        if any([self.filters["estado"], self.filters["imputable"], self.filters["evento"]]):
            message = "No se encontraron movimientos que coincidan con los filtros aplicados"
            icon = ft.Icons.SEARCH_OFF
        elif not self.movements:
            # Caso raro, no hay movimientos en general
            message = "No hay movimientos registrados"
            icon = ft.Icons.INFO_OUTLINE
        else:
            message = "No hay movimientos que mostrar"
            icon = ft.Icons.INFO_OUTLINE

        container.controls.append(
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
                padding=40,
                expand=True
            )
        )

    def _update_table_rows(self):
        """Update table rows with current movements data"""
        if not self.movements_table:
            return
        
        self.movements_table.rows.clear()

        if not self.movements:
            # Crear un DataRow con tantas celdas como columnas
            num_columns = len(self.movements_table.columns)
            
            # Contenedor con mensaje centrado
            dummy_container = ft.Column(
                [
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=ft.Colors.GREY_400),
                    ft.Text(
                        "",
                        style="bodyLarge",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600
                    )
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
            
            # Crear celdas vacías para mantener el número correcto
            cells = [ft.DataCell(ft.Text("")) for _ in range(num_columns)]
            # Poner el mensaje en la primera celda
            cells[1] = ft.DataCell(dummy_container)
            cells[2] = ft.DataCell(ft.Text(
                        "No se encontraron movimientos con los filtros aplicados",
                        style="bodyLarge",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600
                    ))
            
            self.movements_table.rows.append(ft.DataRow(cells=cells))
            self.page.update()
            return
        
        for movement in self.movements:
            # Determine movement type
            is_income = movement.ind_movimiento == MovementType.INCOME_ID.value
            type_text = "Ingreso" if is_income else "Gasto"
            type_color = ft.Colors.GREEN if is_income else ft.Colors.RED
            
            # Determine status
            status_map = {
                MovementState.DRAFT.value: "Borrador",
                MovementState.PENDING_REVIEW.value: "Pendiente Revisión",
                MovementState.REVIEWED.value: "Revisado"
            }
            status_text = status_map.get(movement.ind_estado, "Desconocido")
            
            # Create action buttons (removed delete button)
            actions_row = ft.Row([
                ft.IconButton(
                    ft.Icons.VISIBILITY,
                    icon_size=16,
                    tooltip="Ver detalles",
                    on_click=lambda e, m=movement: self._view_movement_details(m)
                ),
                ft.IconButton(
                    ft.Icons.EDIT,
                    icon_size=16,
                    tooltip="Editar",
                    on_click=lambda e, m=movement: self._edit_movement(m)
                )
            ], spacing=5)
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(format_datetime(movement.fecha_creacion), size=12)),
                    ft.DataCell(ft.Text(str(movement.id_movimiento_economico), size=12)),
                    ft.DataCell(ft.Text(movement.concepto, size=12, max_lines=2)),
                    ft.DataCell(ft.Text(type_text, color=type_color, weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataCell(ft.Text(format_currency(movement.cantidad_total_ctm), 
                                      weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataCell(ft.Text(str(movement.ano_ejercicio), size=12)),
                    ft.DataCell(ft.Text("Sí" if movement.imputable_subvencion else "No",
                                       color=ft.Colors.GREEN if movement.imputable_subvencion else ft.Colors.RED,
                                       size=12)),
                    ft.DataCell(ft.Text(status_text, size=12)),
                    ft.DataCell(actions_row)
                ]
            )
            
            self.movements_table.rows.append(row)
        
        self.page.update()
    
    def _update_filter(self, filter_key: str, value: str):
        """Update filter value"""
        self.filters[filter_key] = value if value != "" else None
    
    def _on_year_change(self, e):
        """Handle year change for event filter"""
        self.selected_year = int(e.control.value)
        self._load_events()
        # Reset event filter when year changes
        self.filters["evento"] = None
        if self.event_dropdown:
            self.event_dropdown.value = "0"
    
    def _apply_filters(self, e):
        """Apply filters and search movements"""
        try:
            # Build filters object
            filters = EconomicMovementFilters(
                fecha_creacion_from=self.filters["fecha_desde"].strftime("%Y-%m-%d"),
                fecha_creacion_to=self.filters["fecha_hasta"].strftime("%Y-%m-%d"),
                ind_estado=int(self.filters["estado"]) if self.filters["estado"] and self.filters["estado"] != "0" else None,
                imputable_subvencion=bool(self.filters["imputable"] == "true") if self.filters["imputable"] else None,
                id_evento=int(self.filters["evento"]) if self.filters["evento"] and self.filters["evento"] != "0" else None
            )
            
            # Search movements
            result = self.safe_api_call(
            lambda: self.services.economic.get_movements_list(filters),
            loading_message="Buscando movimientos..."
        )

            # Asignar siempre los movimientos
            self.movements = result or []

            # Actualizar UI según vista
            if self.is_mobile:
                self._refresh_mobile_display()
            else:
                self._update_table_rows()
            
            # Mensaje informativo
            if self.movements:
                show_success_message(self.page, f"Encontrados {len(self.movements)} movimientos")
            else:
                show_success_message(self.page, "No se encontraron movimientos con los filtros aplicados")
        
        except Exception as ex:
            show_error_message(self.page, f"Error al aplicar filtros: {str(ex)}")
    
    def _clear_filters(self, e):
        """Clear all filters"""
        self.filters = {
            "fecha_desde": date.today().replace(day=1),
            "fecha_hasta": date.today(),
            "estado": None,
            "imputable": None,
            "usuario": None,
            "evento": None
        }
        
        # Reset UI controls
        if self.event_dropdown:
            self.event_dropdown.value = "0"

        self.fecha_desde_btn.text = f"Desde: {self.filters['fecha_desde'].strftime('%d-%m-%Y')}"
        self.fecha_hasta_btn.text = f"Hasta: {self.filters['fecha_hasta'].strftime('%d-%m-%Y')}"
        
        # Reload initial data
        self._load_initial_data()
        if self.is_mobile:
            self._refresh_mobile_display()
        else:
            self._update_table_rows()
    
    def _refresh_mobile_display(self):
        """Refresh mobile cards display"""
        # Find the cards container and rebuild it
        self.page.clean()
        self.setup_page_config("Movimientos Económicos")
        self._setup_content()
    
    def _refresh_data(self):
        """Refresh current data"""
        self._load_initial_data()
        if self.is_mobile:
            self._refresh_mobile_display()
        else:
            self._update_table_rows()
    
    def _view_movement_details(self, movement: EconomicMovementListItem):
        """Navigate to movement details view"""
        self.page.session.set("selected_economy_movement_id", movement.id_movimiento_economico)
        self.page.session.set("edit_mode", False)
        self.router.navigate_to(Routes.ECONOMY_MOVEMENT_DETAIL)
    
    def _edit_movement(self, movement: EconomicMovementListItem):
        """Edit movement"""
        self.page.session.set("selected_economy_movement_id", movement.id_movimiento_economico)
        self.page.session.set("edit_mode", True)
        self.router.navigate_to(Routes.ECONOMY_MOVEMENT_DETAIL)
    
    def _create_new_movement(self):
        """Navigate to create new movement"""
        self.router.navigate_to(Routes.ECONOMY_MOVEMENT_CREATE)