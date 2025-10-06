# services/economic_service.py
from typing import List, Optional
from models.economic import (
    EconomicMovementListItem,
    EconomicMovementDetail,
    EconomicMovementCreate,
    EconomicMovementUpdate,
    EconomicMovementFilters,
    CategoriaSubvencion
)
from models.invoice import FacturaListItem, FacturaCreate, FacturaUpdate
from .api_client import APIClient

class EconomicService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    # Economic Movements
    def get_last_movements(self) -> List[EconomicMovementListItem]:
        """Get recent economic movements"""
        response = self.api.request("GET", "/economic_movement/get_last_economic_movements")
        return [EconomicMovementListItem(**mov) for mov in response.json()]
    
    def get_movements_list(self, filters: EconomicMovementFilters) -> List[EconomicMovementListItem]:
        """Get filtered list of economic movements"""
        response = self.api.request(
            "GET",
            "/economic_movement/economic_movements_list",
            query_params=filters.model_dump(exclude_unset=True)
        )
        return [EconomicMovementListItem(**mov) for mov in response.json()]
    
    def get_movement_detail(self, movement_id: int) -> EconomicMovementDetail:
        """Get detailed information about a specific movement"""
        response = self.api.request(
            "GET",
            "/economic_movement/economic_movement_detail",
            query_params={"movement_id": movement_id}
        )
        return EconomicMovementDetail(**response.json())
    
    def create_movement(self, movement_data: EconomicMovementCreate) -> bool:
        """Create a new economic movement"""
        response = self.api.request(
            "POST",
            "/economic_movement/create_economic_movement",
            json_data=movement_data
        )
        return response.status_code == 201
    
    def update_movement(self, movement_id: int, movement_data: EconomicMovementUpdate) -> bool:
        """Update existing economic movement"""
        response = self.api.request(
            "POST",
            "/economic_movement/update_economic_movement",
            query_params={"movement_id": movement_id},
            json_data=movement_data
        )
        return response.status_code == 200
    
    def delete_movement(self, movement_id: int) -> bool:
        """Delete an economic movement"""
        response = self.api.request(
            "DELETE",
            "/economic_movement/delete_economic_movement",
            query_params={"movement_id": movement_id}
        )
        return response.status_code == 200
    
    # Categories
    def get_categories(self) -> List[CategoriaSubvencion]:
        """Get list of subsidy categories"""
        response = self.api.request("GET", "/categories/categories_list")
        return [CategoriaSubvencion(**cat) for cat in response.json()]
    
    # Invoices
    def get_invoices_by_movement(self, movement_id: int) -> List[FacturaListItem]:
        """Get invoices for a specific movement"""
        response = self.api.request(
            "GET",
            "/invoices/get_invoices_by_movement",
            query_params={"movimiento_id": movement_id}
        )
        return [FacturaListItem(**invoice) for invoice in response.json()]
    
    def create_invoice(self, invoice_data: FacturaCreate) -> bool:
        """Create a new invoice"""
        response = self.api.request(
            "POST",
            "/invoices/create_invoice",
            json_data=invoice_data
        )
        return response.status_code == 201
    
    def update_invoice_data(self, invoice_id: int, invoice_data: FacturaUpdate) -> bool:
        """Update invoice data"""
        response = self.api.request(
            "POST",
            "/invoices/update_invoice_data",
            query_params={"factura_id": invoice_id},
            json_data=invoice_data
        )
        return response.status_code == 200
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        response = self.api.request(
            "DELETE",
            "/invoices/delete_invoice",
            query_params={"factura_id": invoice_id}
        )
        return response.status_code == 200
