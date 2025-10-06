# views/economy/movement_create.py
import flet as ft
from datetime import datetime
from typing import List, Optional
from views.base.base_view import BaseView
from models.economic import EconomicMovementCreate, CategoriaSubvencion
from config.constants import Routes, MovementType, CashBoxState
from utils.helpers import format_currency, create_responsive_columns, show_error_message, show_success_message


class MovementCreateView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        
        self.categories: list[CategoriaSubvencion] = []
        self.events = []
        self.selected_event_year = datetime.now().year
        
        # Form controls
        self.concepto_field = None
        self.cantidad_field = None
        self.ano_ejercicio_field = None
        self.consideraciones_field = None
        self.imputable_checkbox = None
        self.evento_dropdown = None
        self.categoria_dropdown = None
        self.movimiento_dropdown = None
        self.caja_dropdown = None
        self.event_year_dropdown = None
        
        # Content container
        self.main_content = None

    def show(self):
        """Show movement create view"""
        self.setup_page_config("Crear Movimiento Económico")
        self._load_initial_data()
        self._setup_content()

    def _load_initial_data(self):
        """Load initial data for form"""
        # Load categories
        self._load_categories()
        
        # Load events for current year
        self._load_events()

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

    def _setup_content(self):
        """Setup the main content"""
        # Header with navigation
        header = self._create_header()
        
        # Form sections
        form_sections = self._create_form_sections()
        
        # Invoice notice section
        invoice_notice = self._create_invoice_notice()
        
        # Main layout
        self.main_content = ft.Column([
            header,
            ft.Divider(),
            form_sections,
            ft.Divider(),
            invoice_notice
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
        """Create header with navigation and save button"""
        # Title and back button
        title_section = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Volver a movimientos",
                on_click=lambda e: self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            ),
            ft.Text(
                "Crear Nuevo Movimiento",
                style="headlineMedium",
                weight=ft.FontWeight.BOLD
            )
        ], alignment=ft.MainAxisAlignment.START)
        
        # Action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Guardar",
                icon=ft.Icons.SAVE,
                on_click=self._create_movement,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE
                )
            ),
            ft.OutlinedButton(
                "Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            )
        ])
        
        return ft.Row([
            title_section,
            action_buttons
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _create_form_sections(self):
        """Create form sections"""
        # Initialize form controls
        self._initialize_form_controls()
        
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
        
        # Event selection section
        event_section = self._create_event_section()
        
        # Sección 2: Información Fiscal y Organizativa
        info_fiscal_section = ft.Column([
            ft.Text("Información Fiscal y Organizativa", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.ano_ejercicio_field, col=create_responsive_columns(12, 6, 6)),
                ft.Container(self.caja_dropdown, col=create_responsive_columns(12, 6, 6)),
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
                    col=create_responsive_columns(12, 8, 8)
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

    def _initialize_form_controls(self):
        """Initialize all form controls with default values"""
        self.concepto_field = ft.TextField(
            label="Concepto *",
            hint_text="Introduce el concepto del movimiento",
            max_length=45
        )
        
        self.cantidad_field = ft.TextField(
            label="Cantidad (€) *",
            hint_text="0.00",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.ano_ejercicio_field = ft.TextField(
            label="Año Ejercicio *",
            value=str(datetime.now().year),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.consideraciones_field = ft.TextField(
            label="Consideraciones",
            hint_text="Consideraciones adicionales sobre el movimiento",
            multiline=True,
            max_lines=4,
            max_length=1024
        )
        
        self.imputable_checkbox = ft.Checkbox(
            label="Imputable a subvención",
            value=False,
            on_change=self._on_imputable_change
        )
        
        # Create dropdowns
        self._create_dropdowns()

    def _create_dropdowns(self):
        """Create dropdown controls"""
        # Movement type dropdown
        movement_options = [
            ft.dropdown.Option(key=str(MovementType.INCOME_ID.value), text="Ingreso"),
            ft.dropdown.Option(key=str(MovementType.EXPENSE_ID.value), text="Gasto")
        ]
        self.movimiento_dropdown = ft.Dropdown(
            label="Tipo Movimiento *",
            options=movement_options,
            value=str(MovementType.EXPENSE_ID.value),  # Default to expense
            on_change=self._on_movement_type_change
        )
        
        # Cash box dropdown
        cash_options = [
            ft.dropdown.Option(key=str(CashBoxState.NOT_IN_CASH.value), text="No en caja"),
            ft.dropdown.Option(key=str(CashBoxState.IN_CASH.value), text="En caja")
        ]
        self.caja_dropdown = ft.Dropdown(
            label="Estado Caja *",
            options=cash_options,
            value=str(CashBoxState.NOT_IN_CASH.value)  # Default
        )
        
        # Category dropdown - initially disabled
        self.categoria_dropdown = ft.Dropdown(
            label="Categoría",
            options=[],
            disabled=True,
            width=400,
            tooltip="Selecciona una categoría de subvención"
        )

    def _create_event_section(self):
        """Create event selection section"""
        # Year selector for events
        current_year = datetime.now().year
        year_options = [ft.dropdown.Option(key=str(y), text=str(y)) 
                       for y in range(current_year - 5, current_year + 3)]
        
        self.event_year_dropdown = ft.Dropdown(
            label="Año del Evento *",
            value=str(self.selected_event_year),
            options=year_options,
            on_change=self._on_event_year_change
        )
        
        # Event dropdown
        self.evento_dropdown = ft.Dropdown(
            label="Evento *",
            options=[],
            hint_text="Selecciona un evento"
        )
        
        self._update_event_dropdown()
        
        return ft.Column([
            ft.Text("Selección de Evento", style="titleMedium", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.ResponsiveRow([
                    ft.Container(self.event_year_dropdown, col=create_responsive_columns(12, 6, 6)),
                    ft.Container(self.evento_dropdown, col=create_responsive_columns(12, 6, 6)),
                ]),
                padding=10
            )
        ])

    def _create_invoice_notice(self):
        """Create notice about invoices and documents"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE, size=24),
                        ft.Text(
                            "Información sobre Facturas y Documentos",
                            style="titleMedium",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE
                        )
                    ]),
                    ft.Text(
                        "Una vez creado el movimiento, podrás añadir facturas y documentos contables "
                        "en la vista de detalles del movimiento. Para ello, ve a la lista de movimientos "
                        "y selecciona el movimiento creado para editarlo.",
                        size=14,
                        color=ft.Colors.GREY_700
                    )
                ], spacing=10),
                padding=20
            ),
            elevation=2
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
        
        # Reset selection
        self.evento_dropdown.value = None
        self.page.update()

    def _update_category_dropdown(self):
        """Update category dropdown based on movement type and imputable status"""
        if not self.categoria_dropdown:
            return
        
        self.categoria_dropdown.options.clear()
        
        # Only show categories if imputable is checked
        if self.imputable_checkbox.value:
            movement_type_value = int(self.movimiento_dropdown.value) if self.movimiento_dropdown.value else MovementType.EXPENSE_ID.value
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
                        text=f"{cat.categoria} - {cat.descripcion}"
                    )
                )
            
            self.categoria_dropdown.disabled = False
        else:
            self.categoria_dropdown.disabled = True
            self.categoria_dropdown.value = None
        
        self.page.update()

    # Event handlers
    def _on_event_year_change(self, e):
        """Handle event year change"""
        self.selected_event_year = int(e.control.value)
        self._load_events()

    def _on_imputable_change(self, e):
        """Handle imputable checkbox change"""
        self._update_category_dropdown()

    def _on_movement_type_change(self, e):
        """Handle movement type change"""
        self._update_category_dropdown()

    def _create_movement(self, e):
        """Create the new movement"""
        try:
            # Validate required fields
            if not self._validate_form():
                return
            
            # Convert amount to cents
            cantidad_ctm = int(float(self.cantidad_field.value) * 100)
            
            # Prepare create data
            create_data = EconomicMovementCreate(
                id_evento=int(self.evento_dropdown.value),
                concepto=self.concepto_field.value,
                cantidad_total_ctm=cantidad_ctm,
                imputable_subvencion=self.imputable_checkbox.value,
                ano_ejercicio=int(self.ano_ejercicio_field.value),
                categorias_subvencion_id=int(self.categoria_dropdown.value) if self.categoria_dropdown.value else 1,  # Default category
                consideraciones=self.consideraciones_field.value if self.consideraciones_field.value else None,
                ind_movimiento=int(self.movimiento_dropdown.value),
                ind_mov_caja=int(self.caja_dropdown.value)
            )
            
            # Create movement
            success = self.safe_api_call(
                lambda: self.services.economic.create_movement(create_data),
                loading_message="Creando movimiento..."
            )
            
            if success:
                show_success_message(self.page, "Movimiento creado correctamente")
                self.router.navigate_to(Routes.ECONOMY_MOVEMENTS)
            
        except ValueError:
            show_error_message(self.page, "Error en el formato de los datos")
        except Exception as ex:
            show_error_message(self.page, f"Error al crear el movimiento: {str(ex)}")

    def _validate_form(self) -> bool:
        """Validate form fields"""
        errors = []
        
        if not self.concepto_field.value:
            errors.append("El concepto es obligatorio")
            
        if not self.cantidad_field.value:
            errors.append("La cantidad es obligatoria")
        else:
            try:
                amount = float(self.cantidad_field.value)
                if amount <= 0:
                    errors.append("La cantidad debe ser mayor que 0")
            except ValueError:
                errors.append("La cantidad debe ser un número válido")
        
        if not self.ano_ejercicio_field.value:
            errors.append("El año de ejercicio es obligatorio")
        else:
            try:
                year = int(self.ano_ejercicio_field.value)
                if year < 2000 or year > 2100:
                    errors.append("El año de ejercicio debe estar entre 2000 y 2100")
            except ValueError:
                errors.append("El año de ejercicio debe ser un número válido")
        
        if not self.evento_dropdown.value:
            errors.append("Debe seleccionar un evento")
        
        if not self.movimiento_dropdown.value:
            errors.append("Debe seleccionar el tipo de movimiento")
        
        if not self.caja_dropdown.value:
            errors.append("Debe seleccionar el estado de caja")
        
        # Validate category if imputable is checked
        if self.imputable_checkbox.value and not self.categoria_dropdown.value:
            errors.append("Debe seleccionar una categoría cuando es imputable a subvención")
        
        if errors:
            error_message = "Por favor, corrija los siguientes errores:\n\n" + "\n".join(f"• {error}" for error in errors)
            show_error_message(self.page, error_message)
            return False
        
        return True