# main.py
import flet as ft
from core.router import Router
from config.settings import settings

def main(page: ft.Page):
    """Main application entry point"""
    # Configure page
    page.title = settings.APP_TITLE
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Set theme colors
    page.theme = ft.Theme(
        color_scheme_seed=settings.PRIMARY_COLOR,
        use_material3=True
    )
    
    # Initialize router
    router = Router(page)
    
    # Check if user is already logged in
    if router.session_manager.is_authenticated():
        router.navigate_to("/home")
    else:
        router.navigate_to("/login")

if __name__ == "__main__":
    ft.app(target=main)
