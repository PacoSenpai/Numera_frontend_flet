# utils/validators.py
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_nif_nie(nif: str) -> bool:
    """
    Valida NIF/NIE para personas físicas (compatible con la función existente)
    """
    if not nif:
        return False
    
    nif_clean = nif.replace(" ", "").replace("-", "").upper()
    
    patrones = [
        r'^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$',
        r'^[XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$'
    ]
    
    for patron in patrones:
        if re.match(patron, nif_clean):
            return True
    
    return False

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Allow various phone formats
    pattern = r'^[+]?[\d\s\-\(\)]{9,15}$'
    return re.match(pattern, phone) is not None

def validate_iban(iban: str) -> bool:
    """Basic IBAN validation"""
    # Remove spaces and convert to uppercase
    iban = iban.replace(' ', '').upper()
    
    # Check length (Spanish IBAN should be 24 characters)
    if len(iban) != 24:
        return False
    
    # Check if all characters after ES are digits
    return iban[2:].isdigit()

def validate_required_field(value: Optional[str], field_name: str) -> Optional[str]:
    """Validate required field and return error message if invalid"""
    if not value or not value.strip():
        return f"{field_name} es obligatorio"
    return None

def validate_password(password: str) -> bool:
    """Validate password meets minimum requirements"""
    return len(password) >= 6 if password else False


def validate_nif_empresa(nif: str) -> bool:
    """
    Valida NIF de empresas españolas según los formatos oficiales.
    Formatos aceptados:
    - Letra (A,B,C,D,E,F,G,H,J,P,Q,R,S,U,V,N,W) + 7 números + dígito control (letra/número)
    - Para extranjeros: diferentes formatos con más de 9 caracteres
    """
    if not nif:
        return False
    
    # Limpiar espacios y convertir a mayúsculas
    nif_clean = nif.replace(" ", "").replace("-", "").upper()
    
    # Expresiones regulares para diferentes tipos de NIF
    patrones = [
        # Personas jurídicas españolas: Letra + 7 números + dígito control
        r'^[ABCDEFGHJLPQRSUVNW][0-9]{7}[0-9A-J]$',
        
        # NIF de personas físicas españolas: 8 números + letra
        r'^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$',
        
        # NIE para extranjeros: X,Y,Z + 7 números + letra
        r'^[XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$',
        
        # NIF de la Unión Europea (ej: GB, NL, PT, etc.)
        r'^[A-Z]{2}[0-9A-Z]{5,20}$',
        
        # Otros formatos internacionales
        r'^OT[0-9]{9,15}$',
        r'^[0-9A-Z]{10,20}$'  # Formatos más largos para extranjeros
    ]
    
    # Verificar si coincide con algún patrón
    for patron in patrones:
        if re.match(patron, nif_clean):
            return True
    
    return False