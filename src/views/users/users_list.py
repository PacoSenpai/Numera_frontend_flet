# views/users/users_list.py
import flet as ft
from typing import List, Optional
from views.base.base_view import BaseView
from views.base.mixins import FilterMixin, PaginationMixin
from models.user import UserShortView
from utils.helpers import create_responsive_columns, show_success_message
from config.constants import Routes, CREStatus, RGCREStatus, UserStatus
from datetime import datetime



class UsersListView(BaseView, FilterMixin, PaginationMixin):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        FilterMixin.__init__(self)
        PaginationMixin.__init__(self)
        
        self.all_users: List[UserShortView] = []
        self.filtered_users: List[UserShortView] = []
        self.users_container = None
        self.invitation_dialog = None
    
    def show(self):
        """Show users list view"""
        self.setup_page_config("Gestión de Usuarios")
        self._setup_fab()
        self._load_users()
        self._setup_content()
        self._setup_invitation_dialog()
    
    def _setup_fab(self):
        """Setup floating action button for adding new users"""
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Crear nuevo usuario",
            on_click=lambda e: self.router.navigate_to(Routes.USER_CREATE)
        )

    def _setup_invitation_dialog(self):
        """Setup invitation link dialog"""
        self.url_text = ft.Text(
            "Generando enlace...",
            selectable=True,
            size=12,
            font_family="monospace"
        )
        self.token_text = ft.Text(
            "Generando...",
            selectable=True,
            size=12,
            font_family="monospace",
            expand=True
        )
        self.expires_text = ft.Text(
            "Generando...",
            size=12,
            expand=True
        )

        self.invitation_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Enlace de Invitación"),
            content=ft.Column([
                ft.Text("Comparte este enlace para que nuevos usuarios se registren:", size=14),
                ft.Container(
                    content=self.url_text,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=5,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    width=500
                ),
                ft.Row([
                    ft.Text("Token:", size=12, weight=ft.FontWeight.BOLD),
                    self.token_text,
                ]),
                ft.Row([
                    ft.Text("Expira:", size=12, weight=ft.FontWeight.BOLD),
                    self.expires_text,
                ]),
                ft.Text(
                    "Este enlace es de un solo uso y expirará después de su uso o en 1 semana",
                    size=12,
                    color=ft.Colors.ORANGE_800,
                    weight=ft.FontWeight.W_500
                )
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cerrar", on_click=self._close_invitation_dialog),
                ft.TextButton("Copiar Enlace", icon=ft.Icons.CONTENT_COPY, on_click=self._copy_invitation_link),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _load_users(self):
        """Load users from API"""
        result = self.safe_api_call(
            lambda: self.services.users.get_users_list(),
            loading_message="Cargando usuarios..."
        )
        
        if result:
            self.all_users = result
            self.filtered_users = result.copy()
            #self.update_pagination(len(self.filtered_users))
    
    def _setup_content(self):
        """Setup the main content"""
        # Filters section
        filters_section = self._create_filters_section()
        
        # Users container
        self.users_container = ft.Column(spacing=10)
        
        # Pagination
        pagination_controls = self.create_pagination_controls(self._on_page_change)
        
        # Invitation button
        invitation_button = ft.ElevatedButton(
            text="Generar Link de Invitación",
            icon=ft.Icons.LINK,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            on_click=self._generate_invitation_link
        )
        
        # Main layout
        content = ft.Column([
            filters_section,
            ft.Divider(),
            ft.Text(
                f"Usuarios ({len(self.filtered_users)})",
                style="headlineSmall",
                weight=ft.FontWeight.BOLD
            ),
            invitation_button,
            ft.Container(
                content=self.users_container,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                padding=10,
                expand=True
            ),
            pagination_controls
        ], spacing=20, expand=True)
        
        self.page.add(ft.Container(content=content, padding=20, expand=True))
        self._update_users_display()
        self.page.update()
    
    def _create_filters_section(self):
        """Create filters section"""
        # Create filter controls
        nif_filter = self.create_text_filter(
            "nif",
            "NIF/NIE",
            "Buscar por NIF exacto",
            self._apply_filters
        )
        
        name_filter = self.create_text_filter(
            "name",
            "Nombre/Apellido",
            "Buscar por nombre o apellido",
            self._apply_filters
        )
        
        status_options = ["Todos", "Activo", "Inactivo"]
        status_filter = self.create_dropdown_filter(
            "status",
            "Estado",
            status_options,
            self._apply_filters
        )
        status_filter.value = "Activo"  # Default to active users
        
        # Clear filters button
        clear_button = ft.ElevatedButton(
            text="Limpiar filtros",
            icon=ft.Icons.CLEAR,
            on_click=lambda e: self._clear_filters()
        )
        
        # Responsive layout for filters
        return ft.ResponsiveRow([
            ft.Container(nif_filter, col=create_responsive_columns(12, 6, 3)),
            ft.Container(name_filter, col=create_responsive_columns(12, 6, 3)),
            ft.Container(status_filter, col=create_responsive_columns(12, 6, 3)),
            ft.Container(clear_button, col=create_responsive_columns(12, 6, 3)),
        ], spacing=10)
    
    def _apply_filters(self, filter_key: str = None, filter_value: str = None):
        """Apply all filters to the users list"""
        self.filtered_users = self.all_users.copy()
        
        # Apply NIF filter
        nif_filter = self.get_filter_value("nif")
        if nif_filter:
            self.filtered_users = [
                user for user in self.filtered_users
                if nif_filter.lower() in user.nif_nie.lower()
            ]
        
        # Apply name filter
        name_filter = self.get_filter_value("name")
        if name_filter:
            search_term = name_filter.lower()
            self.filtered_users = [
                user for user in self.filtered_users
                if search_term in f"{user.name} {user.surname}".lower()
            ]
        
        # Apply status filter
        status_filter = self.get_filter_value("status")
        if status_filter and status_filter != "Todos":
            target_status = UserStatus.ACTIVE.value if status_filter == "Activo" else UserStatus.INACTIVE.value
            self.filtered_users = [
                user for user in self.filtered_users
                if user.ind_estado == target_status
            ]
        
        # Update pagination and display
        self.current_page = 1
        self.update_pagination(len(self.filtered_users))
        self._update_users_display()
    
    def _clear_filters(self):
        """Clear all filters"""
        self.clear_filters()
        self.filtered_users = self.all_users.copy()
        self.current_page = 1
        self.update_pagination(len(self.filtered_users))
        self._update_users_display()
    
    def _on_page_change(self, page_num: int):
        """Handle page change"""
        self.current_page = page_num
        self._update_users_display()
    
    def _update_users_display(self):
        """Update the users display based on current page and filters"""
        self.users_container.controls.clear()
        
        # Calculate pagination
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_users = self.filtered_users[start_idx:end_idx]
        
        if not page_users:
            self.users_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No se encontraron usuarios con los filtros aplicados",
                        style="bodyLarge",
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            for user in page_users:
                user_card = self._create_user_card(user)
                self.users_container.controls.append(user_card)
        
        self.page.update()
    
    def _create_user_card(self, user: UserShortView) -> ft.Card:
        """Create a user card component"""
        # Determine status styling
        is_active = user.ind_estado == UserStatus.ACTIVE.value
        status_color = ft.Colors.GREEN if is_active else ft.Colors.RED
        status_text = "Activo" if is_active else "Inactivo"
        
        # CRE and RGCRE status
        cre_complete = user.ind_cre == "cre_completo" if user.ind_cre else False
        rgcre_complete = user.ind_rgcre == "rgcre_completo" if user.ind_rgcre else False
        
        cre_color = ft.Colors.GREEN_300 if cre_complete else ft.Colors.RED_300
        rgcre_color = ft.Colors.GREEN_300 if rgcre_complete else ft.Colors.RED_300
        
        cre_text = "CRE: Completo" if cre_complete else "CRE: Incompleto"
        rgcre_text = "RGCRE: Completo" if rgcre_complete else "RGCRE: Incompleto"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header row with name and status
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, color=ft.Colors.PRIMARY),
                            ft.Text(
                                f"{user.name} {user.surname}",
                                weight=ft.FontWeight.BOLD,
                                size=16
                            )
                        ], spacing=10),
                        ft.Container(
                            content=ft.Text(status_text, size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.with_opacity(0.1, status_color),
                            border=ft.border.all(1, status_color),
                            border_radius=5,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Contact info
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.GREY_600),
                            ft.Text(user.email, size=14)
                        ], spacing=5),
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                            ft.Text(user.phone, size=14)
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # NIF and indicators
                    ft.Row([
                        ft.Text(f"NIF/NIE: {user.nif_nie}", size=12, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(cre_text, size=10),
                                bgcolor=ft.Colors.with_opacity(0.1, cre_color),
                                border_radius=3,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2)
                            ),
                            ft.Container(
                                content=ft.Text(rgcre_text, size=10),
                                bgcolor=ft.Colors.with_opacity(0.1, rgcre_color),
                                border_radius=3,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2)
                            )
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Action buttons
                    ft.Row([
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            height=32,
                            on_click=lambda e, u=user: self._edit_user(u)
                        ),
                        ft.ElevatedButton(
                            text="Activar" if not is_active else "Desactivar",
                            icon=ft.Icons.TOGGLE_ON if not is_active else ft.Icons.TOGGLE_OFF,
                            height=32,
                            color=ft.Colors.GREEN if not is_active else ft.Colors.RED,
                            on_click=lambda e, u=user: self._toggle_user_status(u)
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                    
                ], spacing=10),
                padding=15
            ),
            elevation=2,
            margin=ft.margin.only(bottom=10)
        )
    
    def _edit_user(self, user: UserShortView):
        """Navigate to user edit view"""
        self.page.session.set("selected_user_id", user.id_user)
        self.router.navigate_to(Routes.USER_DETAIL)
    
    def _toggle_user_status(self, user: UserShortView):
        """Toggle user active/inactive status"""
        is_active = user.ind_estado == UserStatus.ACTIVE.value
        action = "desactivar" if is_active else "activar"
        
        # Show confirmation dialog
        def confirm_toggle(e):
            self.page.close(dialog)
            self.page.update()
            if e.control.text == "Confirmar":
                self._perform_status_toggle(user, is_active)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Confirmar {action} usuario"),
            content=ft.Text(f"¿Está seguro que desea {action} al usuario {user.name} {user.surname}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=confirm_toggle),
                ft.TextButton("Confirmar", on_click=confirm_toggle),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        self.page.open(self.page.dialog)
        self.page.update()
    
    def _perform_status_toggle(self, user: UserShortView, was_active: bool):
        """Perform the actual status toggle"""
        # Determinar qué método del servicio llamar
        if was_active:
            # Si estaba activo, desactivar
            api_call = lambda: self.services.users.deactivate_user(user.id_user)
            loading_msg = "Desactivando usuario..."
            success_msg = "Usuario desactivado correctamente"
        else:
            # Si estaba inactivo, activar
            api_call = lambda: self.services.users.activate_user(user.id_user)
            loading_msg = "Activando usuario..."
            success_msg = "Usuario activado correctamente"
        
        success = self.safe_api_call(
            api_call,
            loading_message=loading_msg,
            success_message=success_msg
        )
        
        if success:
            # Reload users list
            self._load_users()
            self._update_users_display()

    def _generate_invitation_link(self, e):
        """Generate invitation link"""
        result = self.safe_api_call(
            lambda: self.services.users.create_user_link(),
            loading_message="Generando enlace de invitación..."
        )
        
        if result:
            self._show_invitation_dialog(result)

    def _show_invitation_dialog(self, link_data: dict):
        """Show invitation link dialog with generated data"""
        # Update dialog content with actual data
        
        
        self.url_text.value = link_data.get("url", "Error al generar enlace")
        self.token_text.value = link_data.get("token", "Error al generar token")
        if self.expires_text:
            expires_at = link_data.get("expires_at")
            if expires_at:
                try:
                    # Parse and format the date
                    expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    formatted_date = expires_dt.strftime("%d/%m/%Y a las %H:%M")
                    self.expires_text.value = formatted_date
                except:
                    self.expires_text.value = expires_at
            else:
                self.expires_text.value = "No disponible"
        
        # Store the current link data for copying
        self.current_invitation_link = link_data.get("url", "")
        
        # Show dialog
        self.page.dialog = self.invitation_dialog
        self.page.open(self.page.dialog)
        self.page.update()


    def _close_invitation_dialog(self, e):
        """Close invitation dialog"""
        self.page.close(self.page.dialog)
        self.page.update()
    
    def _copy_invitation_link(self, e):
        """Copy invitation link to clipboard"""
        if hasattr(self, 'current_invitation_link') and self.current_invitation_link:
            self.page.set_clipboard(self.current_invitation_link)
            show_success_message(self.page, "Enlace copiado al portapapeles")