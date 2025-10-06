# views/auth/login_view.py
import flet as ft
import jwt
from datetime import datetime
from models.auth import UserLogin
from views.base.base_view import BaseView
from config.constants import Routes
from utils.helpers import show_error_message
from core.exceptions import APIError


class LoginView(BaseView):
    def __init__(self, page: ft.Page, router, services, session_manager, **kwargs):
        super().__init__(page, router, services, session_manager, **kwargs)
        self.email_field = None
        self.password_field = None
        self.login_button = None
    
    def show(self):
        """Show login view"""
        # Clear any existing navigation
        self.page.appbar = None
        self.page.drawer = None
        
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup login UI"""
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            autofocus=True,
            keyboard_type=ft.KeyboardType.EMAIL
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            width=300,
            password=True,
            on_submit=self._on_login
        )
        
        self.login_button = ft.ElevatedButton(
            text="Iniciar Sesión",
            width=300,
            height=45,
            on_click=self._on_login
        )
        
        # Create login form
        login_form = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "La Satanica",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PRIMARY
                    ),
                    margin=ft.margin.only(bottom=30)
                ),
                self.email_field,
                self.password_field,
                ft.Container(height=20),
                self.login_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
        
        # Add to page
        self.page.add(
            ft.Container(
                content=login_form,
                alignment=ft.alignment.center,
                expand=True
            )
        )
        self.page.update()
    
    def _on_login(self, e):
        """Handle login button click"""
        email = self.email_field.value
        password = self.password_field.value
        
        if not email or not password:
            show_error_message(self.page, "Email y contraseña son obligatorios")
            return
        
        # Create login credentials
        credentials = UserLogin(email=email, password=password)
        
        # Attempt login
        result = self.safe_api_call(
            lambda: self.services.auth.login(credentials),
            loading_message="Iniciando sesión...",
            success_message="¡Bienvenido!"
        )
        
        if result:
            # Decode token to get user info
            try:
                decoded_token = jwt.decode(
                    result.access_token,
                    options={"verify_signature": False}
                )
                
                # Store session
                self.session_manager.set_session(result.model_dump(), decoded_token)
                
                # Set token in API client
                self.services.api_client.set_token(result.access_token)

                self.safe_api_call(
                    lambda: self.services.permissions.load_user_permissions(),
                    loading_message="Cargando permisos..."
                )
                
                # Navigate to home
                self.router.navigate_to(Routes.HOME)
                
            except Exception as ex:
                show_error_message(self.page, f"Error procesando token: {str(ex)}")