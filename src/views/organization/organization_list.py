# views/organizations/organizations_list.py
import flet as ft
from typing import List
from views.base.base_view import BaseView
from views.base.mixins import FilterMixin, PaginationMixin
from models.organization import OrganizationShortView
from utils.helpers import create_responsive_columns
from config.constants import Routes


class OrganizationsListView(BaseView, FilterMixin, PaginationMixin):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        FilterMixin.__init__(self)
        PaginationMixin.__init__(self)
        
        self.all_organizations: List[OrganizationShortView] = []
        self.filtered_organizations: List[OrganizationShortView] = []
        self.organizations_container = None
    
    def show(self):
        """Show organizations list view"""
        self.setup_page_config("Gestión de Organizaciones")
        self._setup_fab()
        self._load_organizations()
        self._setup_content()
    
    def _setup_fab(self):
        """Setup floating action button for adding new organizations"""
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Crear nueva organización",
            on_click=lambda e: self.router.navigate_to(Routes.ORGANIZATION_CREATE)
        )
    
    def _load_organizations(self):
        """Load organizations from API"""
        result = self.safe_api_call(
            lambda: self.services.organizations.get_organizations_list(),
            loading_message="Cargando organizaciones..."
        )
        
        if result:
            self.all_organizations = result
            self.filtered_organizations = result.copy()
            #self.update_pagination(len(self.filtered_organizations))
    
    def _setup_content(self):
        """Setup the main content"""
        # Filters section
        filters_section = self._create_filters_section()
        
        # Organizations container
        self.organizations_container = ft.Column(spacing=10)
        
        # Pagination
        pagination_controls = self.create_pagination_controls(self._on_page_change)
        
        # Main layout
        content = ft.Column([
            filters_section,
            ft.Divider(),
            ft.Text(
                f"Organizaciones ({len(self.filtered_organizations)})",
                style="headlineSmall",
                weight=ft.FontWeight.BOLD
            ),
            ft.Container(
                content=self.organizations_container,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                padding=10,
                expand=True
            ),
            pagination_controls
        ], spacing=20, expand=True)
        
        self.page.add(ft.Container(content=content, padding=20, expand=True))
        self._update_organizations_display()
        self.page.update()
    
    def _create_filters_section(self):
        """Create filters section"""
        # Create filter controls
        nif_filter = self.create_text_filter(
            "nif",
            "NIF",
            "Buscar por NIF",
            self._apply_filters
        )
        
        name_filter = self.create_text_filter(
            "name",
            "Nombre",
            "Buscar por nombre",
            self._apply_filters
        )
        
        # Clear filters button
        clear_button = ft.ElevatedButton(
            text="Limpiar filtros",
            icon=ft.Icons.CLEAR,
            on_click=lambda e: self._clear_filters()
        )
        
        # Responsive layout for filters
        return ft.ResponsiveRow([
            ft.Container(nif_filter, col=create_responsive_columns(12, 6, 4)),
            ft.Container(name_filter, col=create_responsive_columns(12, 6, 4)),
            ft.Container(clear_button, col=create_responsive_columns(12, 6, 4)),
        ], spacing=10)
    
    def _apply_filters(self, filter_key: str = None, filter_value: str = None):
        """Apply all filters to the organizations list"""
        self.filtered_organizations = self.all_organizations.copy()
        
        # Apply NIF filter
        nif_filter = self.get_filter_value("nif")
        if nif_filter:
            self.filtered_organizations = [
                org for org in self.filtered_organizations
                if nif_filter.lower() in org.nif.lower()
            ]
        
        # Apply name filter
        name_filter = self.get_filter_value("name")
        if name_filter:
            search_term = name_filter.lower()
            self.filtered_organizations = [
                org for org in self.filtered_organizations
                if search_term in org.nombre.lower()
            ]
        
        # Update pagination and display
        self.current_page = 1
        self.update_pagination(len(self.filtered_organizations))
        self._update_organizations_display()
    
    def _clear_filters(self):
        """Clear all filters"""
        self.clear_filters()
        self.filtered_organizations = self.all_organizations.copy()
        self.current_page = 1
        self.update_pagination(len(self.filtered_organizations))
        self._update_organizations_display()
    
    def _on_page_change(self, page_num: int):
        """Handle page change"""
        self.current_page = page_num
        self._update_organizations_display()
    
    def _update_organizations_display(self):
        """Update the organizations display based on current page and filters"""
        self.organizations_container.controls.clear()
        
        # Calculate pagination
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_organizations = self.filtered_organizations[start_idx:end_idx]
        
        if not page_organizations:
            self.organizations_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No se encontraron organizaciones con los filtros aplicados",
                        style="bodyLarge",
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            for organization in page_organizations:
                org_card = self._create_organization_card(organization)
                self.organizations_container.controls.append(org_card)
        
        self.page.update()
    
    def _create_organization_card(self, organization: OrganizationShortView) -> ft.Card:
        """Create an organization card component"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header row with name and NIF
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.APARTMENT, color=ft.Colors.PRIMARY),
                            ft.Text(
                                organization.nombre,
                                weight=ft.FontWeight.BOLD,
                                size=16
                            )
                        ], spacing=10),
                        ft.Text(f"NIF: {organization.nif}", size=12, color=ft.Colors.GREY_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Contact info
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.GREY_600),
                            ft.Text(organization.email or "Sin email", size=14)
                        ], spacing=5) if organization.email else ft.Text("Sin email", size=14, color=ft.Colors.GREY_500),
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                            ft.Text(organization.telefono or "Sin teléfono", size=14)
                        ], spacing=5) if organization.telefono else ft.Text("Sin teléfono", size=14, color=ft.Colors.GREY_500)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Action buttons
                    ft.Row([
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            height=32,
                            on_click=lambda e, o=organization: self._edit_organization(o)
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                    
                ], spacing=10),
                padding=15
            ),
            elevation=2,
            margin=ft.margin.only(bottom=10)
        )
    
    def _edit_organization(self, organization: OrganizationShortView):
        """Navigate to organization edit view"""
        self.page.session.set("selected_organization_id", organization.id_organizacion)
        self.page.session.set("edit_mode", False)
        self.router.navigate_to(Routes.ORGANIZATION_DETAIL)