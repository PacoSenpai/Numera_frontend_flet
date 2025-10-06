# views/events/event_detail.py
import flet as ft
from typing import Optional
from views.base.base_view import BaseView
from models.event import EventDetail, EventUpdate
from utils.helpers import show_success_message, show_error_message
from config.constants import Routes


class EventDetailView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.event_id = None
        self.event_data: Optional[EventDetail] = None
        self.form_fields = {}
        self.is_editing = False

    def show(self):
        """Show event detail view"""
        self.event_id = self.page.session.get("selected_event_id")
        self.is_editing = self.page.session.get("edit_mode")

        if not self.event_id:
            show_error_message(self.page, "No se ha seleccionado ningún evento")
            self.router.navigate_to(Routes.EVENTS)
            return

        # Recuperar el evento desde la sesión
        event_dict = self.page.session.get("selected_event_data")
        if not event_dict:
            show_error_message(self.page, "No se ha podido cargar el evento")
            self.router.navigate_to(Routes.EVENTS)
            return

        self.event_data = EventDetail(**event_dict)

        self.setup_page_config("Detalles del Evento")
        self._setup_content()

    def _setup_content(self):
        """Setup the main content"""
        if not self.event_data:
            return

        # Header with event info and actions
        header = self._create_header()

        # Form sections
        basic_section = self._create_basic_info_section()

        # Action buttons
        actions_section = self._create_actions_section()

        # Main layout
        content = ft.Column([
            header,
            ft.Divider(),
            basic_section,
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
            ft.Column([
                ft.Text(
                    self.event_data.name,
                    style="headlineMedium",
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(f"ID: {self.event_data.event_id}", color=ft.Colors.GREY_600)
            ], expand=True),
            ft.Switch(
                label="Modo edición",
                value=self.is_editing,
                on_change=self._toggle_edit_mode
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _create_basic_info_section(self):
        self.form_fields['name'] = ft.TextField(
            label="Nombre",
            value=self.event_data.name,
            read_only=not self.is_editing
        )

        self.form_fields['description'] = ft.TextField(
            label="Descripción",
            value=self.event_data.description,
            read_only=not self.is_editing,
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        self.form_fields['year'] = ft.TextField(
            label="Año",
            value=str(self.event_data.year),
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.form_fields['month'] = ft.TextField(
            label="Mes (opcional)",
            value=str(self.event_data.month) if self.event_data.month else "",
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.form_fields['day'] = ft.TextField(
            label="Día (opcional)",
            value=str(self.event_data.day) if self.event_data.day else "",
            read_only=not self.is_editing,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        return ft.Column([
            ft.Text("Información del Evento", style="titleLarge", weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Container(self.form_fields['name'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['description'], col={"xs": 12, "md": 6}),
                ft.Container(self.form_fields['year'], col={"xs": 12, "md": 4}),
                ft.Container(self.form_fields['month'], col={"xs": 12, "md": 4}),
                ft.Container(self.form_fields['day'], col={"xs": 12, "md": 4}),
            ])
        ])

    def _create_actions_section(self):
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
                    on_click=lambda e: self.router.navigate_to(Routes.EVENTS)
                )
            ])

    def _toggle_edit_mode(self, e):
        self.is_editing = not self.is_editing
        for field in self.form_fields.values():
            if hasattr(field, 'read_only'):
                field.read_only = not self.is_editing

        self.page.clean()
        self.setup_page_config("Detalles del Evento")
        self._setup_content()

    def _save_changes(self, e):
        errors = self._validate_form()
        if errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(errors)}")
            return

        update_data = EventUpdate(
            event_id=self.event_id,
            name=self.form_fields['name'].value,
            description=self.form_fields['description'].value,
            year=int(self.form_fields['year'].value),
            month=int(self.form_fields['month'].value) if self.form_fields['month'].value else None,
            day=int(self.form_fields['day'].value) if self.form_fields['day'].value else None
        )

        success = self.safe_api_call(
            lambda: self.services.events.update_event(update_data),
            loading_message="Guardando cambios...",
            success_message="Evento actualizado correctamente"
        )

        if success:
            # Actualizar también en la sesión
            self.page.session.set("selected_event_data", update_data.dict())
            self.event_data = EventDetail(**update_data.dict())
            self.is_editing = False
            self.page.clean()
            self.setup_page_config("Detalles del Evento")
            self._setup_content()

    def _validate_form(self) -> list:
        errors = []

        if not self.form_fields['name'].value:
            errors.append("Nombre es obligatorio")
        if not self.form_fields['description'].value:
            errors.append("Descripción es obligatoria")
        if not self.form_fields['year'].value or not self.form_fields['year'].value.isdigit():
            errors.append("El año debe ser un número válido")
        elif int(self.form_fields['year'].value) <= 0:
            errors.append("El año debe ser positivo")

        if self.form_fields['month'].value and (
            not self.form_fields['month'].value.isdigit() or not (1 <= int(self.form_fields['month'].value) <= 12)
        ):
            errors.append("El mes debe estar entre 1 y 12")

        if self.form_fields['day'].value and (
            not self.form_fields['day'].value.isdigit() or not (1 <= int(self.form_fields['day'].value) <= 31)
        ):
            errors.append("El día debe estar entre 1 y 31")

        return errors
