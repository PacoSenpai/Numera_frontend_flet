# Component examples for reusability
# components/common/forms.py
import flet as ft
from typing import List, Optional, Callable, Dict, Any
from datetime import date


class FormField:
    """Base form field wrapper"""
    def __init__(self, control: ft.Control, label: str, required: bool = False, validator: Optional[Callable] = None):
        self.control = control
        self.label = label
        self.required = required
        self.validator = validator
        self.error_text = None
    
    def validate(self) -> bool:
        """Validate field and return True if valid"""
        if self.required and not self.get_value():
            self.error_text = f"{self.label} es obligatorio"
            return False
        
        if self.validator and self.get_value():
            try:
                self.validator(self.get_value())
            except ValueError as e:
                self.error_text = str(e)
                return False
        
        self.error_text = None
        return True
    
    def get_value(self):
        """Get field value"""
        if hasattr(self.control, 'value'):
            return self.control.value
        return None
    
    def set_value(self, value):
        """Set field value"""
        if hasattr(self.control, 'value'):
            self.control.value = value


class ResponsiveForm:
    """Responsive form builder"""
    def __init__(self, page: ft.Page):
        self.page = page
        self.fields: Dict[str, FormField] = {}
        self.sections: List[Dict] = []
    
    def add_section(self, title: str, fields: List[Dict]):
        """Add a form section with fields"""
        section = {
            "title": title,
            "fields": fields
        }
        self.sections.append(section)
        
        # Create form fields
        for field_config in fields:
            field_name = field_config["name"]
            field_type = field_config.get("type", "text")
            
            # Create appropriate control based on type
            if field_type == "text":
                control = ft.TextField(
                    label=field_config["label"],
                    hint_text=field_config.get("hint"),
                    multiline=field_config.get("multiline", False),
                    max_lines=field_config.get("max_lines", 1),
                    keyboard_type=field_config.get("keyboard_type", ft.KeyboardType.TEXT)
                )
            elif field_type == "dropdown":
                control = ft.Dropdown(
                    label=field_config["label"],
                    options=[ft.dropdown.Option(opt) for opt in field_config["options"]]
                )
            elif field_type == "date":
                control = ft.TextField(
                    label=field_config["label"],
                    read_only=True,
                    suffix=ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=lambda e, name=field_name: self._show_date_picker(name)
                    )
                )
            else:
                control = ft.TextField(label=field_config["label"])
            
            # Create form field
            form_field = FormField(
                control=control,
                label=field_config["label"],
                required=field_config.get("required", False),
                validator=field_config.get("validator")
            )
            
            self.fields[field_name] = form_field
    
    def build(self) -> ft.Column:
        """Build the complete form"""
        form_controls = []
        
        for section in self.sections:
            # Section title
            if section["title"]:
                form_controls.append(
                    ft.Text(section["title"], style="titleMedium", weight=ft.FontWeight.BOLD)
                )
            
            # Create responsive row for section fields
            section_controls = []
            for field_config in section["fields"]:
                field_name = field_config["name"]
                field = self.fields[field_name]
                
                col_config = field_config.get("col", {"xs": 12, "md": 6})
                section_controls.append(
                    ft.Container(field.control, col=col_config)
                )
            
            form_controls.append(ft.ResponsiveRow(section_controls))
        
        return ft.Column(form_controls, spacing=20)
    
    def validate(self) -> bool:
        """Validate entire form"""
        is_valid = True
        for field in self.fields.values():
            if not field.validate():
                is_valid = False
        return is_valid
    
    def get_data(self) -> Dict[str, Any]:
        """Get all form data as dictionary"""
        data = {}
        for name, field in self.fields.items():
            data[name] = field.get_value()
        return data
    
    def set_data(self, data: Dict[str, Any]):
        """Set form data from dictionary"""
        for name, value in data.items():
            if name in self.fields:
                self.fields[name].set_value(value)
    
    def _show_date_picker(self, field_name: str):
        """Show date picker for date fields"""
        date_picker = ft.DatePicker(
            on_change=lambda e: self._handle_date_selection(field_name, e.control.value)
        )
        self.page.overlay.append(date_picker)
        date_picker.pick_date()
        self.page.update()
    
    def _handle_date_selection(self, field_name: str, selected_date: date):
        """Handle date selection"""
        if selected_date and field_name in self.fields:
            formatted_date = selected_date.strftime("%d/%m/%Y")
            self.fields[field_name].set_value(formatted_date)
            self.page.update()