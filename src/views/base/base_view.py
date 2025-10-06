# views/base/base_view.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import flet as ft
from core.navigation import NavigationMixin
from core.exceptions import APIError, AuthenticationError, NetworkError
from utils.helpers import show_error_message, show_success_message, show_info_message


class LoadingMixin:
    """Mixin for loading state management"""
    
    def __init__(self):
        self._loading_overlay = None
        self._is_loading = False
    
    def show_loading(self, message: str = "Cargando..."):
        """Show loading overlay"""
        if self._is_loading:
            return
            
        self._is_loading = True
        self._loading_overlay = ft.AlertDialog(
            modal=True,
            content=ft.Row([
                ft.ProgressRing(scale=0.5),
                ft.Text(message)
            ], tight=True),
        )
        self.page.dialog = self._loading_overlay
        #self._loading_overlay.open = True
        self.page.open(self.page.dialog)
        self.page.update()
    
    def hide_loading(self):
        """Hide loading overlay"""
        if not self._is_loading:
            return
            
        self._is_loading = False
        if self._loading_overlay:
            #self._loading_overlay.open = False
            self.page.close(self.page.dialog)
            #self.page.dialog = None
            self.page.update()


class ErrorHandlingMixin:
    """Mixin for error handling"""
    
    def handle_error(self, error: Exception):
        """Handle different types of errors"""
        if isinstance(error, AuthenticationError):
            show_error_message(self.page, "Sesión expirada. Redirigiendo al login...")
            # Router will handle redirect automatically
        elif isinstance(error, NetworkError):
            show_error_message(self.page, f"Error de conexión: {str(error)}")
        elif isinstance(error, APIError):
            show_error_message(self.page, f"Error: {str(error)}")
        else:
            show_error_message(self.page, f"Error inesperado: {str(error)}")


class BaseView(ABC, NavigationMixin, LoadingMixin, ErrorHandlingMixin):
    """Base class for all views"""
    
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__()
        self.page = page
        self.router = router
        self.services = services
        self.session_manager = session_manager
        self.kwargs = kwargs
        
        # Clear any existing floating action button
        self.page.floating_action_button = None
    
    @abstractmethod
    def show(self):
        """Each view must implement this method"""
        pass
    
    def setup_page_config(self, title: str):
        """Setup basic page configuration"""
        self.setup_navigation(title)
        self.page.title = title
        self.page.scroll = ft.ScrollMode.AUTO
    
    def safe_api_call(self, api_call, loading_message: str = "Cargando...", success_message: str = None):
        """Safely execute API call with error handling and loading states"""
        try:
            #self.show_loading(loading_message)
            result = api_call()
            
            if success_message:
                show_success_message(self.page, success_message)
            
            
        except Exception as e:
            self.handle_error(e)
            return None
        finally:
            #self.hide_loading()
            pass
             
        return result
