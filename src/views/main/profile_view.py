import flet as ft
from typing import Optional
from views.base.base_view import BaseView
from models.user import UserProfile, ChangePasswordRequest
from models.auth import ChangePasswordRequest as AuthChangePassword
from utils.validators import (
validate_email, validate_phone, validate_iban,
validate_required_field, validate_nif_nie
)
from utils.helpers import show_success_message, show_error_message, format_date
from components.common.forms import ResponsiveForm

class ProfileView(BaseView):
    def init(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().init(page, router, services, session_manager, **kwargs)
        self.user_profile: Optional[UserProfile] = None
        self.profile_form: Optional[ResponsiveForm] = None
        self.password_dialog = None
    
    def show(self):
        """Show profile view"""
        self.setup_page_config("Mi Perfil")
        self._load_profile_data()
        self._setup_content()

    def _load_profile_data(self):
        """Load user profile data from API"""
        result = self.safe_api_call(
            lambda: self.services.auth.get_current_user(),
            loading_message="Cargando perfil de usuario..."
        )
        
        if result:
            self.user_profile = result
        else:
            show_error_message(self.page, "Error al cargar el perfil de usuario")
            self.router.navigate_to("/home")

    def _setup_content(self):
        """Setup the main content"""
        if not self.user_profile:
            return
        
        # Header with user info
        header = self._create_header()
        
        # Profile form
        profile_form_section = self._create_profile_form()
        
        # Password change section
        password_section = self._create_password_section()
        
        # Action buttons
        actions_section = self._create_actions_section()
        
        # Main layout
        content = ft.Column([
            header,
            ft.Divider(),
            profile_form_section,
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
        """Create header with user info"""
        user_name = f"{self.user_profile.name} {self.user_profile.surname}"
        
        # Profile avatar/icon
        avatar = ft.Container(
            content=ft.Text(
                self.user_profile.name[0].upper() if self.user_profile.name else "U",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            width=80,
            height=80,
            bgcolor=ft.Colors.PRIMARY,
            border_radius=40,
            alignment=ft.alignment.center
        )
        
        # Create theme switch
        self.theme_switch = ft.Switch(
            value=(self.page.theme_mode == ft.ThemeMode.LIGHT),
            on_change=self._handle_theme_change,
            tooltip="Cambiar entre modo claro y oscuro"
        )
        
        return ft.Row([
            # Left side - Avatar and basic info
            ft.Row([
                avatar,
                ft.Column([
                    ft.Text(
                        user_name,
                        style="headlineMedium",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        self.user_profile.email,
                        style="bodyLarge",
                        color=ft.Colors.GREY_600
                    ),
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                        ft.Text(self.user_profile.phone, color=ft.Colors.GREY_600)
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.BADGE, size=16, color=ft.Colors.GREY_600),
                        ft.Text(f"NIF: {self.user_profile.nif_nie}", color=ft.Colors.GREY_600)
                    ], spacing=5)
                ], spacing=5)
            ], spacing=15),
            
            # Right side - Member since date and theme switch
            ft.Column([
                ft.Text(
                    f"Miembro desde: {format_date(self.user_profile.signup_date)}",
                    size=12,
                    color=ft.Colors.GREY_600
                ),
                ft.Container(height=5),  # Small spacing
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LIGHT_MODE, size=20, color=ft.Colors.AMBER),
                            self.theme_switch,
                            ft.Icon(ft.Icons.DARK_MODE, size=20, color=ft.Colors.BLUE_GREY),
                        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                        padding=10,
                        width=200
                    ),
                    elevation=1
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.END)
            
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)


    def _handle_theme_change(self, e):
        """Handle theme change"""
        if self.theme_switch.value:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            # Update switch label
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            # Update switch label
        
        # Save theme preference to session or local storage
        # TODO guardar el theme
        #self._save_theme_preference()
        
        # Update the page to apply theme changes
        self.page.update()

    def _create_profile_form(self):
        """Create the profile form using ResponsiveForm"""
        self.profile_form = ResponsiveForm(self.page)
        
        # Personal Information Section
        personal_fields = [
            {
                "name": "name",
                "label": "Nombre",
                "type": "text",
                "required": True,
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "surname", 
                "label": "Apellidos",
                "type": "text",
                "required": True,
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "nif_nie",
                "label": "NIF/NIE", 
                "type": "text",
                "required": True,
                "readonly": True,
                "validator": lambda x: validate_nif_nie(x) or ValueError("Formato de NIF/NIE inválido"),
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "birth_date",
                "label": "Fecha de nacimiento",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            }
        ]
        
        # Contact Information Section  
        contact_fields = [
            {
                "name": "email",
                "label": "Email",
                "type": "text",
                "required": True,
                "readonly": True,
                "keyboard_type": ft.KeyboardType.EMAIL,
                "validator": lambda x: validate_email(x) or ValueError("Formato de email inválido"),
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "phone",
                "label": "Teléfono",
                "type": "text", 
                "required": True,
                "readonly": True,
                "keyboard_type": ft.KeyboardType.PHONE,
                "validator": lambda x: validate_phone(x) or ValueError("Formato de teléfono inválido"),
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "address",
                "label": "Dirección",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "city",
                "label": "Población", 
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            }
        ]
        
        # Banking Information Section
        banking_fields = [
            {
                "name": "account_holder",
                "label": "Titular de la cuenta",
                "type": "text",
                "required": True,
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "iban", 
                "label": "IBAN",
                "type": "text",
                "required": True,
                "readonly": True,
                "validator": lambda x: validate_iban(x) or ValueError("Formato de IBAN inválido"),
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "social_security",
                "label": "Número Seguridad Social",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            }
        ]
        
        # Parents Information Section (if applicable)
        parents_fields = [
            {
                "name": "parent1_name",
                "label": "Nombre Progenitor 1",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent1_id", 
                "label": "NIF Progenitor 1",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent1_phone",
                "label": "Teléfono Progenitor 1", 
                "type": "text",
                "readonly": True,
                "keyboard_type": ft.KeyboardType.PHONE,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent1_email",
                "label": "Email Progenitor 1",
                "type": "text",
                "readonly": True,
                "keyboard_type": ft.KeyboardType.EMAIL, 
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent2_name",
                "label": "Nombre Progenitor 2",
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent2_id",
                "label": "NIF Progenitor 2", 
                "type": "text",
                "readonly": True,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent2_phone",
                "label": "Teléfono Progenitor 2",
                "type": "text",
                "readonly": True,
                "keyboard_type": ft.KeyboardType.PHONE,
                "col": {"xs": 12, "md": 6}
            },
            {
                "name": "parent2_email",
                "label": "Email Progenitor 2",
                "type": "text", 
                "readonly": True,
                "keyboard_type": ft.KeyboardType.EMAIL,
                "col": {"xs": 12, "md": 6}
            }
        ]
        
        # Additional Information Section
        additional_fields = [
            {
                "name": "notes",
                "label": "Notas adicionales",
                "type": "text",
                "readonly": True,
                "multiline": True,
                "max_lines": 4,
                "col": {"xs": 12}
            }
        ]
        
        # Add sections to form
        self.profile_form.add_section("Información Personal", personal_fields)
        self.profile_form.add_section("Información de Contacto", contact_fields)  
        self.profile_form.add_section("Información Bancaria", banking_fields)
        
        # Only show parents section if user has parent data
        if (self.user_profile.parent1_name or self.user_profile.parent2_name or 
            self.user_profile.parent1_id or self.user_profile.parent2_id):
            self.profile_form.add_section("Información de Progenitores", parents_fields)
        
        self.profile_form.add_section("Información Adicional", additional_fields)
        
        # Populate form with current data
        self._populate_form_data()
        
        return self.profile_form.build()

    def _populate_form_data(self):
        """Populate form with current user data"""
        form_data = {
            "name": self.user_profile.name,
            "surname": self.user_profile.surname,
            "nif_nie": self.user_profile.nif_nie,
            "birth_date": format_date(self.user_profile.birth_date),
            "email": self.user_profile.email,
            "phone": self.user_profile.phone,
            "address": self.user_profile.address or "",
            "city": self.user_profile.city or "",
            "account_holder": self.user_profile.account_holder,
            "iban": self.user_profile.iban,
            "social_security": self.user_profile.social_security or "",
            "parent1_name": self.user_profile.parent1_name or "",
            "parent1_id": self.user_profile.parent1_id or "",
            "parent1_phone": self.user_profile.parent1_phone or "",
            "parent1_email": self.user_profile.parent1_email or "",
            "parent2_name": self.user_profile.parent2_name or "",
            "parent2_id": self.user_profile.parent2_id or "",
            "parent2_phone": self.user_profile.parent2_phone or "",
            "parent2_email": self.user_profile.parent2_email or "",
            "notes": self.user_profile.notes or ""
        }
        
        self.profile_form.set_data(form_data)

    def _create_password_section(self):
        """Create password change section"""
        return ft.Column([
            ft.Text("Cambiar Contraseña", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Por seguridad, puedes cambiar tu contraseña en cualquier momento.",
                            color=ft.Colors.GREY_600
                        ),
                        ft.ElevatedButton(
                            text="Cambiar Contraseña",
                            icon=ft.Icons.LOCK_RESET,
                            on_click=self._show_password_dialog
                        )
                    ], spacing=15),
                    padding=20
                ),
                elevation=2
            )
        ])

    def _create_actions_section(self):
        """Create action buttons section"""
        return ft.Row([
            ft.ElevatedButton(
                text="Volver al inicio",
                icon=ft.Icons.HOME,
                on_click=lambda e: self.router.navigate_to("/home")
            )
        ])

    def _show_password_dialog(self, e):
        """Show password change dialog"""
        # Password fields
        old_password_field = ft.TextField(
            label="Contraseña actual",
            password=True,
            width=300
        )
        
        new_password_field = ft.TextField(
            label="Nueva contraseña",
            password=True,
            width=300
        )
        
        confirm_password_field = ft.TextField(
            label="Confirmar nueva contraseña", 
            password=True,
            width=300
        )
        
        def close_dialog(e):
            self.page.close(self.password_dialog)
            self.page.update()
        
        def change_password(e):
            old_pass = old_password_field.value
            new_pass = new_password_field.value
            confirm_pass = confirm_password_field.value
            
            # Validate inputs
            if not old_pass or not new_pass or not confirm_pass:
                show_error_message(self.page, "Todos los campos son obligatorios")
                return
            
            if new_pass != confirm_pass:
                show_error_message(self.page, "Las contraseñas no coinciden")
                return
            
            if len(new_pass) < 6:
                show_error_message(self.page, "La contraseña debe tener al menos 6 caracteres")
                return
            
            # Close dialog and perform change
            close_dialog(e)
            self._perform_password_change(old_pass, new_pass)
        
        self.password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cambiar Contraseña"),
            content=ft.Column([
                ft.Text("Introduce tu contraseña actual y la nueva contraseña."),
                old_password_field,
                new_password_field,
                confirm_password_field
            ], spacing=15, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Cambiar Contraseña", on_click=change_password)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = self.password_dialog
        self.page.open(self.page.dialog)
        self.page.update()

    def _perform_password_change(self, old_password: str, new_password: str):
        """Perform password change"""
        password_data = AuthChangePassword(
            old_password=old_password,
            new_password=new_password
        )
        
        success = self.safe_api_call(
            lambda: self.services.auth.change_password(password_data),
            loading_message="Cambiando contraseña...",
            success_message="Contraseña cambiada correctamente"
        )
        
        if success:
            # Optionally, you might want to redirect to login to re-authenticate
            pass