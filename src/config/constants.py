# config/constants.py
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "usuario_activo"
    INACTIVE = "usuario_inactivo"
    ACTIVE_ID = "1"
    INACTIVE_ID = "2"


class CREStatus(Enum):
    COMPLETE = "cre_completo"
    INCOMPLETE = "cre_incompleto"
    COMPLETE_ID = "3"
    INCOMPLETE_ID = "4"

class RGCREStatus(Enum):
    COMPLETE = "rgcre_completo"
    INCOMPLETE = "rgcre_incompleto"
    COMPLETE_ID = "5"
    INCOMPLETE_ID = "6"

class MovementType(Enum):
    INCOME_ID = 12
    EXPENSE_ID = 13
    INCOME = "mov_eco_entrada"
    EXPENSE = "mov_eco_salida"

class MovementState(Enum):
    DRAFT = 7
    PENDING_REVIEW = 8
    REVIEWED = 9

class CashBoxState(Enum):
    IN_CASH = 14
    NOT_IN_CASH = 15

class InvoiceComputable(Enum):
    COMPUTABLE = 10
    NOT_COMPUTABLE = 11

class Permissions(Enum):
    # Home
    HOME = "home"
    
    # Perfil
    PROFILE = "profile"
    CHANGE_PASSWORD = "change_password"
    
    # Usuarios
    USERS_LIST = "users_list"
    USERS_MANAGE = "users_manage"
    
    # Organización
    ORGANIZATION_LIST = "organization_list"
    ORGANIZATION_MANAGE = "organization_manage"
    
    # Eventos
    EVENTS_LIST = "events_list"
    EVENTS_MANAGE = "events_manage"
    
    # Roles
    ROLES_LIST = "roles_list"
    ROLES_MANAGE = "roles_manage"
    ROLES_BY_USER = "roles_by_user"
    
    # Categorías
    CATEGORY_LIST = "category_list"
    
    # Documentos contables
    ACCOUNTING_DOCS_READ = "accounting_docs_read"
    ACCOUNTING_DOCS_MANAGE = "accounting_docs_manage"
    
    # Movimientos económicos
    MOVEMENTS_READ = "movements_read"
    MOVEMENTS_MANAGE = "movements_manage"
    MOVEMENTS_MANAGE_REVIEWED = "movements_manage_reviwed"
    
    # Facturas
    INVOICE_READ = "invoice_read"
    INVOICE_WRITE = "invoice_write"
    
    # Permisos genéricos
    LECTURA = "lectura"
    ESCRITURA = "escritura"

# Navigation routes
class Routes:
    LOGIN = "/login"
    HOME = "/home"
    PROFILE = "/profile"
    ECONOMY = "/economy"
    ECONOMY_MOVEMENTS = "/economy_movements"
    ECONOMY_STATISTICS = "/economy_statistics"
    ECONOMY_MOVEMENT_DETAIL = "/economy_movement_detail"
    ECONOMY_MOVEMENT_CREATE = "/economy_movement_create"
    USERS = "/users"
    USER_DETAIL = "/user_detail"
    USER_CREATE = "/user_create"
    ORGANIZATIONS = "/organizations"
    ORGANIZATION_DETAIL = "/organization_detail"
    ORGANIZATION_CREATE = "/organization_create"
    EVENTS = "/events"
    EVENT_DETAIL = "/event_detail"
    EVENT_CREATE = "/event_create"
    LOGOUT = "/logout"

# Mapeo de rutas a permisos requeridos
ROUTE_PERMISSIONS = {
    Routes.HOME: [Permissions.HOME],
    Routes.PROFILE: [Permissions.PROFILE],
    Routes.USERS: [Permissions.USERS_LIST],
    Routes.USER_CREATE: [Permissions.USERS_MANAGE],
    Routes.USER_DETAIL: [Permissions.USERS_MANAGE],
    Routes.ORGANIZATIONS: [Permissions.ORGANIZATION_LIST],
    Routes.ORGANIZATION_CREATE: [Permissions.ORGANIZATION_MANAGE],
    Routes.ORGANIZATION_DETAIL: [Permissions.ORGANIZATION_MANAGE],
    Routes.EVENTS: [Permissions.EVENTS_LIST],
    Routes.EVENT_CREATE: [Permissions.EVENTS_MANAGE],
    Routes.EVENT_DETAIL: [Permissions.EVENTS_MANAGE],
    Routes.ECONOMY: [Permissions.MOVEMENTS_READ],
    Routes.ECONOMY_MOVEMENTS: [Permissions.MOVEMENTS_READ],
    Routes.ECONOMY_MOVEMENT_DETAIL: [Permissions.MOVEMENTS_MANAGE],
    Routes.ECONOMY_MOVEMENT_CREATE: [Permissions.MOVEMENTS_MANAGE],
}
