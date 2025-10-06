# views/users/user_create.py
import flet as ft
from datetime import date
from typing import Optional
from views.base.base_view import BaseView
from models.user import UserCreate
from utils.validators import (
    validate_email, validate_nif_nie, validate_phone, 
    validate_iban, validate_required_field, validate_password
)
from utils.helpers import show_success_message, show_error_message
from config.constants import Routes, CREStatus, RGCREStatus, UserStatus


class UserFormView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.form_fields = {}
        self.cre_checkbox = None
        self.rgcre_checkbox = None
    
    def show(self):
        """Show user creation view"""
        self.setup_page_config("Crear Nuevo Usuario")
        self._setup_content()
    
    def _setup_content(self):
        """Setup the main content"""
        # Header
        header = self._create_header()
        
        # Form sections
        personal_section = self._create_personal_info_section()
        contact_section = self._create_contact_info_section()
        banking_section = self._create_banking_info_section()
        parents_section = self._create_parents_info_section()
        additional_section = self._create_additional_info_section()
        indicators_section = self._create_indicators_section()  # Nueva sección
        password_section = self._create_password_section()
        
        # Action buttons
        actions_section = self._create_actions_section()
        
        # Main layout
        content = ft.Column([
            header,
            ft.Divider(),
            personal_section,
            ft.Divider(),
            contact_section,
            ft.Divider(),
            banking_section,
            ft.Divider(),
            parents_section,
            ft.Divider(),
            additional_section,
            ft.Divider(),
            indicators_section,  # Nueva sección
            ft.Divider(),
            password_section,
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
        """Create header with title"""
        return ft.Row([
            ft.Text(
                "Crear Nuevo Usuario",
                style="headlineMedium",
                weight=ft.FontWeight.BOLD
            )
        ])
    
    def _create_personal_info_section(self):
        """Create personal information section"""
        self.form_fields['nombre'] = ft.TextField(
            label="Nombre*",
            on_change=self._validate_field
        )
        
        self.form_fields['apellidos'] = ft.TextField(
            label="Apellidos*",
            on_change=self._validate_field
        )
        
        self.form_fields['nif_nie'] = ft.TextField(
            label="NIF/NIE*",
            on_change=self._validate_nif
        )
        
        self.form_fields['fecha_nacimiento'] = ft.TextField(
            label="Fecha de nacimiento*",
            hint_text="DD/MM/YYYY",
            on_change=self._format_date_input,
            max_length=10
        )
        
        return ft.Column([
            ft.Text("Información Personal", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['nombre'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['apellidos'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['nif_nie'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['fecha_nacimiento'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_contact_info_section(self):
        """Create contact information section"""
        self.form_fields['email'] = ft.TextField(
            label="Email*",
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=self._validate_email
        )
        
        self.form_fields['telefono'] = ft.TextField(
            label="Teléfono*",
            keyboard_type=ft.KeyboardType.PHONE,
            on_change=self._validate_phone
        )
        
        self.form_fields['domicilio'] = ft.TextField(
            label="Dirección",
            on_change=self._validate_field
        )
        
        self.form_fields['poblacion'] = ft.TextField(
            label="Población",
            on_change=self._validate_field
        )
        
        return ft.Column([
            ft.Text("Información de Contacto", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['email'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['telefono'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['domicilio'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['poblacion'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_banking_info_section(self):
        """Create banking information section"""
        self.form_fields['titular_cuenta'] = ft.TextField(
            label="Titular de la cuenta*",
            on_change=self._validate_field
        )
        
        self.form_fields['iban'] = ft.TextField(
            label="IBAN*",
            on_change=self._validate_iban
        )
        
        self.form_fields['numero_ss'] = ft.TextField(
            label="Número Seguridad Social",
            on_change=self._validate_field
        )
        
        return ft.Column([
            ft.Text("Información Bancaria", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['titular_cuenta'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['iban'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['numero_ss'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_parents_info_section(self):
        """Create parents information section"""
        parent_fields = [
            ('nombre_progenitor1', 'Nombre Progenitor 1'),
            ('nif_nie_progenitor1', 'NIF Progenitor 1'),
            ('telefono_progenitor1', 'Teléfono Progenitor 1'),
            ('email_progenitor1', 'Email Progenitor 1'),
            ('nombre_progenitor2', 'Nombre Progenitor 2'),
            ('nif_nie_progenitor2', 'NIF Progenitor 2'),
            ('telefono_progenitor2', 'Teléfono Progenitor 2'),
            ('email_progenitor2', 'Email Progenitor 2'),
        ]
        
        for field_name, label in parent_fields:
            self.form_fields[field_name] = ft.TextField(
                label=label,
                on_change=self._validate_field
            )
        
        return ft.Column([
            ft.Text("Información de Progenitores", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.Text("Progenitor 1", style="titleMedium", weight=ft.FontWeight.W_500),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['nombre_progenitor1'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['nif_nie_progenitor1'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['telefono_progenitor1'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['email_progenitor1'], col={"xs": 12, "md": 6}),
            ]),
            ft.Text("Progenitor 2", style="titleMedium", weight=ft.FontWeight.W_500),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['nombre_progenitor2'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['nif_nie_progenitor2'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['telefono_progenitor2'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['email_progenitor2'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_additional_info_section(self):
        """Create additional information section"""
        self.form_fields['consideraciones'] = ft.TextField(
            label="Consideraciones",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        return ft.Column([
            ft.Text("Información Adicional", style="titleLarge", weight=ft.FontWeight.BOLD),
            self.form_fields['consideraciones']
        ])
    
    def _create_indicators_section(self):
        """Create indicators section with checkboxes for CRE and RGCRE"""
        self.cre_checkbox = ft.Checkbox(
            label="CRE Completo",
            value=False,  # Por defecto incompleto
            tooltip="Indica si el usuario tiene el CRE completo"
        )
        
        self.rgcre_checkbox = ft.Checkbox(
            label="RGCRE Completo",
            value=False,  # Por defecto incompleto
            tooltip="Indica si el usuario tiene el RGCRE completo"
        )
        
        return ft.Column([
            ft.Text("Indicadores", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.Text("Estado de la documentación:", style="bodyMedium"),
            ft.ResponsiveRow([
                ft.Container(self.cre_checkbox, col={"xs": 12, "md": 6}),
                ft.Container(self.rgcre_checkbox, col={"xs": 12, "md": 6}),
            ]),
            ft.Text(
                "Nota: Por defecto ambos indicadores se crean como 'incompletos'. "
                "Marque estas casillas solo si la documentación está completa.",
                style="bodySmall",
                color=ft.Colors.GREY_600
            )
        ])
    
    def _create_password_section(self):
        """Create password section"""
        self.form_fields['password'] = ft.TextField(
            label="Contraseña*",
            password=True,
            can_reveal_password=True,
            on_change=self._validate_password
        )
        
        self.form_fields['confirm_password'] = ft.TextField(
            label="Confirmar contraseña*",
            password=True,
            can_reveal_password=True,
            on_change=self._validate_password_confirmation
        )
        
        return ft.Column([
            ft.Text("Contraseña", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['password'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['confirm_password'], col={"xs": 12, "md": 6}),
            ])
        ])
    
    def _create_actions_section(self):
        """Create action buttons section"""
        return ft.Row([
            ft.ElevatedButton(
                text="Crear Usuario",
                icon=ft.Icons.PERSON_ADD,
                on_click=self._create_user
            ),
            ft.ElevatedButton(
                text="Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: self.router.navigate_to("/users")
            )
        ], spacing=10)
    
    def _format_date_input(self, e):
        """Auto-format date input with slashes (dd/mm/yyyy)"""
        field = e.control
        text = field.value
        
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, text))
        
        # Format with slashes
        if len(cleaned) > 4:
            formatted = f"{cleaned[:2]}/{cleaned[2:4]}/{cleaned[4:8]}"
        elif len(cleaned) > 2:
            formatted = f"{cleaned[:2]}/{cleaned[2:4]}"
        else:
            formatted = cleaned
        
        # Update field value if different
        if text != formatted:
            field.value = formatted
            self.page.update()
        
        # Validate the date
        self._validate_date(e)
    
    def _validate_field(self, e):
        """Validate required field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_email(self, e):
        """Validate email field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_email(field.value):
            field.error_text = "Formato de email inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_nif(self, e):
        """Validate NIF/NIE field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_nif_nie(field.value):
            field.error_text = "Formato de NIF/NIE inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_phone(self, e):
        """Validate phone field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_phone(field.value):
            field.error_text = "Formato de teléfono inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_iban(self, e):
        """Validate IBAN field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_iban(field.value):
            field.error_text = "Formato de IBAN inválido"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_date(self, e):
        """Validate date field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        else:
            # Check if the date format is correct (dd/mm/yyyy)
            parts = field.value.split('/')
            if len(parts) != 3 or not all(part.isdigit() for part in parts):
                field.error_text = "Formato de fecha inválido (DD/MM/YYYY)"
            else:
                day, month, year = map(int, parts)
                try:
                    # Try to create a date object to validate
                    date(year, month, day)
                    field.error_text = None
                except ValueError:
                    field.error_text = "Fecha inválida"
        self.page.update()
    
    def _validate_password(self, e):
        """Validate password field"""
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not validate_password(field.value):
            field.error_text = "La contraseña debe tener al menos 6 caracteres"
        else:
            field.error_text = None
        
        # Also validate confirmation if it exists
        if hasattr(self, 'form_fields') and 'confirm_password' in self.form_fields:
            confirm_field = self.form_fields['confirm_password']
            if confirm_field.value and field.value != confirm_field.value:
                confirm_field.error_text = "Las contraseñas no coinciden"
            else:
                confirm_field.error_text = None
        
        self.page.update()
    
    def _validate_password_confirmation(self, e):
        """Validate password confirmation field"""
        field = e.control
        password = self.form_fields['password'].value
        
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif field.value != password:
            field.error_text = "Las contraseñas no coinciden"
        else:
            field.error_text = None
        self.page.update()
    
    def _create_user(self, e):
        """Create new user"""
        # Validate all fields
        validation_errors = self._validate_form()
        if validation_errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(validation_errors)}")
            return
        
        # Parse date from DD/MM/YYYY to date object
        try:
            day, month, year = map(int, self.form_fields['fecha_nacimiento'].value.split('/'))
            birth_date = f"{year}-{month:02d}-{day:02d}"
        except (ValueError, AttributeError):
            show_error_message(self.page, "Formato de fecha inválido. Use DD/MM/YYYY")
            return
        
        # Determine CRE and RGCRE status based on checkboxes
        ind_cre = CREStatus.COMPLETE_ID.value if self.cre_checkbox.value else CREStatus.INCOMPLETE_ID.value  # 1 = completo, 0 = incompleto
        ind_rgcre = RGCREStatus.COMPLETE_ID.value if self.rgcre_checkbox.value else RGCREStatus.INCOMPLETE_ID.value  # 1 = completo, 0 = incompleto
        
        # Create user model
        user_data = UserCreate(
            nombre=self.form_fields['nombre'].value,
            apellidos=self.form_fields['apellidos'].value,
            nif_nie=self.form_fields['nif_nie'].value,
            password=self.form_fields['password'].value,
            fecha_nacimiento=birth_date,
            domicilio=self.form_fields['domicilio'].value or None,
            poblacion=self.form_fields['poblacion'].value or None,
            telefono=self.form_fields['telefono'].value,
            email=self.form_fields['email'].value,
            titular_cuenta=self.form_fields['titular_cuenta'].value,
            iban=self.form_fields['iban'].value,
            numero_ss=self.form_fields['numero_ss'].value or None,
            nombre_progenitor1=self.form_fields['nombre_progenitor1'].value or None,
            nombre_progenitor2=self.form_fields['nombre_progenitor2'].value or None,
            nif_nie_progenitor1=self.form_fields['nif_nie_progenitor1'].value or None,
            nif_nie_progenitor2=self.form_fields['nif_nie_progenitor2'].value or None,
            telefono_progenitor1=self.form_fields['telefono_progenitor1'].value or None,
            telefono_progenitor2=self.form_fields['telefono_progenitor2'].value or None,
            email_progenitor1=self.form_fields['email_progenitor1'].value or None,
            email_progenitor2=self.form_fields['email_progenitor2'].value or None,
            consideraciones=self.form_fields['consideraciones'].value or None,
            ind_cre=ind_cre,
            ind_rgcre=ind_rgcre,
            ind_estado=UserStatus.ACTIVE_ID.value
        )
        
        # Save to API
        success = self.safe_api_call(
            lambda: self.services.users.create_user(user_data),
            loading_message="Creando usuario...",
            success_message="Usuario creado correctamente"
        )
        
        if success:
            # Navigate back to users list
            self.router.navigate_to("/users")
    
    def _validate_form(self) -> list:
        """Validate form data and return list of errors"""
        errors = []
        
        # Required fields
        required_checks = [
            ('nombre', 'Nombre'),
            ('apellidos', 'Apellidos'),
            ('nif_nie', 'NIF/NIE'),
            ('fecha_nacimiento', 'Fecha de nacimiento'),
            ('email', 'Email'),
            ('telefono', 'Teléfono'),
            ('titular_cuenta', 'Titular de cuenta'),
            ('iban', 'IBAN'),
            ('password', 'Contraseña'),
            ('confirm_password', 'Confirmar contraseña')
        ]
        
        for field_name, display_name in required_checks:
            error = validate_required_field(self.form_fields[field_name].value, display_name)
            if error:
                errors.append(error)
        
        # Email validation
        if self.form_fields['email'].value and not validate_email(self.form_fields['email'].value):
            errors.append("Formato de email inválido")
        
        # NIF validation
        if self.form_fields['nif_nie'].value and not validate_nif_nie(self.form_fields['nif_nie'].value):
            errors.append("Formato de NIF/NIE inválido")
        
        # Phone validation
        if self.form_fields['telefono'].value and not validate_phone(self.form_fields['telefono'].value):
            errors.append("Formato de teléfono inválido")
        
        # IBAN validation
        if self.form_fields['iban'].value and not validate_iban(self.form_fields['iban'].value):
            errors.append("Formato de IBAN inválido")
        
        # Password validation
        if self.form_fields['password'].value and not validate_password(self.form_fields['password'].value):
            errors.append("La contraseña debe tener al menos 6 caracteres")
        
        # Password confirmation
        if (self.form_fields['password'].value and self.form_fields['confirm_password'].value and 
            self.form_fields['password'].value != self.form_fields['confirm_password'].value):
            errors.append("Las contraseñas no coinciden")
        
        # Date validation
        if self.form_fields['fecha_nacimiento'].value:
            try:
                parts = self.form_fields['fecha_nacimiento'].value.split('/')
                if len(parts) != 3:
                    errors.append("Formato de fecha inválido (DD/MM/YYYY)")
                else:
                    day, month, year = map(int, parts)
                    date(year, month, day)
            except (ValueError, IndexError):
                errors.append("Formato de fecha inválido (DD/MM/YYYY)")
        
        return errors