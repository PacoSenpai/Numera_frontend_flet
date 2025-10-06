# views/organizations/organization_form.py
import flet as ft
from views.base.base_view import BaseView
from models.organization import OrganizationCreate
from utils.validators import (
    validate_email, validate_phone, 
    validate_iban, validate_nif_empresa
)
from utils.helpers import show_success_message, show_error_message
from config.constants import Routes


class OrganizationFormView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.form_fields = {}
    
    def show(self):
        """Show organization creation view"""
        self.setup_page_config("Crear Nueva Organización")
        self._setup_content()
    
    def _setup_content(self):
        """Setup the main content"""
        header = self._create_header()
        
        basic_section = self._create_basic_info_section()
        contact_section = self._create_contact_info_section()
        address_section = self._create_address_section()
        banking_section = self._create_banking_info_section()
        actions_section = self._create_actions_section()
        
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
        
        self.page.add(
            ft.Container(
                content=ft.ListView(controls=[content], expand=True),
                padding=20,
                expand=True
            )
        )
        self.page.update()
    
    def _create_header(self):
        return ft.Row([
            ft.Text(
                "Crear Nueva Organización",
                style="headlineMedium",
                weight=ft.FontWeight.BOLD
            )
        ])
    
    def _create_basic_info_section(self):
        self.form_fields['nombre'] = ft.TextField(
            label="Nombre*",
            on_change=lambda e: self._validate_field(e, "nombre")
        )
        
        self.form_fields['nif'] = ft.TextField(
            label="NIF*",
            on_change=lambda e: self._validate_nif(e)
        )
        
        self.form_fields['descripcion'] = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        nif_info = ft.Container(
            content=ft.Column([
                ft.Text("Formatos de NIF aceptados:", size=12, weight=ft.FontWeight.BOLD),
                ft.Text("• Sociedades: A12345678 (A,B,C,D,E,F,G,H,J,P,Q,R,S,U,V,N,W)", size=10),
                ft.Text("• Personas físicas: 12345678X", size=10),
                ft.Text("• Extranjeros: X1234567X, GB123456789, etc.", size=10),
            ], spacing=2),
            margin=ft.margin.only(top=5),
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=5
        )
        
        return ft.Column([
            ft.Text("Información Básica", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['nombre'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['nif'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['descripcion'], col={"xs": 12}),
                ft.Container(nif_info, col={"xs": 12}),
            ])
        ])
    
    def _create_contact_info_section(self):
        self.form_fields['email'] = ft.TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=lambda e: self._validate_email(e)
        )
        
        self.form_fields['telefono'] = ft.TextField(
            label="Teléfono",
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
        self.form_fields['direccion'] = ft.TextField(
            label="Dirección*",
            on_change=lambda e: self._validate_field(e, "direccion")
        )
        
        self.form_fields['poblacion'] = ft.TextField(
            label="Población*",
            on_change=lambda e: self._validate_field(e, "poblacion")
        )
        
        self.form_fields['codigo_postal'] = ft.TextField(
            label="Código Postal*",
            on_change=lambda e: self._validate_field(e, "codigo_postal")
        )
        
        self.form_fields['provincia'] = ft.TextField(
            label="Provincia"
        )
        
        self.form_fields['pais'] = ft.TextField(
            label="País",
            value="España"
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
        self.form_fields['iban'] = ft.TextField(
            label="IBAN",
            on_change=lambda e: self._validate_iban(e)
        )
        
        return ft.Column([
            ft.Text("Información Bancaria", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['iban'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_actions_section(self):
        return ft.Row([
            ft.ElevatedButton(
                text="Crear Organización",
                icon=ft.Icons.ADD,
                on_click=self._create_organization
            ),
            ft.ElevatedButton(
                text="Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: self.router.navigate_to(Routes.ORGANIZATIONS)
            )
        ], spacing=10)
    
    def _validate_field(self, e, field_name):
        field = e.control
        if not field.value and field_name in ['nombre', 'nif', 'iban', 'direccion', 'poblacion', 'codigo_postal']:
            field.error_text = "Este campo es obligatorio"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_email(self, e):
        field = e.control
        if field.value and not validate_email(field.value):
            field.error_text = "Formato de email inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_nif(self, e):
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_nif_empresa(field.value):
            field.error_text = "Formato de NIF inválido. Use: A12345678, B1234567X, GB123456789, etc."
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_phone(self, e):
        field = e.control
        if field.value and not validate_phone(field.value):
            field.error_text = "Formato de teléfono inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_iban(self, e):
        field = e.control
        if field.value and not validate_iban(field.value):
            field.error_text = "Formato de IBAN inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _create_organization(self, e):
        validation_errors = self._validate_form()
        if validation_errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(validation_errors)}")
            return
        
        organization_data = OrganizationCreate(
            nif=self.form_fields['nif'].value,
            nombre=self.form_fields['nombre'].value,
            descripcion=self.form_fields['descripcion'].value or None,
            iban=self.form_fields['iban'].value or None,
            direccion=self.form_fields['direccion'].value,
            poblacion=self.form_fields['poblacion'].value,
            codigo_postal=self.form_fields['codigo_postal'].value,
            provincia=self.form_fields['provincia'].value or None,
            pais=self.form_fields['pais'].value or None,
            email=self.form_fields['email'].value or None,
            telefono=self.form_fields['telefono'].value or None
        )
        
        success = self.safe_api_call(
            lambda: self.services.organizations.create_organization(organization_data),
            loading_message="Creando organización...",
            success_message="Organización creada correctamente"
        )
        
        if success:
            self.router.navigate_to(Routes.ORGANIZATIONS)
    
    def _validate_form(self) -> list:
        errors = []
        
        required_checks = [
            ('nombre', 'Nombre'),
            ('nif', 'NIF'),
            ('direccion', 'Dirección'),
            ('poblacion', 'Población'),
            ('codigo_postal', 'Código Postal'),
        ]
        
        for field_name, display_name in required_checks:
            if not self.form_fields[field_name].value:
                errors.append(f"{display_name} es obligatorio")
        
        if self.form_fields['email'].value and not validate_email(self.form_fields['email'].value):
            errors.append("Formato de email inválido")
        
        if self.form_fields['nif'].value and not validate_nif_empresa(self.form_fields['nif'].value):
            errors.append("Formato de NIF inválido")
        
        if self.form_fields['telefono'].value and not validate_phone(self.form_fields['telefono'].value):
            errors.append("Formato de teléfono inválido")
        
        if self.form_fields['iban'].value and not validate_iban(self.form_fields['iban'].value):
            errors.append("Formato de IBAN inválido")
        
        return errors
