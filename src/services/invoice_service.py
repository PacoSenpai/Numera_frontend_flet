# services/invoice_service.py
from typing import List, Optional
from models.invoice import FacturaCreate, FacturaUpdate, FacturaListItem
from .api_client import APIClient
import tempfile

class InvoiceService:
    def __init__(self, api_client: APIClient):
        self.api = api_client

    def create_invoice(self, invoice_data: FacturaCreate) -> bool:
        """Create a new invoice"""
        response = self.api.request(
            "POST",
            "/invoices/create_invoice",
            json_data=invoice_data
        )
        return response.status_code == 201

    def update_invoice_data(self, invoice_id: int, update_data: FacturaUpdate) -> bool:
        """Update invoice data"""
        response = self.api.request(
            "POST",
            "/invoices/update_invoice_data",
            query_params={"factura_id": invoice_id},
            json_data=update_data
        )
        return response.status_code == 200

    def update_invoice_file(self, invoice_id: int, file_path: str) -> bool:
        """Upload invoice file (PDF)"""
        # This endpoint expects a file upload via multipart/form-data
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self.api.request(
                "POST",
                "/invoices/update_invoice_file",
                query_params={"factura_id": invoice_id},
                files=files
            )
        return response.status_code == 200
    
    def download_invoice(self, invoice_id: int) -> Optional[str]:
        """Download invoice file and return the local file path"""
        try:
            response = self.api.request(
                "GET",
                "/invoices/download_invoice",
                query_params={"factura_id": invoice_id}
            )
            
            if response.status_code == 200:
                # Archivo temporal para guardar la factura
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(response.content)
                    return temp_file.name
            else:
                return None
                
        except Exception as e:
            print(f"Error downloading invoice: {e}")
            return None

    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        response = self.api.request(
            "DELETE",
            "/invoices/delete_invoice",
            query_params={"factura_id": invoice_id}
        )
        return response.status_code == 200

    def get_invoices_by_movement(self, movement_id: int) -> List[FacturaListItem]:
        """Get invoices by movement ID"""
        response = self.api.request(
            "GET",
            "/invoices/get_invoices_by_movement",
            query_params={"movimiento_id": movement_id}
        )
        return [FacturaListItem(**invoice) for invoice in response.json()]