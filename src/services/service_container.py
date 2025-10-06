# services/service_container.py
from .api_client import APIClient
from .auth_service import AuthService
from .user_service import UserService
from .economic_service import EconomicService
from .accounting_docs_service import AccountingService
from .organization_service import OrganizationService
from .home_service import HomeService
from .event_service import EventService
from .invoice_service import InvoiceService
from .permission_service import PermissionService
from .role_service import RoleService

class ServiceContainer:
    """Dependency injection container for services"""
    
    def __init__(self):
        # Initialize API client
        self.api_client = APIClient()
        
        # Initialize services
        self.auth = AuthService(self.api_client)
        self.users = UserService(self.api_client)
        self.economic = EconomicService(self.api_client)
        self.accounting = AccountingService(self.api_client)
        self.organizations = OrganizationService(self.api_client)
        self.home = HomeService(self.api_client)
        self.events = EventService(self.api_client)
        self.invoices = InvoiceService(self.api_client)
        self.permissions = PermissionService(self.api_client)
        self.roles = RoleService(self.api_client)
    
    def set_session_manager(self, session_manager):
        """Set session manager for token handling"""
        self.api_client.set_session_manager(session_manager)