# views/economy/movement_detail.py
import flet as ft
from datetime import datetime, date
from typing import List, Optional
from views.base.base_view import BaseView
from models.economic import EconomicMovementDetail, EconomicMovementUpdate, CategoriaSubvencion
from models.invoice import FacturaListItem
from models.accounting_docs import DocsContablesListItem
from config.constants import Routes, MovementType, MovementState, CashBoxState, InvoiceComputable
from utils.helpers import format_currency, format_datetime, create_responsive_columns, show_error_message, show_success_message
import os


class MovementDetailView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        
        self.movement_id: int = None
        self.movement: EconomicMovementDetail = None
        self.edit_mode = False
        self.categories: list[CategoriaSubvencion] = []
        self.events = []
        self.invoices = []
        self.accounting_docs = []
        self.selected_event_year = datetime.now().year  # Año para eventos
        self.event_year_from_api = None  # Año real del evento desde la API
        
        # Form controls
        self.concepto_field = None
        self.cantidad_field = None
        self.ano_ejercicio_field = None
        self.consideraciones_field = None
        self.imputable_checkbox = None
        self.evento_dropdown = None
        self.categoria_dropdown = None
        self.estado_dropdown = None
        self.movimiento_dropdown = None
        self.caja_dropdown = None
        self.edit_switch = None
        self.event_year_dropdown = None
        
        # Content containers
        self.main_content = None
        self.invoices_container = None
        self.docs_container = None

    def show(self):
        """Show movement detail view"""
        self.movement_id = self.page.session.get("selected_economy_movement_id")
        self.edit_mode = self.page.session.get("edit_mode")
        
        if not self.movement_id:
            show_error_message(self.page, "No se seleccionó ningún movimiento")
            self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            return
        
        self.setup_page_config("Detalle Movimiento")
        self._load_initial_data()
        self._setup_content()

    def _load_initial_data(self):
        """Load movement details and related data"""
        # Load movement details
        result = self.safe_api_call(
            lambda: self.services.economic.get_movement_detail(self.movement_id),
            loading_message="Cargando detalles del movimiento..."
        )
        
        if not result:
            self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            return
        
        self.movement = result

        # Obtener el año real del evento desde la API si existe
        self._load_event_year()
        
        # Establecer el año del evento basado en el evento actual
        # Usar el año real del evento si está disponible, si no usar el año fiscal
        if self.event_year_from_api:
            self.selected_event_year = self.event_year_from_api
        else:
            self.selected_event_year = self.movement.ano_ejercicio
        
        # Load categories and events for dropdowns
        self._load_categories()
        self._load_events()
        
        # Load invoices and accounting documents
        self._load_invoices()
        self._load_accounting_docs()

    def _load_event_year(self):
        """Load the actual year of the event from the API"""
        if self.movement and self.movement.id_evento:
            event_details = self.safe_api_call(
                lambda: self.services.events.get_event_details(self.movement.id_evento),
                loading_message="Cargando detalles del evento..."
            )
            
            self.event_year_from_api = event_details.year

    def _load_categories(self):
        """Load categories for dropdown"""
        result = self.safe_api_call(
            lambda: self.services.economic.get_categories(),
            loading_message="Cargando categorías..."
        )
        self.categories = result or []

    def _load_events(self):
        """Load events for dropdown based on selected year"""
        result = self.safe_api_call(
            lambda: self.services.events.get_events_list(self.selected_event_year),
            loading_message="Cargando eventos..."
        )
        self.events = result or []
        
        # Update event dropdown if it exists
        if self.evento_dropdown:
            self._update_event_dropdown()

    def _load_invoices(self):
        """Load invoices for this movement"""
        result = self.safe_api_call(
            lambda: self.services.invoices.get_invoices_by_movement(self.movement_id),  # Cambiar de economic a invoices
            loading_message="Cargando facturas..."
        )
        self.invoices = result or []

    def _load_accounting_docs(self):
        """Load accounting documents for this movement"""
        result = self.safe_api_call(
            lambda: self.services.accounting.get_accounting_docs_by_movement(self.movement_id),
            loading_message="Cargando documentos contables..."
        )
        self.accounting_docs = result or []

    def _setup_content(self):
        """Setup the main content"""
        if not self.movement:
            return

        # Header with navigation and edit switch
        header = self._create_header()
        
        # Movement details section
        details_section = self._create_details_section()
        
        # Invoices section
        invoices_section = self._create_invoices_section()
        
        # Accounting documents section
        docs_section = self._create_accounting_docs_section()
        
        # Main layout
        self.main_content = ft.Column([
            header,
            ft.Divider(),
            details_section,
            ft.Divider(),
            invoices_section,
            ft.Divider(),
            docs_section
        ], spacing=20, expand=True)
        
        self.page.add(
            ft.Container(
                content=ft.ListView(controls=[self.main_content], expand=True),
                padding=20,
                expand=True
            )
        )
        self.page.update()

    def _create_header(self):
        """Create header with navigation and edit switch"""
        # Title and back button
        title_section = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Volver a movimientos",
                on_click=lambda e: self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            ),
            ft.Text(
                f"Movimiento #{self.movement.id_movimiento_economico}",
                style="headlineMedium",
                weight=ft.FontWeight.BOLD
            )
        ], alignment=ft.MainAxisAlignment.START)
        
        # Edit switch and action buttons
        self.edit_switch = ft.Switch(
            label="Modo edición",
            value=self.edit_mode,
            on_change=self._on_edit_switch_change
        )
        
        # Crear el botón de guardar siempre, pero controlar su estado
        self.save_button = ft.ElevatedButton(
            "Guardar",
            icon=ft.Icons.SAVE,
            on_click=self._save_changes,
            disabled=not self.edit_mode
        )
        
        action_buttons = ft.Row([
            self.edit_switch,
            ft.Container(width=20),  # Spacing
            self.save_button,
            ft.OutlinedButton(
                "Eliminar",
                icon=ft.Icons.DELETE,
                on_click=self._delete_movement,
                style=ft.ButtonStyle(color=ft.Colors.RED)
            )
        ])
        
        return ft.Row([
            title_section,
            action_buttons
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _create_details_section(self):
        """Create movement details section"""
        # Movement type and status info - Estado más prominente
        is_income = self.movement.ind_movimiento == MovementType.INCOME_ID.value
        type_text = "Ingreso" if is_income else "Gasto"
        type_color = ft.Colors.GREEN if is_income else ft.Colors.RED
        
        status_map = {
            MovementState.DRAFT.value: ("Borrador", ft.Colors.ORANGE),
            MovementState.PENDING_REVIEW.value: ("Pendiente Revisión", ft.Colors.BLUE),
            MovementState.REVIEWED.value: ("Revisado", ft.Colors.GREEN)
        }
        status_text, status_color = status_map.get(self.movement.ind_estado, ("Desconocido", ft.Colors.GREY))
        
        # Estado más prominente con información de tesorería
        status_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ASSIGNMENT_TURNED_IN, size=32, color=status_color),
                        ft.Column([
                            ft.Text("Estado del Movimiento", size=14, color=ft.Colors.GREY_600),
                            ft.Text(status_text, size=24, weight=ft.FontWeight.BOLD, color=status_color)
                        ], spacing=2, expand=True)
                    ], spacing=15),
                    ft.Container(
                        content=ft.Text(
                            "ℹ️ Solo tesorería puede cambiar a 'Revisado'",
                            size=12,
                            color=ft.Colors.GREY_600,
                            italic=True
                        ),
                        margin=ft.margin.only(top=8)
                    )
                ]),
                padding=20
            ),
            elevation=3
        )
        
        # Info cards adicionales
        other_info = ft.ResponsiveRow([
            ft.Container(
                content=self._create_info_card("Tipo", type_text, ft.Icons.SWAP_VERT, type_color),
                col=create_responsive_columns(6, 4, 4)
            ),
            ft.Container(
                content=self._create_info_card("Cantidad", format_currency(self.movement.cantidad_total_ctm), ft.Icons.EURO, ft.Colors.BLUE),
                col=create_responsive_columns(6, 4, 4)
            ),
            ft.Container(
                content=self._create_info_card("Año Ejercicio", str(self.movement.ano_ejercicio), ft.Icons.CALENDAR_MONTH, ft.Colors.PURPLE),
                col=create_responsive_columns(6, 4, 4)
            )
        ])
        
        # Form fields
        form_section = self._create_form_section()
        
        return ft.Column([
            ft.Text("Información del Movimiento", style="titleLarge", weight=ft.FontWeight.BOLD),
            status_card,  # Estado prominente primero
            ft.Container(height=10),
            other_info,
            ft.Container(height=20),
            form_section
        ])

    def _create_info_card(self, title: str, value: str, icon, color):
        """Create an information card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=24, color=color),
                    ft.Column([
                        ft.Text(title, size=12, color=ft.Colors.GREY_600),
                        ft.Text(value, size=16, weight=ft.FontWeight.BOLD)
                    ], spacing=2, expand=True)
                ], spacing=10),
                padding=15
            ),
            elevation=2
        )

    def _create_form_section(self):
        """Create form fields section with organized sections"""
        # Initialize form controls
        self.concepto_field = ft.TextField(
            label="Concepto",
            value=self.movement.concepto,
            read_only=not self.edit_mode,
            max_length=45
        )
        
        self.cantidad_field = ft.TextField(
            label="Cantidad (€)",
            value=str(self.movement.cantidad_total_ctm / 100),
            read_only=not self.edit_mode,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.ano_ejercicio_field = ft.TextField(
            label="Año Ejercicio",
            value=str(self.movement.ano_ejercicio),
            read_only=not self.edit_mode,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.consideraciones_field = ft.TextField(
            label="Consideraciones",
            value=self.movement.consideraciones or "",
            read_only=not self.edit_mode,
            multiline=True,
            max_lines=4,
            max_length=1024
        )
        
        self.imputable_checkbox = ft.Checkbox(
            label="Imputable a subvención",
            value=self.movement.imputable_subvencion,
            disabled=not self.edit_mode,
            on_change=self._on_imputable_change
        )
        
        # Dropdowns
        self._create_dropdowns()
        
        # Event year selector and event search
        event_section = self._create_event_section()
        
        # Sección 1: Información General
        info_general_section = ft.Column([
            ft.Text("Información General", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.concepto_field, col=create_responsive_columns(12, 6, 6)),
                ft.Container(self.cantidad_field, col=create_responsive_columns(12, 6, 6)),
            ]),
            ft.ResponsiveRow([
                ft.Container(self.movimiento_dropdown, col=create_responsive_columns(12, 6, 6)),
            ])
        ], spacing=15)
        
        # Sección 2: Información Fiscal y Organizativa
        info_fiscal_section = ft.Column([
            ft.Text("Información Fiscal y Organizativa", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.ano_ejercicio_field, col=create_responsive_columns(12, 6, 4)),
                ft.Container(self.estado_dropdown, col=create_responsive_columns(12, 6, 4)),
                ft.Container(self.caja_dropdown, col=create_responsive_columns(12, 6, 4)),
            ]),
            event_section
        ], spacing=15)
        
        # Sección 3: Información de Subvención
        info_subvencion_section = ft.Column([
            ft.Text("Información de Subvención", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(
                    self.imputable_checkbox, 
                    col=create_responsive_columns(12, 12, 12)
                ),
            ]),
            ft.ResponsiveRow([
                ft.Container(
                    self.categoria_dropdown, 
                    col=create_responsive_columns(12, 8, 8)  # Aumentar el ancho de la columna
                ),
            ])
        ], spacing=15)
        
        # Sección 4: Consideraciones
        consideraciones_section = ft.Column([
            ft.Text("Consideraciones", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.consideraciones_field, col=create_responsive_columns(12, 12, 12))
            ])
        ], spacing=15)
        
        # Layout completo con todas las secciones
        return ft.Column([
            info_general_section,
            ft.Divider(),
            info_fiscal_section,
            ft.Divider(),
            info_subvencion_section,
            ft.Divider(),
            consideraciones_section
        ], spacing=20)

    def _create_event_section(self):
        """Create event selection section with year selector and searchable dropdown"""
        # Year selector for events
        current_year = datetime.now().year
        
        # Crear opciones de años desde 5 años atrás hasta 2 años adelante
        year_options = [ft.dropdown.Option(key=str(y), text=str(y)) 
                       for y in range(current_year - 5, current_year + 2)]
        
        # Si el año del evento de la API no está en las opciones, añadirlo
        if (self.event_year_from_api and self.event_year_from_api not in range(current_year - 5, current_year + 2)):
            year_options.append(
                ft.dropdown.Option(
                    key=str(self.event_year_from_api), 
                    text=str(self.event_year_from_api)
                )
            )
            # Ordenar las opciones
            year_options.sort(key=lambda x: int(x.key))
        
        self.event_year_dropdown = ft.Dropdown(
            label="Año del Evento",
            value=str(self.selected_event_year),
            options=year_options,
            disabled=not self.edit_mode,
            on_change=self._on_event_year_change
        )
        
        # Event searchable dropdown
        self.evento_dropdown = ft.Dropdown(
            label="Evento",
            options=[],
            value=str(self.movement.id_evento) if self.movement and self.movement.id_evento else None,
            disabled=not self.edit_mode
        )
        
        self._update_event_dropdown()
        
        return ft.Column([
            ft.Text("Selección de Evento", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.ResponsiveRow([
                        ft.Container(self.event_year_dropdown, col=create_responsive_columns(12, 6, 6)),
                        ft.Container(self.evento_dropdown, col=create_responsive_columns(12, 6, 6)),
                    ]),
                    # Añadir información sobre el año real del evento si es diferente al año fiscal
                    self._create_event_year_info()
                ]),
                padding=10
            )
        ])
    
    def _create_event_year_info(self):
        """Create info text if event year differs from fiscal year"""
        if (self.event_year_from_api and 
            self.event_year_from_api != self.movement.ano_ejercicio and
            self.movement.id_evento):
            
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, size=16, color=ft.Colors.BLUE),
                    ft.Text(
                        f"Nota: El evento seleccionado pertenece al año {self.event_year_from_api}, "
                        f"diferente del año fiscal ({self.movement.ano_ejercicio})",
                        size=12,
                        color=ft.Colors.BLUE_700,
                        italic=True
                    )
                ]),
                margin=ft.margin.only(top=5)
            )
        
        return ft.Container()  # Contenedor vacío si no hay diferencia

    def _create_dropdowns(self):
        """Create dropdown controls"""
        # Status dropdown
        status_options = [
            ft.dropdown.Option(key=str(MovementState.DRAFT.value), text="Borrador"),
            ft.dropdown.Option(key=str(MovementState.PENDING_REVIEW.value), text="Pendiente Revisión"),
            ft.dropdown.Option(key=str(MovementState.REVIEWED.value), text="Revisado")
        ]
        self.estado_dropdown = ft.Dropdown(
            label="Estado",
            options=status_options,
            value=str(self.movement.ind_estado),
            disabled=not self.edit_mode
        )
        
        # Movement type dropdown
        movement_options = [
            ft.dropdown.Option(key=str(MovementType.INCOME_ID.value), text="Ingreso"),
            ft.dropdown.Option(key=str(MovementType.EXPENSE_ID.value), text="Gasto")
        ]
        self.movimiento_dropdown = ft.Dropdown(
            label="Tipo Movimiento",
            options=movement_options,
            value=str(self.movement.ind_movimiento),
            disabled=not self.edit_mode,
            on_change=self._on_movement_type_change
        )
        
        # Category dropdown - filtered by movement type and enabled by imputable checkbox
        self._update_category_dropdown()
        
        # Cash box dropdown
        cash_options = [
            ft.dropdown.Option(key=str(CashBoxState.IN_CASH.value), text="En caja"),
            ft.dropdown.Option(key=str(CashBoxState.NOT_IN_CASH.value), text="No en caja")
        ]
        self.caja_dropdown = ft.Dropdown(
            label="Estado Caja",
            options=cash_options,
            value=str(self.movement.ind_mov_caja),
            disabled=not self.edit_mode
        )

    def _update_event_dropdown(self):
        """Update event dropdown options based on selected year"""
        if not self.evento_dropdown:
            return
            
        self.evento_dropdown.options.clear()
        
        # Add events for selected year
        for event in self.events:
            event_date = f"{event.day}/{event.month}" if event.day and event.month else "Sin fecha"
            self.evento_dropdown.options.append(
                ft.dropdown.Option(
                    key=str(event.event_id), 
                    text=f"{event.name} ({event_date})"
                )
            )
        
        # Si hay un año de evento desde la API y estamos en ese año, seleccionar el evento
        if (self.event_year_from_api and 
            self.selected_event_year == self.event_year_from_api and
            self.movement and self.movement.id_evento):
            
            current_event_id = str(self.movement.id_evento)
            if any(opt.key == current_event_id for opt in self.evento_dropdown.options):
                self.evento_dropdown.value = current_event_id
            else:
                # Si el evento no está en la lista, añadir una opción especial
                self.evento_dropdown.options.append(
                    ft.dropdown.Option(
                        key=current_event_id,
                        text=f"Evento #{self.movement.id_evento} (no encontrado en {self.selected_event_year})"
                    )
                )
                self.evento_dropdown.value = current_event_id
        else:
            # Comportamiento normal
            current_event_id = str(self.movement.id_evento) if self.movement and self.movement.id_evento else None
            if current_event_id and any(opt.key == current_event_id for opt in self.evento_dropdown.options):
                self.evento_dropdown.value = current_event_id
            else:
                self.evento_dropdown.value = None
            
        self.page.update()

    def _update_category_dropdown(self):
        """Update category dropdown based on movement type and imputable status"""
        if not hasattr(self, 'categoria_dropdown') or self.categoria_dropdown is None:
            self.categoria_dropdown = ft.Dropdown(
                label="Categoría",
                options=[],
                disabled=not self.edit_mode,
                width=400,  # Añadir ancho más grande para categorías
                tooltip="Selecciona una categoría de subvención"  # Añadir tooltip para texto largo
            )
        
        self.categoria_dropdown.options.clear()
        
        # Obtener valores actuales de los controles
        imputable_value = self.imputable_checkbox.value if self.imputable_checkbox else self.movement.imputable_subvencion
        movement_type_value = int(self.movimiento_dropdown.value) if self.movimiento_dropdown and self.movimiento_dropdown.value else self.movement.ind_movimiento
        
        # Only show categories if imputable is checked
        if imputable_value:
            category_movement_map = {"gasto": MovementType.EXPENSE_ID.value, "ingreso": MovementType.INCOME_ID.value}
            
            filtered_categories = [
                cat for cat in self.categories 
                if category_movement_map.get(cat.tipo_categoria, MovementType.EXPENSE_ID.value) == movement_type_value
            ]
            
            # Add category options with description
            for cat in filtered_categories:
                self.categoria_dropdown.options.append(
                    ft.dropdown.Option(
                        key=str(cat.id_categorias_subvencion), 
                        text=f"{cat.categoria} - {cat.descripcion}",
                        #tooltip=f"{cat.categoria} - {cat.descripcion}"  # Añadir tooltip para texto completo
                    )
                )
            
            # Mantener la selección actual si es válida
            current_category_id = str(self.movement.categorias_subvencion_id) if self.movement else None
            if current_category_id and any(opt.key == current_category_id for opt in self.categoria_dropdown.options):
                self.categoria_dropdown.value = current_category_id
            else:
                self.categoria_dropdown.value = None
            self.categoria_dropdown.disabled = not self.edit_mode
        else:
            self.categoria_dropdown.disabled = True
            self.categoria_dropdown.value = None
        
        if hasattr(self, 'page'):
            self.page.update()

    # Event handlers
    def _on_edit_switch_change(self, e):
        """Handle edit switch change"""
        self.edit_mode = e.control.value
        self.page.session.set("edit_mode", self.edit_mode)

        # Actualizar el botón de guardar
        if hasattr(self, 'save_button'):
            self.save_button.disabled = not self.edit_mode
        
        # Update all form controls
        self._update_form_controls_state()
        self.page.update()

    def _update_form_controls_state(self):
        """Update form controls enabled/disabled state"""
        controls = [
            self.concepto_field,
            self.cantidad_field,
            self.ano_ejercicio_field,
            self.consideraciones_field,
            self.imputable_checkbox,
            self.estado_dropdown,
            self.movimiento_dropdown,
            self.caja_dropdown,
            self.event_year_dropdown,
            self.evento_dropdown
        ]
        
        for control in controls:
            if control:
                if hasattr(control, 'read_only'):
                    control.read_only = not self.edit_mode
                elif hasattr(control, 'disabled'):
                    control.disabled = not self.edit_mode
        
        # Special handling for category dropdown
        self._update_category_dropdown()

    def _on_event_year_change(self, e):
        """Handle event year change"""
        self.selected_event_year = int(e.control.value)
        self._load_events()

    def _on_imputable_change(self, e):
        """Handle imputable checkbox change"""
        #if self.movement:
        #    self.movement.imputable_subvencion = e.control.value
        self._update_category_dropdown()

    def _on_movement_type_change(self, e):
        """Handle movement type change"""
        #if self.movement:
        #    self.movement.ind_movimiento = int(e.control.value)
        self._update_category_dropdown()

    def _create_invoices_section(self):
        """Create invoices section"""
        header = ft.Row([
            ft.Text("Operaciones / Facturas", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Agregar factura",
                on_click=self._add_invoice
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.invoices_container = ft.Column(spacing=10)
        self._update_invoices_display()
        
        return ft.Column([header, self.invoices_container])

    def _create_accounting_docs_section(self):
        """Create accounting documents section"""
        header = ft.Row([
            ft.Text("Documentos Contables", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Agregar documento",
                on_click=self._add_accounting_doc
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.docs_container = ft.Column(spacing=10)
        self._update_docs_display()
        
        return ft.Column([header, self.docs_container])

    def _update_invoices_display(self):
        """Update invoices display"""
        self.invoices_container.controls.clear()
        
        if not self.invoices:
            self.invoices_container.controls.append(
                ft.Container(
                    content=ft.Text("No hay operaciones o facturas asociadas", color=ft.Colors.GREY_600),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for invoice in self.invoices:
                card = self._create_invoice_card(invoice)
                self.invoices_container.controls.append(card)
        
        self.page.update()

    def _create_invoice_card(self, invoice: FacturaListItem):
        """Create a card for an invoice"""
        computable_text = "Subvencionable" if invoice.ind_computable == InvoiceComputable.COMPUTABLE.value else "No Subvencionable"
        computable_color = ft.Colors.GREEN if invoice.ind_computable == InvoiceComputable.COMPUTABLE.value else ft.Colors.ORANGE
        
        content = ft.Row([
            ft.Column([
                ft.Text(f"#{invoice.id_factura}: {invoice.nombre}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Cantidad: {format_currency(invoice.cantidad_ctm)}", size=14),
                ft.Text(f"Creada: {format_datetime(invoice.fecha_creacion)}", size=12, color=ft.Colors.GREY_600),
                ft.Text(f"Emisión: {invoice.fecha_emision_factura.strftime('%d/%m/%Y')}", size=12) if invoice.fecha_emision_factura else ft.Text("Sin fecha emisión", size=12, color=ft.Colors.GREY_600),
                ft.Container(
                    content=ft.Text(computable_text, size=10, color=ft.Colors.WHITE),
                    bgcolor=computable_color,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=3
                )
            ], expand=True, spacing=4),
            ft.Column([
                ft.IconButton(
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Descargar factura",
                    on_click=lambda e, inv=invoice: self._download_invoice(inv)
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="Editar factura",
                    on_click=lambda e, inv=invoice: self._edit_invoice(inv)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Eliminar",
                    icon_color=ft.Colors.RED,
                    on_click=lambda e, inv=invoice: self._delete_invoice(inv)
                )
            ])
        ])
        
        return ft.Card(
            content=ft.Container(content=content, padding=15),
            elevation=2
        )

    def _update_docs_display(self):
        """Update accounting documents display"""
        self.docs_container.controls.clear()
        
        if not self.accounting_docs:
            self.docs_container.controls.append(
                ft.Container(
                    content=ft.Text("No hay documentos contables asociados", color=ft.Colors.GREY_600),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for doc in self.accounting_docs:
                card = self._create_doc_card(doc)
                self.docs_container.controls.append(card)
        
        self.page.update()

    def _create_doc_card(self, doc):
        """Create a card for an accounting document"""
        content = ft.Row([
            ft.Column([
                ft.Text(doc.nombre, weight=ft.FontWeight.BOLD),
                ft.Text(f"Documento #{doc.id_docs_contables}", size=12, color=ft.Colors.GREY_600),
            ], expand=True, spacing=4),
            ft.Column([
                ft.IconButton(
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Descargar",
                    on_click=lambda e, d=doc: self._download_document(d)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Eliminar",
                    icon_color=ft.Colors.RED,
                    on_click=lambda e, d=doc: self._delete_document(d)
                )
            ])
        ])
        
        return ft.Card(
            content=ft.Container(content=content, padding=15),
            elevation=2
        )

    def _save_changes(self, e):
        """Save changes to the movement"""
        try:
            # Validate form data
            cantidad_ctm = int(float(self.cantidad_field.value) * 100) if self.cantidad_field.value else self.movement.cantidad_total_ctm
            
            # Prepare update data - usar valores actuales de controles
            update_data = EconomicMovementUpdate(
                id_evento=int(self.evento_dropdown.value) if self.evento_dropdown.value else None,
                concepto=self.concepto_field.value,
                cantidad_total_ctm=cantidad_ctm,
                imputable_subvencion=self.imputable_checkbox.value,
                ano_ejercicio=int(self.ano_ejercicio_field.value) if self.ano_ejercicio_field.value else None,
                categorias_subvencion_id=int(self.categoria_dropdown.value) if self.categoria_dropdown.value else None,
                consideraciones=self.consideraciones_field.value,
                ind_movimiento=int(self.movimiento_dropdown.value) if self.movimiento_dropdown.value else None,
                ind_estado=int(self.estado_dropdown.value) if self.estado_dropdown.value else None,
                ind_mov_caja=int(self.caja_dropdown.value) if self.caja_dropdown.value else None
            )
            
            # Solo incluir campos que han cambiado
            # (puedes mantener tu lógica actual de comparación si lo prefieres)
            
            # Save changes
            success = self.safe_api_call(
                lambda: self.services.economic.update_movement(self.movement_id, update_data),
                loading_message="Guardando cambios..."
            )
            
            if success:
                show_success_message(self.page, "Movimiento actualizado correctamente")
                self._load_initial_data()  # Esto actualizará self.movement con los nuevos valores
                self.page.clean()
                self._setup_content()
            
        except ValueError as e:
            show_error_message(self.page, "Error en los datos introducidos")
        except Exception as e:
            show_error_message(self.page, f"Error al guardar: {str(e)}")

    def _delete_movement(self, e):
        """Delete the movement"""
        def confirm_delete(e):
            success = self.safe_api_call(
                lambda: self.services.economic.delete_movement(self.movement_id),
                loading_message="Eliminando movimiento..."
            )
            
            if success:
                show_success_message(self.page, "Movimiento eliminado correctamente")
                self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            
            self.page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este movimiento? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(confirm_dialog)),
                ft.TextButton("Eliminar", on_click=confirm_delete)
            ]
        )
        
        self.page.open(confirm_dialog)

    # Invoice operations
    def _add_invoice(self, e):
        """Add new invoice"""
        # Store current movement ID for the invoice form
        self.page.session.set("invoice_movement_id", self.movement_id)
        self.page.session.set("invoice_edit_mode", False)
        self._show_invoice_dialog()

    def _view_invoice_details(self, invoice):
        """View invoice details"""
        # Store invoice data for detail view
        self.page.session.set("selected_invoice_id", invoice.id_factura)
        self.page.session.set("invoice_movement_id", self.movement_id)
        self.page.session.set("invoice_edit_mode", True)
        self._show_invoice_dialog()
    
    def _show_invoice_dialog(self):
        """Show invoice form as a modal dialog with improved search bars"""
        movement_id = self.page.session.get("invoice_movement_id")
        invoice_id = self.page.session.get("selected_invoice_id") if self.page.session.get("invoice_edit_mode") else None
        is_edit = self.page.session.get("invoice_edit_mode")

        # Obtener el año fiscal del movimiento actual
        fiscal_year = self.movement.ano_ejercicio
        first_date = date(fiscal_year, 1, 1)
        last_date = date(fiscal_year, 12, 31)
        
        # Cargar organizaciones
        organizations = self.safe_api_call(
            lambda: self.services.organizations.get_organizations_list(),
            loading_message="Cargando organizaciones..."
        ) or []
        
        # Variables para almacenar selecciones
        selected_file = None
        selected_emisor_id = None
        selected_beneficiario_id = None
        selected_emisor_name = ft.Text("", size=12, color=ft.Colors.GREY_600)
        selected_beneficiario_name = ft.Text("", size=12, color=ft.Colors.GREY_600)
        selected_file_name = ft.Text("Ningún archivo seleccionado", size=12, color=ft.Colors.GREY_600)

        # Create form fields for invoice
        nombre_field = ft.TextField(
            label="Nombre de la factura *",
            hint_text="Nombre descriptivo de la factura",
            width=400
        )

        computable_options = [
            ft.dropdown.Option(key=str(InvoiceComputable.COMPUTABLE.value), text="Subvencionable"),
            ft.dropdown.Option(key=str(InvoiceComputable.NOT_COMPUTABLE.value), text="No Subvencionable")
        ]
        
        computable_dropdown = ft.Dropdown(
            label="Estado Subvencionable *",
            options=computable_options,
            value=str(InvoiceComputable.COMPUTABLE.value),
            width=400
        )
        
        cantidad_field = ft.TextField(
            label="Cantidad (€) *",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="0.00",
            width=400
        )
        
        cod_factura_field = ft.TextField(
            label="Código Factura Externo",
            hint_text="Número o código de la factura",
            width=400
        )
        
        fecha_button = ft.ElevatedButton(
            text="Seleccionar fecha de emisión",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.open(date_picker),
            width=400
        )

        # Date picker for invoice
        def _change_invoice_date_text(e):
            if date_picker.value:
                fecha_button.text = f"Fecha seleccionada: {date_picker.value.strftime('%d/%m/%Y')}"
                
                # Validar que la fecha esté dentro del año fiscal
                selected_year = date_picker.value.year
                if selected_year != fiscal_year:
                    show_error_message(self.page, f"La fecha debe ser del año fiscal {fiscal_year}")
                    # Resetear la fecha si no es válida
                    date_picker.value = None
                    fecha_button.text = "Seleccionar fecha de emisión"
            else:
                fecha_button.text = "Seleccionar fecha de emisión"
            self.page.update()

        date_picker = ft.DatePicker(
            first_date=date(2020, 1, 1),
            last_date=date(2030, 12, 31),
            on_change=_change_invoice_date_text
        )
        self.page.overlay.append(date_picker)
        
        
        # File picker for invoice file
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        
        file_button = ft.ElevatedButton(
            text="Seleccionar archivo de factura",
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda e: file_picker.pick_files(
                allowed_extensions=["pdf", "jpg", "jpeg", "png"],
                dialog_title="Seleccionar archivo de factura"
            ),
            width=400
        )

        
            
        
        # Función para manejar selección de organizaciones (siguiendo el ejemplo de la documentación)
        def close_anchor_emisor(e):
            nonlocal selected_emisor_id
            org_id = int(e.control.data)
            organization = next((org for org in organizations if org.id_organizacion == org_id), None)
            if organization:
                selected_emisor_id = organization.id_organizacion
                selected_emisor_name.value = f"Seleccionado: {organization.nombre} ({organization.nif})"
                selected_emisor_name.color = ft.Colors.GREEN
                emisor_search.close_view(organization.nombre)
                self.page.update()

        def close_anchor_beneficiario(e):
            nonlocal selected_beneficiario_id
            org_id = int(e.control.data)
            organization = next((org for org in organizations if org.id_organizacion == org_id), None)
            if organization:
                selected_beneficiario_id = organization.id_organizacion
                selected_beneficiario_name.value = f"Seleccionado: {organization.nombre} ({organization.nif})"
                selected_beneficiario_name.color = ft.Colors.GREEN
                beneficiario_search.close_view(organization.nombre)
                self.page.update()

        def handle_change_emisor(e):
            # Filtrar organizaciones en tiempo real
            query = e.data.lower()
            filtered_orgs = [
                org for org in organizations 
                if query in org.nombre.lower() or query in org.nif.lower()
            ]
            
            controls = [
                ft.ListTile(
                    title=ft.Text(org.nombre),
                    subtitle=ft.Text(f"NIF: {org.nif}"),
                    on_click=close_anchor_emisor,
                    data=org.id_organizacion
                ) for org in filtered_orgs
            ]
            
            # Si no hay resultados, mostrar mensaje
            if not filtered_orgs:
                controls.append(
                    ft.ListTile(
                        title=ft.Text("No se encontraron organizaciones"),
                        subtitle=ft.Text("Intenta con otros términos de búsqueda"),
                    )
                )
            
            emisor_search.controls = controls
            self.page.update()

        def handle_change_beneficiario(e):
            # Filtrar organizaciones en tiempo real
            query = e.data.lower()
            filtered_orgs = [
                org for org in organizations 
                if query in org.nombre.lower() or query in org.nif.lower()
            ]
            
            controls = [
                ft.ListTile(
                    title=ft.Text(org.nombre),
                    subtitle=ft.Text(f"NIF: {org.nif}"),
                    on_click=close_anchor_beneficiario,
                    data=org.id_organizacion
                ) for org in filtered_orgs
            ]
            
            # Si no hay resultados, mostrar mensaje
            if not filtered_orgs:
                controls.append(
                    ft.ListTile(
                        title=ft.Text("No se encontraron organizaciones"),
                        subtitle=ft.Text("Intenta con otros términos de búsqueda"),
                    )
                )
            
            beneficiario_search.controls = controls
            self.page.update()

        def handle_tap_emisor(e):
            # Mostrar todas las organizaciones al abrir
            controls = [
                ft.ListTile(
                    title=ft.Text(org.nombre),
                    subtitle=ft.Text(f"NIF: {org.nif}"),
                    on_click=close_anchor_emisor,
                    data=org.id_organizacion
                ) for org in organizations
            ]
            emisor_search.controls = controls
            emisor_search.open_view()
            self.page.update()

        def handle_tap_beneficiario(e):
            # Mostrar todas las organizaciones al abrir
            controls = [
                ft.ListTile(
                    title=ft.Text(org.nombre),
                    subtitle=ft.Text(f"NIF: {org.nif}"),
                    on_click=close_anchor_beneficiario,
                    data=org.id_organizacion
                ) for org in organizations
            ]
            beneficiario_search.controls = controls
            beneficiario_search.open_view()
            self.page.update()

        # Crear las search bars siguiendo el ejemplo de la documentación
        emisor_search = ft.SearchBar(
            bar_hint_text="Buscar organización emisora...",
            view_hint_text="Selecciona una organización emisora",
            on_change=handle_change_emisor,
            on_tap=handle_tap_emisor,
            width=400
        )

        beneficiario_search = ft.SearchBar(
            bar_hint_text="Buscar organización beneficiaria...", 
            view_hint_text="Selecciona una organización beneficiaria",
            on_change=handle_change_beneficiario,
            on_tap=handle_tap_beneficiario,
            width=400
        )
        
        # Configurar el file picker
        def on_file_picked(e: ft.FilePickerResultEvent):
            nonlocal selected_file
            if e.files:
                selected_file = e.files[0]
                selected_file_name.value = f"Archivo seleccionado: {selected_file.name}"
                selected_file_name.color = ft.Colors.GREEN
            else:
                selected_file = None
                selected_file_name.value = "Ningún archivo seleccionado"
                selected_file_name.color = ft.Colors.GREY_600
            self.page.update()
        
        file_picker.on_result = on_file_picked
        
        # Configurar el date picker
        def on_date_change(e):
            if date_picker.value:
                selected_date = date_picker.value
                fecha_button.text = f"Fecha seleccionada: {selected_date.strftime('%d/%m/%Y')}"
            else:
                fecha_button.text = "Seleccionar fecha de emisión"
            self.page.update()
        
        date_picker.on_change = on_date_change
        
        # Cargar datos de la factura si estamos editando
        if is_edit and invoice_id:
            # Buscar la factura en la lista de facturas del movimiento
            invoice_to_edit = next((inv for inv in self.invoices if inv.id_factura == invoice_id), None)
            if invoice_to_edit:
                # Cargar los datos de la factura en los campos
                
                computable_dropdown.value = str(invoice_to_edit.ind_computable)
                cantidad_field.value = str(invoice_to_edit.amount_euros)
                nombre_field.value = invoice_to_edit.nombre
                if invoice_to_edit.fecha_emision_factura:
                    date_picker.value = invoice_to_edit.fecha_emision_factura
                    fecha_button.text = f"Fecha seleccionada: {invoice_to_edit.fecha_emision_factura.strftime('%d/%m/%Y')}"
                cod_factura_field.value = invoice_to_edit.cod_factura_externo or ""
                
                # Cargar organizaciones emisora y beneficiaria si están disponibles
                if invoice_to_edit.id_emisor:
                    # Buscar la organización emisora
                    emisor_org = next((org for org in organizations if org.id_organizacion == invoice_to_edit.id_emisor), None)
                    if emisor_org:
                        selected_emisor_id = emisor_org.id_organizacion
                        selected_emisor_name.value = f"Seleccionado: {emisor_org.nombre} ({emisor_org.nif})"
                        selected_emisor_name.color = ft.Colors.GREEN
                        emisor_search.value = emisor_org.nombre
                
                if invoice_to_edit.id_beneficiario:
                    # Buscar la organización beneficiaria
                    ben_org = next((org for org in organizations if org.id_organizacion == invoice_to_edit.id_beneficiario), None)
                    if ben_org:
                        selected_beneficiario_id = ben_org.id_organizacion
                        selected_beneficiario_name.value = f"Seleccionado: {ben_org.nombre} ({ben_org.nif})"
                        selected_beneficiario_name.color = ft.Colors.GREEN
                        beneficiario_search.value = ben_org.nombre
        
        # Función para guardar la factura
        def save_invoice(e):
            try:
                # Validar campos obligatorios
                if not nombre_field.value:  # ← NUEVA VALIDACIÓN
                    show_error_message(self.page, "El nombre de la operación es obligatorio")
                    return

                if not cantidad_field.value:
                    show_error_message(self.page, "La cantidad es obligatoria")
                    return
                
                if not computable_dropdown.value:
                    show_error_message(self.page, "El estado computable es obligatorio")
                    return
                
                # Validar campos obligatorios para facturas computables
                if computable_dropdown.value == str(InvoiceComputable.COMPUTABLE.value):
                    if not date_picker.value:
                        show_error_message(self.page, "La fecha de emision de la factura es obligatoria")
                        return
                    if not selected_emisor_id:
                        show_error_message(self.page, "El emisor es obligatorio")
                        return
                    if not selected_beneficiario_id:
                        show_error_message(self.page, "El receptor es obligatorio")
                        return
                    if not cod_factura_field.value:
                        show_error_message(self.page, "El código de factura externo es obligatorio")
                        return
                    if not selected_file and not is_edit:
                        show_error_message(self.page, "El archivo de factura es obligatorio")
                        return
                
                # Convertir cantidad a céntimos
                amount_euros = float(cantidad_field.value)
                amount_cents = int(amount_euros * 100)
                
                from models.invoice import FacturaCreate, FacturaUpdate
                
                if is_edit and invoice_id:
                    # Update existing invoice
                    update_data = FacturaUpdate(
                        ind_computable=int(computable_dropdown.value),
                        nombre=nombre_field.value,
                        cantidad_ctm=amount_cents,
                        fecha_emision_factura=date_picker.value.strftime("%Y-%m-%d") if date_picker.value else None,
                        id_emisor=selected_emisor_id,
                        id_beneficiario=selected_beneficiario_id,
                        cod_factura_externo=cod_factura_field.value if cod_factura_field.value else None
                    )
                    
                    success = self.safe_api_call(
                        lambda: self.services.invoices.update_invoice_data(invoice_id, update_data),
                        loading_message="Actualizando operacion..."
                    )
                    
                    # Si hay un nuevo archivo, actualizarlo
                    if success and selected_file:
                        success_file = self.safe_api_call(
                            lambda: self.services.invoices.update_invoice_file(invoice_id, selected_file.path),
                            loading_message="Subiendo archivo de factura..."
                        )
                        if not success_file:
                            show_error_message(self.page, "Error al subir el archivo de factura")
                    
                else:
                    # Create new invoice
                    create_data = FacturaCreate(
                        id_movimiento_economico=movement_id,
                        nombre=nombre_field.value,
                        ind_computable=int(computable_dropdown.value),
                        cantidad_ctm=amount_cents,
                        fecha_emision_factura=date_picker.value.strftime("%Y-%m-%d") if date_picker.value else None,
                        id_emisor=selected_emisor_id,
                        id_beneficiario=selected_beneficiario_id,
                        cod_factura_externo=cod_factura_field.value if cod_factura_field.value else None
                    )
                    
                    success = self.safe_api_call(
                        lambda: self.services.invoices.create_invoice(create_data),
                        loading_message="Creando factura..."
                    )
                    
                    # Si la factura se creó correctamente, subir el archivo
                    if success and selected_file:
                        # Obtener el ID de la factura recién creada
                        invoices = self.safe_api_call(
                            lambda: self.services.invoices.get_invoices_by_movement(movement_id),
                            loading_message="Obteniendo facturas..."
                        )
                        
                        if invoices:
                            # Encontrar la factura más reciente (asumimos que es la que acabamos de crear)
                            new_invoice = max(invoices, key=lambda x: x.id_factura)
                            success_file = self.safe_api_call(
                                lambda: self.services.invoices.update_invoice_file(new_invoice.id_factura, selected_file.path),
                                loading_message="Subiendo archivo de factura..."
                            )
                            
                            if not success_file:
                                show_error_message(self.page, "Error al subir el archivo de factura")
                
                if success:
                    action = "actualizada" if is_edit else "creada"
                    show_success_message(self.page, f"Factura {action} correctamente")
                    self._load_invoices()
                    self._update_invoices_display()
                    self.page.close(invoice_dialog)
                    self.page.update()
                
            except ValueError:
                show_error_message(self.page, "Error en el formato de la cantidad")
            except Exception as ex:
                show_error_message(self.page, f"Error al guardar la factura: {str(ex)}")
        
        # Create modal dialog
        title = "Editar Operacion" if is_edit else "Nueva Operacion"
        invoice_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Datos de la Operación", style="titleMedium", weight=ft.FontWeight.BOLD),
                    computable_dropdown,
                    nombre_field,
                    cantidad_field,
                    fecha_button,
                    cod_factura_field,
                    
                    ft.Text("Organización Emisora", style="titleSmall", weight=ft.FontWeight.BOLD),
                    emisor_search,
                    selected_emisor_name,
                    
                    ft.Text("Organización Beneficiaria", style="titleSmall", weight=ft.FontWeight.BOLD),
                    beneficiario_search,
                    selected_beneficiario_name,
                    
                    ft.Container(height=10),
                    ft.Text("Documento de factura", style="titleMedium", weight=ft.FontWeight.BOLD),
                    file_button,
                    selected_file_name
                ], scroll=ft.ScrollMode.ALWAYS, spacing=15),
                width=450,
                height=550
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(invoice_dialog)),
                ft.TextButton("Guardar", on_click=save_invoice)
            ]
        )
        
        self.page.open(invoice_dialog)

    def _download_invoice(self, invoice):
        """Handle the downloaded invoice file - compatible with web and desktop"""
        try:

            file_path = self.safe_api_call(
                lambda: self.services.invoices.download_invoice(invoice.id_factura),
                loading_message="Descargando factura..."
            )

            # Detectar si estamos en un entorno web
            is_web = hasattr(self.page, 'web') and self.page.web
            
            if is_web:
                # Para entorno web: usar un enfoque diferente
                #self._web_invoice_download_flow(file_path, invoice)
                show_error_message(self.page, f"La descarga desde web no esta implementada")
            else:
                # Para entorno de escritorio: usar FilePicker normal
                self._handle_desktop_download(file_path= file_path, invoice=invoice)
                
        except Exception as e:
            show_error_message(self.page, f"Error al manejar la descarga: {str(e)}")
            # Limpiar el archivo temporal en caso de error
            try:
                os.unlink(file_path)
            except:
                pass

    def _handle_desktop_download(self, file_path: str, invoice):
        """Handle the downloaded invoice file"""
        try:
            # Crear un file picker para guardar el archivo
            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        # Copiar el archivo temporal a la ubicación seleccionada por el usuario
                        import shutil
                        shutil.copy2(file_path, e.path)
                        show_success_message(self.page, f"Factura guardada en: {e.path}")
                        
                        # Limpiar el archivo temporal
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                            
                    except Exception as ex:
                        show_error_message(self.page, f"Error al guardar el archivo: {str(ex)}")
                else:
                    # El usuario canceló la operación, limpiar el archivo temporal
                    try:
                        os.unlink(file_path)
                    except:
                        pass

                # Remover el FilePicker del overlay después de usarlo
                try:
                    self.page.overlay.remove(save_file_dialog)
                    self.page.update()
                except:
                    pass
            
            # Crear y añadir el FilePicker a la página
            save_file_dialog = ft.FilePicker(on_result=on_save_result)
            self.page.overlay.append(save_file_dialog)
            self.page.update()  # Actualizar la página para que reconozca el nuevo overlay
            
            # Sugerir un nombre de archivo basado en la factura
            suggested_name = f"factura_{invoice.id_factura}.pdf"
            
            # Abrir el diálogo para guardar archivo
            save_file_dialog.save_file(
                dialog_title="Guardar factura como...",
                file_name=suggested_name,
                allowed_extensions=["pdf"]
            )
            
        except Exception as e:
            show_error_message(self.page, f"Error al manejar la descarga: {str(e)}")
            # Limpiar el archivo temporal en caso de error
            try:
                os.unlink(file_path)
            except:
                pass

    def _edit_invoice(self, invoice):
        """Edit invoice"""
        # Store invoice data for edit view
        self.page.session.set("selected_invoice_id", invoice.id_factura)
        self.page.session.set("invoice_movement_id", self.movement_id)
        self.page.session.set("invoice_edit_mode", True)
        self._show_invoice_dialog()

    def _delete_invoice(self, invoice):
        """Delete invoice with confirmation dialog"""
        def confirm_delete(e):
            success = self.safe_api_call(
                lambda: self.services.invoices.delete_invoice(invoice.id_factura),
                loading_message="Eliminando factura..."
            )
            
            if success:
                show_success_message(self.page, "Factura eliminada correctamente")
                self._load_invoices()
                self._update_invoices_display()
            
            self.page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar esta factura?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(confirm_dialog)),
                ft.TextButton("Eliminar", on_click=confirm_delete)
            ]
        )
        
        self.page.open(confirm_dialog)

    def _add_accounting_doc(self, e):
        """Add new accounting document"""
        # Create file picker
        def on_file_result(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                self._upload_accounting_doc(file)

        file_picker = ft.FilePicker(on_result=on_file_result)
        self.page.overlay.append(file_picker)
        
        # Show file picker
        file_picker.pick_files(
            allowed_extensions=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            dialog_title="Seleccionar documento contable"
        )
        self.page.update()
    
    def _upload_accounting_doc(self, file):
        """Upload accounting document"""
        # Create dialog for document name
        name_field = ft.TextField(
            label="Nombre del documento",
            value=file.name,
            width=400
        )
        
        def upload_doc(e):
            if not name_field.value:
                show_error_message(self.page, "El nombre del documento es obligatorio")
                return
                
            # Here you would implement the actual file upload
            # For now, we'll simulate it
            success = True  # Replace with actual upload logic
            
            if success:
                show_success_message(self.page, "Documento subido correctamente")
                self._load_accounting_docs()
                self._update_docs_display()
                self.page.close(upload_dialog)
            
        upload_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Subir Documento Contable"),
            content=ft.Column([
                ft.Text(f"Archivo: {file.name}"),
                name_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(upload_dialog)),
                ft.TextButton("Subir", on_click=upload_doc)
            ]
        )
        
        self.page.open(upload_dialog)

    def _download_document(self, doc):
        """Download accounting document"""
        """
        try:
            response = self.safe_api_call(
                lambda: self.services.accounting.download_accounting_doc(doc.id_docs_contables),
                loading_message="Descargando documento..."
            )
            
            if response:
                show_success_message(self.page, f"Descargando {doc.nombre}")
                # Here you would handle the actual file download
                # This would depend on how Flet handles file downloads
            
        except Exception as e:
            show_error_message(self.page, f"Error al descargar el documento: {str(e)}")
        """
        show_error_message(self.page, f"Esta funcionalidad no esta implementada aun")

    def _delete_document(self, doc):
        """Delete accounting document"""
        def confirm_delete(e):
            success = self.safe_api_call(
                lambda: self.services.accounting.delete_accounting_doc(doc.id_docs_contables),
                loading_message="Eliminando documento..."
            )
            
            if success:
                show_success_message(self.page, "Documento eliminado correctamente")
                self._load_accounting_docs()
                self._update_docs_display()
            
            self.page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este documento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(confirm_dialog)),
                ft.TextButton("Eliminar", on_click=confirm_delete)
            ]
        )
        
        self.page.open(confirm_dialog)