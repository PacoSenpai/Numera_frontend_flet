# views/events/event_form.py
import flet as ft
from views.base.base_view import BaseView
from models.event import EventCreate
from utils.validators import validate_required_field
from utils.helpers import show_success_message, show_error_message
from config.constants import Routes


class EventFormView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.form_fields = {}
    
    def show(self):
        """Show event creation view"""
        self.setup_page_config("Crear Nuevo Evento")
        self._setup_content()
    
    def _setup_content(self):
        """Setup the main content"""
        header = self._create_header()
        
        basic_section = self._create_basic_info_section()
        actions_section = self._create_actions_section()
        
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
            ft.Text(
                "Crear Nuevo Evento",
                style="headlineMedium",
                weight=ft.FontWeight.BOLD
            )
        ])
    
    def _create_basic_info_section(self):
        self.form_fields['name'] = ft.TextField(
            label="Nombre*",
            on_change=lambda e: self._validate_field(e, "name")
        )
        
        self.form_fields['description'] = ft.TextField(
            label="Descripción*",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=lambda e: self._validate_field(e, "description")
        )
        
        self.form_fields['year'] = ft.TextField(
            label="Año*",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._validate_year(e)
        )
        
        self.form_fields['month'] = ft.TextField(
            label="Mes (opcional)",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._validate_month(e)
        )
        
        self.form_fields['day'] = ft.TextField(
            label="Día (opcional)",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._validate_day(e)
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
        return ft.Row([
            ft.ElevatedButton(
                text="Crear Evento",
                icon=ft.Icons.ADD,
                on_click=self._create_event
            ),
            ft.ElevatedButton(
                text="Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: self.router.navigate_to(Routes.EVENTS)
            )
        ], spacing=10)
    
    def _validate_field(self, e, field_name):
        field = e.control
        if not field.value and field_name in ['name', 'description', 'year']:
            field.error_text = "Este campo es obligatorio"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_year(self, e):
        field = e.control
        if not field.value:
            field.error_text = "Este campo es obligatorio"
        elif not field.value.isdigit() or int(field.value) <= 0:
            field.error_text = "El año debe ser un número positivo"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_month(self, e):
        field = e.control
        if field.value and (not field.value.isdigit() or not (1 <= int(field.value) <= 12)):
            field.error_text = "El mes debe estar entre 1 y 12"
        else:
            field.error_text = None
        self.page.update()
    
    def _validate_day(self, e):
        field = e.control
        if field.value and (not field.value.isdigit() or not (1 <= int(field.value) <= 31)):
            field.error_text = "El día debe estar entre 1 y 31"
        else:
            field.error_text = None
        self.page.update()
    
    def _create_event(self, e):
        validation_errors = self._validate_form()
        if validation_errors:
            show_error_message(self.page, f"Errores de validación: {', '.join(validation_errors)}")
            return
        
        event_data = EventCreate(
            name=self.form_fields['name'].value,
            description=self.form_fields['description'].value,
            year=int(self.form_fields['year'].value),
            month=int(self.form_fields['month'].value) if self.form_fields['month'].value else None,
            day=int(self.form_fields['day'].value) if self.form_fields['day'].value else None
        )
        
        success = self.safe_api_call(
            lambda: self.services.events.create_event(event_data),
            loading_message="Creando evento...",
            success_message="Evento creado correctamente"
        )
        
        if success:
            self.router.navigate_to(Routes.EVENTS)
    
    def _validate_form(self) -> list:
        errors = []
        
        required_checks = [
            ('name', 'Nombre'),
            ('description', 'Descripción'),
            ('year', 'Año'),
        ]
        
        for field_name, display_name in required_checks:
            if not self.form_fields[field_name].value:
                errors.append(f"{display_name} es obligatorio")
        
        if self.form_fields['year'].value:
            if not self.form_fields['year'].value.isdigit() or int(self.form_fields['year'].value) <= 0:
                errors.append("El año debe ser un número positivo")
        
        if self.form_fields['month'].value:
            if not self.form_fields['month'].value.isdigit() or not (1 <= int(self.form_fields['month'].value) <= 12):
                errors.append("El mes debe estar entre 1 y 12")
        
        if self.form_fields['day'].value:
            if not self.form_fields['day'].value.isdigit() or not (1 <= int(self.form_fields['day'].value) <= 31):
                errors.append("El día debe estar entre 1 y 31")
        
        return errors