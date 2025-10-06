# views/organizations/organization_detail.py
import flet as ft
from typing import Optional
from views.base.base_view import BaseView
from models.organization import OrganizationDetail, OrganizationUpdate
from utils.validators import (
    validate_email, validate_nif_nie, validate_phone, 
    validate_iban, validate_required_field
)
from utils.helpers import show_success_message, show_error_message, format_datetime
from config.constants import Routes


class OrganizationDetailView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.organization_id = None
        self.organization_data: Optional[OrganizationDetail] = None
        self.form_fields = {}
        self.is_editing = False
    
    def show(self):
        """Show organization detail view"""
        # Get organization ID from session
        self.organization_id = self.page.session.get("selected_organization_id")
        self.is_editing = self.page.session.get("edit_mode")
        
        if not self.organization_id:
            show_error_message(self.page, "No se ha seleccionado ninguna organización")
            self.router.navigate_to(Routes.ORGANIZATIONS)
            return
        
        self.setup_page_config("Detalles de la Organización")
        self._load_organization_data()
        self._setup_content()
    
    def _load_organization_data(self):
        """Load organization data from API"""
        result = self.safe_api_call(
            lambda: self.services.organizations.get_organization_details(self.organization_id),
            loading_message="Cargando datos de la organización..."
        )
        
        if result:
            self.organization_data = result
        else:
            show_error_message(self.page, "Error al cargar los datos de la organización")
            self.router.navigate_to(Routes.ORGANIZATIONS)
    
    def _setup_content(self):
        """Setup the main content"""
        if not self.organization_data:
            return
        
        # Header with organization info and actions
        header = self._create_header()
        
        # Form sections
        basic_section = self._create_basic_info_section()
        contact_section = self._create_contact_info_section()
        address_section = self._create_address_section()
        banking_section = self._create_banking_info_section()
        
        # Action buttons
        actions_section = self._create_actions_section()
        
        # Main layout
        content = ft.Column([
            header,
            ft.Divider(),
            basic_section,
            ft.Divider(),
            contact_section,
            ft.Divider(),
            address_section,
            ft.Divider(),
            banking_section,
            ft.Divider(),
            actions_section
        ], spacing=20)
        
        # Scrollable container
        self.page.add(
            ft.Container(
                content=ft.ListView(controls=[content], expand=True),
                padding=20,
                expand=True
            )
        )
        self.page.update()
    
    def _create_header(self):
        """Create header with organization info and edit toggle"""
        return ft.Row([
            ft.Column([
                ft.Text(
                    self.organization_data.nombre,
                    style="headlineMedium",
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(f"ID: {self.organization_data.id_organizacion}", color=ft.Colors.GREY_600)
            ], expand=True),
            ft.Switch(
                label="Modo edición",
                value=self.is_editing,
                on_change=self._toggle_edit_mode
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _create_basic_info_section(self):
        """Create basic information section"""
        self.form_fields['nombre'] = ft.TextField(
            label="Nombre",
            value=self.organization_data.nombre,
            read_only=not self.is_editing,
            on_change=lambda e: self._validate_field(e, "nombre")
        )
        
        self.form_fields['nif'] = ft.TextField(
            label="NIF",
            value=self.organization_data.nif,
            read_only=not self.is_editing,
            on_change=lambda e: self._validate_nif(e)
        )
        
        self.form_fields['descripcion'] = ft.TextField(
            label="Descripción",
            value=self.organization_data.descripcion or "",
            read_only=not self.is_editing,
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        
        return ft.Column([
            ft.Text("Información Básica", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['nombre'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['nif'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['descripcion'], col={"xs": 12}),
            ])
        ])
    
    def _create_contact_info_section(self):
        """Create contact information section"""
        self.form_fields['email'] = ft.TextField(
            label="Email",
            value=self.organization_data.email or "",
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=lambda e: self._validate_email(e)
        )
        
        self.form_fields['telefono'] = ft.TextField(
            label="Teléfono",
            value=self.organization_data.telefono or "",
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.PHONE,
            on_change=lambda e: self._validate_phone(e)
        )
        
        return ft.Column([
            ft.Text("Información de Contacto", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['email'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['telefono'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_address_section(self):
        """Create address information section"""
        self.form_fields['direccion'] = ft.TextField(
            label="Dirección",
            value=self.organization_data.direccion or "",
            read_only=not self.is_editing
        )
        
        self.form_fields['poblacion'] = ft.TextField(
            label="Población",
            value=self.organization_data.poblacion or "",
            read_only=not self.is_editing
        )
        
        self.form_fields['codigo_postal'] = ft.TextField(
            label="Código Postal",
            value=self.organization_data.codigo_postal or "",
            read_only=not self.is_editing
        )
        
        self.form_fields['provincia'] = ft.TextField(
            label="Provincia",
            value=self.organization_data.provincia or "",
            read_only=not self.is_editing
        )
        
        self.form_fields['pais'] = ft.TextField(
            label="País",
            value=self.organization_data.pais or "",
            read_only=not self.is_editing
        )
        
        return ft.Column([
            ft.Text("Información de Dirección", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['direccion'], col={"xs": 12}),
                ft.Container(self.form_fields['poblacion'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['codigo_postal'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['provincia'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['pais'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_banking_info_section(self):
        """Create banking information section"""
        self.form_fields['iban'] = ft.TextField(
            label="IBAN",
            value=self.organization_data.iban or "",
            read_only=not self.is_editing,
            on_change=lambda e: self._validate_iban(e)
        )
        
        return ft.Column([
            ft.Text("Información Bancaria", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['iban'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_actions_section(self):
        """Create action buttons section"""
        if self.is_editing:
            return ft.Row([
                ft.ElevatedButton(
                    text="Guardar cambios",
                    icon=ft.Icons.SAVE,
                    on_click=self._save_changes
                ),
                ft.ElevatedButton(
                    text="Cancelar",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e: self._toggle_edit_mode(None)
                )
            ], spacing=10)
        else:
            return ft.Row([
                ft.ElevatedButton(
                    text="Volver a la lista",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: self.router.navigate_to(Routes.ORGANIZATIONS)
                )
            ])
    
    def _toggle_edit_mode(self, e):
        """Toggle between view and edit mode"""
        self.is_editing = not self.is_editing
        
        # Update all form fields
        for field in self.form_fields.values():
            if hasattr(field, 'read_only'):
                field.read_only = not self.is_editing
        
        # Rebuild the page
        self.page.clean()
        self.setup_page_config("Detalles de la Organización")
        self._setup_content()
    
    def _validate_field(self, e, field_name):
        """Validate required field"""
        field = e.control
        if not field.value and field_name in [
            'nombre', 'nif', 'iban', 'direccion', 'poblacion', 'codigo_postal'
        ]:
            field.error_text = "Este campo es obligatorio"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_email(self, e):
        """Validate email field"""
        field = e.control
        if field.value and not validate_email(field.value):
            field.error_text = "Formato de email inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_nif(self, e):
        """Validate NIF field"""
        field = e.control
        if field.value and not validate_nif_nie(field.value):
            field.error_text = "Formato de NIF inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_phone(self, e):
        """Validate phone field"""
        field = e.control
        if field.value and not validate_phone(field.value):
            field.error_text = "Formato de teléfono inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_iban(self, e):
        """Validate IBAN field"""
        field = e.control
        if field.value and not validate_iban(field.value):
            field.error_text = "Formato de IBAN inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _save_changes(self, e):
        """Save organization changes"""
        # Validate form data
        validation_errors = self._validate_form()
        if validation_errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(validation_errors)}")
            return

        # Create update model
        update_data = OrganizationUpdate(
            id_organizacion=self.organization_id,
            nif=self.form_fields['nif'].value,
            nombre=self.form_fields['nombre'].value,
            descripcion=self.form_fields['descripcion'].value or None,
            iban=self.form_fields['iban'].value,
            direccion=self.form_fields['direccion'].value,
            poblacion=self.form_fields['poblacion'].value,
            codigo_postal=self.form_fields['codigo_postal'].value,
            provincia=self.form_fields['provincia'].value or None,
            pais=self.form_fields['pais'].value or None,
            email=self.form_fields['email'].value or None,
            telefono=self.form_fields['telefono'].value or None
        )

        # Save to API
        success = self.safe_api_call(
            lambda: self.services.organizations.update_organization(update_data),
            loading_message="Guardando cambios...",
            success_message="Organización actualizada correctamente"
        )

        if success:
            self._load_organization_data()
            self.is_editing = False
            self.page.clean()
            self.setup_page_config("Detalles de la Organización")
            self._setup_content()
    
    def _validate_form(self) -> list:
        """Validate form data and return list of errors"""
        errors = []

        # Required fields
        required_checks = [
            ('nombre', 'Nombre'),
            ('nif', 'NIF'),
            ('iban', 'IBAN'),
            ('direccion', 'Dirección'),
            ('poblacion', 'Población'),
            ('codigo_postal', 'Código Postal'),
        ]

        for field_name, display_name in required_checks:
            if not self.form_fields[field_name].value:
                errors.append(f"{display_name} es obligatorio")

        # Email validation
        if self.form_fields['email'].value and not validate_email(self.form_fields['email'].value):
            errors.append("Formato de email inválido")

        # NIF validation
        if self.form_fields['nif'].value and not validate_nif_nie(self.form_fields['nif'].value):
            errors.append("Formato de NIF inválido")

        # Phone validation
        if self.form_fields['telefono'].value and not validate_phone(self.form_fields['telefono'].value):
            errors.append("Formato de teléfono inválido")

        # IBAN validation
        if self.form_fields['iban'].value and not validate_iban(self.form_fields['iban'].value):
            errors.append("Formato de IBAN inválido")

        return errors