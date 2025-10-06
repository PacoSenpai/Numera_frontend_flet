# views/base/mixins.py
import flet as ft
from typing import List, Dict, Callable, Optional, Any
from utils.helpers import create_responsive_columns, is_mobile


class FilterMixin:
    """Mixin for views that need filtering functionality"""
    
    def __init__(self):
        self.filters = {}
        self.filter_controls = {}
    
    def create_text_filter(self, key: str, label: str, hint: str = None, on_change: Callable = None):
        """Create a text filter field"""
        filter_field = ft.TextField(
            label=label,
            hint_text=hint,
            expand=True,
            on_change=lambda e: self._handle_filter_change(key, e.control.value, on_change)
        )
        self.filter_controls[key] = filter_field
        return filter_field
    
    def create_dropdown_filter(self, key: str, label: str, options: List[str], on_change: Callable = None):
        """Create a dropdown filter"""
        dropdown = ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(opt) for opt in options],
            expand=True,
            on_change=lambda e: self._handle_filter_change(key, e.control.value, on_change)
        )
        self.filter_controls[key] = dropdown
        return dropdown
    
    def create_date_filter(self, key: str, label: str, on_change: Callable = None):
        """Create a date filter with date picker"""
        date_button = ft.ElevatedButton(
            text=label,
            expand=True,
            on_click=lambda e: self._show_date_picker(key, on_change)
        )
        self.filter_controls[key] = date_button
        return date_button
    
    def _handle_filter_change(self, key: str, value: Any, callback: Callable = None):
        """Handle filter value changes"""
        self.filters[key] = value
        if callback:
            callback(key, value)
    
    def _show_date_picker(self, key: str, callback: Callable = None):
        """Show date picker for date filters"""
        date_picker = ft.DatePicker(
            on_change=lambda e: self._handle_date_selection(key, e.control.value, callback)
        )
        self.page.overlay.append(date_picker)
        date_picker.pick_date()
        self.page.update()
    
    def _handle_date_selection(self, key: str, date_value, callback: Callable = None):
        """Handle date selection"""
        if date_value:
            date_str = date_value.strftime("%Y-%m-%d")
            self.filters[key] = date_str
            # Update button text
            if key in self.filter_controls:
                self.filter_controls[key].text = f"{key}: {date_value.strftime('%d/%m/%Y')}"
                self.page.update()
            
            if callback:
                callback(key, date_str)
    
    def get_filter_value(self, key: str):
        """Get current filter value"""
        return self.filters.get(key)
    
    def clear_filters(self):
        """Clear all filters"""
        self.filters.clear()
        for control in self.filter_controls.values():
            if isinstance(control, ft.TextField):
                control.value = ""
            elif isinstance(control, ft.Dropdown):
                control.value = None
            elif isinstance(control, ft.ElevatedButton):
                # Reset button text to original
                pass
        self.page.update()


class PaginationMixin:
    """Mixin for views that need pagination"""
    
    def __init__(self):
        self.current_page = 1
        self.page_size = 20
        self.total_items = 0
        self.total_pages = 0
    
    def create_pagination_controls(self, on_page_change: Callable):
        """Create pagination controls"""
        self.pagination_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[]
        )
        self.on_page_change = on_page_change
        return self.pagination_row
    
    def update_pagination(self, total_items: int):
        """Update pagination controls based on total items"""
        self.total_items = total_items
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        self.pagination_row.controls.clear()
        
        if self.total_pages <= 1:
            return
        
        # Previous button
        prev_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            disabled=self.current_page == 1,
            on_click=lambda e: self._go_to_page(self.current_page - 1)
        )
        self.pagination_row.controls.append(prev_btn)
        
        # Page numbers
        start_page = max(1, self.current_page - 2)
        end_page = min(self.total_pages, start_page + 4)
        
        for page_num in range(start_page, end_page + 1):
            btn = ft.TextButton(
                text=str(page_num),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY if page_num == self.current_page else None
                ),
                on_click=lambda e, p=page_num: self._go_to_page(p)
            )
            self.pagination_row.controls.append(btn)
        
        # Next button
        next_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            disabled=self.current_page == self.total_pages,
            on_click=lambda e: self._go_to_page(self.current_page + 1)
        )
        self.pagination_row.controls.append(next_btn)
        
        # Page info
        info_text = ft.Text(
            f"Página {self.current_page} de {self.total_pages} ({self.total_items} elementos)"
        )
        self.pagination_row.controls.append(info_text)
        
        self.page.update()
    
    def _go_to_page(self, page_num: int):
        """Navigate to specific page"""
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            self.on_page_change(page_num)