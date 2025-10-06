# views/users/user_detail.py
import flet as ft
from datetime import date
from typing import Optional
from views.base.base_view import BaseView
from models.user import UserDetail, UserUpdate
from utils.validators import (
    validate_email, validate_nif_nie, validate_phone, 
    validate_iban, validate_required_field
)
from utils.helpers import show_success_message, show_error_message, format_date, format_datetime
from config.constants import CREStatus, RGCREStatus, UserStatus, Routes


class UserDetailView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.user_id = None
        self.user_data: Optional[UserDetail] = None
        self.form_fields = {}
        self.is_editing = False

        # Administracion de roles
        self.user_roles: list = []  # Roles actuales del usuario
        self.available_roles: list = []  # Todos los roles disponibles
        self.roles_to_add = set()  # Roles a añadir
        self.roles_to_remove = set()  # Roles a eliminar
        self.role_dropdown = None  # Inicializar el dropdown
    
    def show(self):
        """Show user detail view"""
        # Get user ID from session
        self.user_id = self.page.session.get("selected_user_id")
        if not self.user_id:
            show_error_message(self.page, "No se ha seleccionado ningún usuario")
            self.router.navigate_to("/users")
            return
        
        self.setup_page_config("Detalles del Usuario")
        self._load_roles_data()
        self._load_user_data()
        self._setup_content()

    def _load_roles_data(self):
        """Load roles data for the user"""
        # Load user's current roles
        user_roles_result = self.safe_api_call(
            lambda: self.services.roles.get_user_roles(self.user_id),
            loading_message="Cargando roles del usuario..."
        )
        
        if user_roles_result:
            self.user_roles = user_roles_result
        
        # Load all available roles
        all_roles_result = self.safe_api_call(
            lambda: self.services.roles.get_roles_list(),
            loading_message="Cargando roles disponibles..."
        )
        
        if all_roles_result:
            self.available_roles = all_roles_result
    
    def _load_user_data(self):
        """Load user data from API"""
        
        result = self.safe_api_call(
            lambda: self.services.users.get_user_details(self.user_id),
            loading_message="Cargando datos del usuario..."
        )
        
        if result:
            self.user_data = result
        else:
            show_error_message(self.page, "Error al cargar los datos del usuario")
            self.router.navigate_to(Routes.USERS)
    
    def _setup_content(self):
        """Setup the main content"""
        if not self.user_data:
            return
        
        # Header with user info and actions
        header = self._create_header()
        
        # Audit information section (small and discrete)
        audit_section = self._create_audit_section()
        
        # Form sections
        personal_section = self._create_personal_info_section()
        contact_section = self._create_contact_info_section()
        banking_section = self._create_banking_info_section()
        parents_section = self._create_parents_info_section()
        additional_section = self._create_additional_info_section()
        indicators_section = self._create_indicators_section()
        roles_section = self._create_roles_section()
        
        # Action buttons
        actions_section = self._create_actions_section()
        
        # Main layout
        content = ft.Column([
            header,
            audit_section,  # Audit info right after header
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
            indicators_section,
            ft.Divider(),
            roles_section,
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
        """Create header with user info and edit toggle"""
        status_color = ft.Colors.GREEN if self.user_data.ind_estado == UserStatus.ACTIVE_ID.value else ft.Colors.RED
        status_text = "Activo" if self.user_data.ind_estado == UserStatus.ACTIVE_ID.value else "Inactivo"
        
        return ft.Row([
            ft.Column([
                ft.Text(
                    f"{self.user_data.name} {self.user_data.surname}",
                    style="headlineMedium",
                    weight=ft.FontWeight.BOLD
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Text(status_text, color=status_color, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.with_opacity(0.1, status_color),
                        border=ft.border.all(1, status_color),
                        border_radius=5,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4)
                    ),
                    ft.Text(f"ID: {self.user_data.id_user}", color=ft.Colors.GREY_600)
                ], spacing=10)
            ], expand=True),
            ft.Switch(
                label="Modo edición",
                value=self.is_editing,
                on_change=self._toggle_edit_mode
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _create_audit_section(self):
        """Create audit information section (discrete and small)"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.GREY_400),
                    ft.Text("Información de auditoría", size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500)
                ], spacing=5),
                ft.Container(
                    content=ft.Row([
                        # Creation info
                        ft.Column([
                            ft.Text("Creado:", size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                            ft.Text(
                                format_datetime(self.user_data.creation_date),
                                size=10,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Text(
                                f"Por usuario ID: {self.user_data.created_by}",
                                size=9,
                                color=ft.Colors.GREY_500,
                                italic=True
                            )
                        ], spacing=2),
                        
                        # Separator
                        ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                        
                        # Last update info
                        ft.Column([
                            ft.Text("Última modificación:", size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                            ft.Text(
                                format_datetime(self.user_data.update_date),
                                size=10,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Text(
                                f"Por usuario ID: {self.user_data.updated_by}",
                                size=9,
                                color=ft.Colors.GREY_500,
                                italic=True
                            )
                        ], spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.GREY),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.GREY))
                )
            ], spacing=8),
            margin=ft.margin.only(bottom=10)
        )
    
    def _create_personal_info_section(self):
        """Create personal information section"""
        self.form_fields['nombre'] = ft.TextField(
            label="Nombre",
            value=self.user_data.name,
            read_only=not self.is_editing
        )
        
        self.form_fields['apellidos'] = ft.TextField(
            label="Apellidos",
            value=self.user_data.surname,
            read_only=not self.is_editing
        )
        
        self.form_fields['nif_nie'] = ft.TextField(
            label="NIF/NIE",
            value=self.user_data.nif_nie,
            read_only=not self.is_editing
        )
        
        self.form_fields['fecha_nacimiento'] = ft.TextField(
            label="Fecha de nacimiento",
            value=format_date(self.user_data.birth_date),
            read_only=True  # Keep date readonly for simplicity
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
            label="Email",
            value=self.user_data.email,
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.EMAIL
        )
        
        self.form_fields['telefono'] = ft.TextField(
            label="Teléfono",
            value=self.user_data.phone,
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.PHONE
        )
        
        self.form_fields['domicilio'] = ft.TextField(
            label="Dirección",
            value=self.user_data.address or "",
            read_only=not self.is_editing
        )
        
        self.form_fields['poblacion'] = ft.TextField(
            label="Población",
            value=self.user_data.city or "",
            read_only=not self.is_editing
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
            label="Titular de la cuenta",
            value=self.user_data.account_holder,
            read_only=not self.is_editing
        )
        
        self.form_fields['iban'] = ft.TextField(
            label="IBAN",
            value=self.user_data.iban,
            read_only=not self.is_editing
        )
        
        self.form_fields['numero_ss'] = ft.TextField(
            label="Número Seguridad Social",
            value=self.user_data.social_security or "",
            read_only=not self.is_editing
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
            ('nombre_progenitor1', 'Nombre Progenitor 1', self.user_data.parent1_name),
            ('nif_nie_progenitor1', 'NIF Progenitor 1', self.user_data.parent1_id),
            ('telefono_progenitor1', 'Teléfono Progenitor 1', self.user_data.parent1_phone),
            ('email_progenitor1', 'Email Progenitor 1', self.user_data.parent1_email),
            ('nombre_progenitor2', 'Nombre Progenitor 2', self.user_data.parent2_name),
            ('nif_nie_progenitor2', 'NIF Progenitor 2', self.user_data.parent2_id),
            ('telefono_progenitor2', 'Teléfono Progenitor 2', self.user_data.parent2_phone),
            ('email_progenitor2', 'Email Progenitor 2', self.user_data.parent2_email),
        ]
        
        for field_name, label, value in parent_fields:
            self.form_fields[field_name] = ft.TextField(
                label=label,
                value=value or "",
                read_only=not self.is_editing
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
            value=self.user_data.notes or "",
            read_only=not self.is_editing,
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
        cre_complete = self.user_data.ind_cre == CREStatus.COMPLETE_ID.value
        rgcre_complete = self.user_data.ind_rgcre == RGCREStatus.COMPLETE_ID.value
        
        self.cre_checkbox = ft.Checkbox(
            label="CRE Completo",
            value=cre_complete,
            disabled=not self.is_editing,
            tooltip="Indica si el usuario tiene el CRE completo"
        )
        
        self.rgcre_checkbox = ft.Checkbox(
            label="RGCRE Completo",
            value=rgcre_complete,
            disabled=not self.is_editing,
            tooltip="Indica si el usuario tiene el RGCRE completo"
        )
        
        return ft.Column([
            ft.Text("Indicadores", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.cre_checkbox, col={"xs": 12, "md": 6}),
                ft.Container(self.rgcre_checkbox, col={"xs": 12, "md": 6}),
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
                    on_click=lambda e: self.router.navigate_to("/users")
                )
            ])
    
    def _toggle_edit_mode(self, e):
        """Toggle between view and edit mode"""
        self.is_editing = not self.is_editing
        
        # Update all form fields
        for field in self.form_fields.values():
            if hasattr(field, 'read_only'):
                field.read_only = not self.is_editing
        
        # Update checkboxes
        if hasattr(self, 'cre_checkbox'):
            self.cre_checkbox.disabled = not self.is_editing
        if hasattr(self, 'rgcre_checkbox'):
            self.rgcre_checkbox.disabled = not self.is_editing
        
        # Rebuild the page
        self.page.clean()
        self.setup_page_config("Detalles del Usuario")
        self._setup_content()
    
    def _save_changes(self, e):
        """Save user changes"""
        # Validate form data
        validation_errors = self._validate_form()
        if validation_errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(validation_errors)}")
            return
        
        # Determine CRE and RGCRE status based on checkboxes
        ind_cre = CREStatus.COMPLETE_ID.value if self.cre_checkbox.value else CREStatus.INCOMPLETE_ID.value
        ind_rgcre = RGCREStatus.COMPLETE_ID.value if self.rgcre_checkbox.value else RGCREStatus.INCOMPLETE_ID.value
        
        # Create update model
        update_data = UserUpdate(
            id_usuario=self.user_data.id_user,
            nombre=self.form_fields['nombre'].value,
            apellidos=self.form_fields['apellidos'].value,
            nif_nie=self.form_fields['nif_nie'].value,
            email=self.form_fields['email'].value,
            telefono=self.form_fields['telefono'].value,
            domicilio=self.form_fields['domicilio'].value or None,
            poblacion=self.form_fields['poblacion'].value or None,
            titular_cuenta=self.form_fields['titular_cuenta'].value,
            iban=self.form_fields['iban'].value,
            numero_ss=self.form_fields['numero_ss'].value or None,
            nombre_progenitor1=self.form_fields['nombre_progenitor1'].value or None,
            nif_nie_progenitor1=self.form_fields['nif_nie_progenitor1'].value or None,
            telefono_progenitor1=self.form_fields['telefono_progenitor1'].value or None,
            email_progenitor1=self.form_fields['email_progenitor1'].value or None,
            nombre_progenitor2=self.form_fields['nombre_progenitor2'].value or None,
            nif_nie_progenitor2=self.form_fields['nif_nie_progenitor2'].value or None,
            telefono_progenitor2=self.form_fields['telefono_progenitor2'].value or None,
            email_progenitor2=self.form_fields['email_progenitor2'].value or None,
            consideraciones=self.form_fields['consideraciones'].value or None,
            ind_cre=ind_cre,
            ind_rgcre=ind_rgcre
        )
        
        # Save to API
        success = self.safe_api_call(
            lambda: self.services.users.update_user(update_data),
            loading_message="Guardando cambios...",
            success_message="Usuario actualizado correctamente"
        )

        # Save role changes
        role_success = True
        if self.roles_to_add or self.roles_to_remove:
            role_success = self._save_role_changes()
        
        if success and role_success:
            # Reload user data and switch to view mode
            self._load_user_data()
            self.is_editing = False
            self.roles_to_add.clear()
            self.roles_to_remove.clear()
            self.page.clean()
            self.setup_page_config("Detalles del Usuario")
            self._setup_content()
    
    def _validate_form(self) -> list:
        """Validate form data and return list of errors"""
        errors = []
        
        # Required fields
        required_checks = [
            ('nombre', 'Nombre'),
            ('apellidos', 'Apellidos'),
            ('nif_nie', 'NIF/NIE'),
            ('email', 'Email'),
            ('telefono', 'Teléfono'),
            ('titular_cuenta', 'Titular de cuenta'),
            ('iban', 'IBAN')
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
        
        return errors
    
    ############################## ROLES #######################################

    def _get_available_roles_for_dropdown(self):
        """Get available roles for dropdown (roles not assigned to user)"""
        # Get current assigned role IDs (excluding those to be removed)
        current_role_ids = {role.id_rol for role in self.user_roles}
        effective_assigned_ids = current_role_ids - self.roles_to_remove
        
        # Get roles to be added
        roles_to_add_ids = self.roles_to_add
        
        # Available roles are those not currently assigned and not scheduled to be added
        available_roles = []
        for role in self.available_roles:
            if (role.id_rol not in effective_assigned_ids and 
                role.id_rol not in roles_to_add_ids):
                available_roles.append(role)
        
        return available_roles

    def _create_roles_section(self):
        """Create roles management section"""
        # Current roles display
        current_roles_content = self._create_current_roles_display()
        
        # Add role controls
        add_role_content = self._create_add_role_controls()
        
        return ft.Column([
            ft.Text("Gestión de Roles", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.Text("Roles asignados:", style="titleMedium", weight=ft.FontWeight.W_500),
            current_roles_content,
            ft.Divider(),
            add_role_content
        ])
    
    def _create_current_roles_display(self):
        """Create display for current user roles"""
        # Get effective roles (current roles minus those to remove, plus those to add)
        effective_roles = []
        
        # Add current roles that are not marked for removal
        for user_role in self.user_roles:
            if user_role.id_rol not in self.roles_to_remove:
                effective_roles.append((user_role, False))  # False = not new
        
        # Add roles scheduled to be added
        for role_id in self.roles_to_add:
            role = next((r for r in self.available_roles if r.id_rol == role_id), None)
            if role:
                effective_roles.append((role, True))  # True = new role
        
        if not effective_roles:
            return ft.Container(
                content=ft.Text("No hay roles asignados", style="bodyMedium", italic=True),
                padding=10
            )
        
        roles_container = ft.Column(spacing=5)
        
        for role, is_new in effective_roles:
            role_card = self._create_role_card(role, is_new)
            if role_card:
                roles_container.controls.append(role_card)
        
        return roles_container
    
    def _create_role_card(self, role, is_new=False):
        """Create a role card component"""
        try:
            # Crear controles de forma segura
            row_controls = []
            
            # Columna con nombre y descripción
            row_controls.append(
                ft.Column([
                    ft.Text(role.nombre, weight=ft.FontWeight.BOLD),
                    ft.Text(role.descripcion or "Sin descripción", size=12, color=ft.Colors.GREY_600)
                ], expand=True)
            )
            
            # Container con fecha o "NUEVO"
            date_container = None
            if is_new:
                date_text = "NUEVO"
                color = ft.Colors.GREEN
                bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
            else:
                # For existing roles, show assignment date if available
                user_role = next((ur for ur in self.user_roles if ur.id_rol == role.id_rol), None)
                if user_role and hasattr(user_role, 'fecha_asignacion'):
                    date_text = format_datetime(user_role.fecha_asignacion)
                else:
                    date_text = "Asignado"
                color = ft.Colors.GREY_500
                bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREY)
            
            date_container = ft.Container(
                content=ft.Text(date_text, size=10, color=color),
                bgcolor=bgcolor,
                border_radius=5,
                padding=ft.padding.symmetric(horizontal=6, vertical=2)
            )
            row_controls.append(date_container)
            
            # Botón de eliminar (solo en edición)
            if self.is_editing:
                delete_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    tooltip="Eliminar rol",
                    on_click=lambda e, r=role: self._remove_role(r.id_rol)
                )
                row_controls.append(delete_button)
            
            return ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=row_controls,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=10
                ),
                elevation=1
            )
        except Exception as e:
            print(f"Error creando tarjeta de rol: {e}")
            return None
    
    def _create_add_role_controls(self):
        """Create controls for adding new roles"""
        try:
            # Get available roles for dropdown
            available_for_addition = self._get_available_roles_for_dropdown()
            
            if not available_for_addition:
                return ft.Text("Todos los roles disponibles están asignados", style="bodyMedium", italic=True)
            
            # Create dropdown options
            dropdown_options = [
                ft.dropdown.Option(
                    text=role.nombre,
                    key=str(role.id_rol)
                ) for role in available_for_addition
            ]
            
            self.role_dropdown = ft.Dropdown(
                label="Seleccionar rol para añadir",
                options=dropdown_options,
                width=300,
                disabled=not self.is_editing
            )
            
            return ft.Row([
                self.role_dropdown,
                ft.ElevatedButton(
                    text="Añadir Rol",
                    icon=ft.Icons.ADD,
                    on_click=self._add_role,
                    disabled=not self.is_editing
                )
            ], spacing=10)
        except Exception as e:
            print(f"Error creando controles de añadir rol: {e}")
            return ft.Text("Error al cargar controles de roles", style="bodyMedium", color=ft.Colors.RED)
    
    def _add_role(self, e):
        """Add a role to the user"""
        if not self.role_dropdown.value:
            show_error_message(self.page, "Selecciona un rol para añadir")
            return
        
        role_id = int(self.role_dropdown.value)
        
        # Check if role is already in user_roles
        current_role_ids = {role.id_rol for role in self.user_roles}
        
        if role_id in current_role_ids:
            # If role is already assigned but marked for removal, cancel the removal
            if role_id in self.roles_to_remove:
                self.roles_to_remove.remove(role_id)
                show_success_message(self.page, "Cancelada eliminación del rol")
            else:
                show_error_message(self.page, "Este rol ya está asignado al usuario")
                return
        else:
            # Add to roles_to_add if it's a new role
            if role_id in self.roles_to_add:
                show_error_message(self.page, "Este rol ya está programado para ser añadido")
                return
            self.roles_to_add.add(role_id)
            show_success_message(self.page, "Rol programado para añadir")
        
        # Clear dropdown selection and refresh
        self.role_dropdown.value = None
        self._refresh_roles_section()
    
    def _remove_role(self, role_id: int):
        """Remove a role from the user"""
        current_role_ids = {role.id_rol for role in self.user_roles}
        
        if role_id in current_role_ids:
            # If role is currently assigned, mark for removal
            if role_id in self.roles_to_remove:
                show_error_message(self.page, "Este rol ya está programado para eliminación")
                return
            self.roles_to_remove.add(role_id)
            show_success_message(self.page, "Rol programado para eliminar")
        elif role_id in self.roles_to_add:
            # If role is scheduled to be added, cancel the addition
            self.roles_to_add.remove(role_id)
            show_success_message(self.page, "Cancelada adición del rol")
        else:
            show_error_message(self.page, "Este rol no está asignado al usuario")
            return
        
        # Refresh the display
        self._refresh_roles_section()
    
    def _refresh_roles_section(self):
        """Refresh the roles section"""
        # Rebuild the page to reflect changes
        self.page.clean()
        self.setup_page_config("Detalles del Usuario")
        self._setup_content()
    
    def _save_role_changes(self):
        """Save role changes to the API"""
        success_count = 0
        error_messages = []
        
        # Remove roles first
        for role_id in self.roles_to_remove:
            success = self.safe_api_call(
                lambda: self.services.roles.remove_role_from_user(self.user_id, role_id),
                loading_message="Eliminando roles...",
            )
            if success:
                success_count += 1
            else:
                error_messages.append(f"Error eliminando rol ID: {role_id}")
        
        # Add roles
        for role_id in self.roles_to_add:
            success = self.safe_api_call(
                lambda: self.services.roles.add_role_to_user(self.user_id, role_id),
                loading_message="Añadiendo roles...",
            )
            if success:
                success_count += 1
            else:
                error_messages.append(f"Error añadiendo rol ID: {role_id}")
        
        # Show results
        total_operations = len(self.roles_to_remove) + len(self.roles_to_add)
        if success_count == total_operations:
            show_success_message(self.page, f"Todos los cambios de roles guardados correctamente ({success_count} operaciones)")
        elif success_count > 0:
            show_error_message(self.page, f"Se completaron {success_count} de {total_operations} operaciones. Errores: {', '.join(error_messages)}")
        else:
            show_error_message(self.page, f"No se pudo completar ninguna operación. Errores: {', '.join(error_messages)}")
        
        return success_count > 0