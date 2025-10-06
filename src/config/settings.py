# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
#from pydantic import Base

class Settings(BaseSettings):
    # API Configuration
    SERVER_ROUTE: str = "https://lasatanicabk.pacoserver.cc"#"http://127.0.0.1:8000"
    API_TIMEOUT: int = 30
    
    # UI Configuration
    APP_TITLE: str = "La Satanica"
    APP_VERSION: str = "1.0.0"
    
    # Responsive breakpoints
    MOBILE_BREAKPOINT: int = 768
    TABLET_BREAKPOINT: int = 1024
    
    # Theme colors
    PRIMARY_COLOR: str = "#ba3838"  # red
    SECONDARY_COLOR: str = "#d6c974"  # yellow
    ACCENT_COLOR: str = "#810099"  # purple
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()