# services/accounting_service.py
from typing import List
from models.accounting_docs import DocsContablesListItem, DocsContablesUpdate
from .api_client import APIClient

class AccountingService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_accounting_docs_by_movement(self, movement_id: int) -> List[DocsContablesListItem]:
        """Get accounting documents for a specific movement"""
        response = self.api.request(
            "GET",
            "/accounting_docs/accounting_docs_list",
            query_params={"movimiento_id": movement_id}
        )
        return [DocsContablesListItem(**doc) for doc in response.json()]
    
    def delete_accounting_doc(self, doc_id: int) -> bool:
        """Delete an accounting document"""
        response = self.api.request(
            "DELETE",
            "/accounting_docs/delete_accounting_doc",
            query_params={"doc_id": doc_id}
        )
        return response.status_code == 200
    
    def update_accounting_doc(self, doc_id: int, doc_data: DocsContablesUpdate) -> bool:
        """Update accounting document data"""
        response = self.api.request(
            "POST",
            "/accounting_docs/update_accounting_doc",
            query_params={"doc_id": doc_id},
            json_data=doc_data
        )
        return response.status_code == 200
    
    def upload_accounting_doc(self, movement_id: int, nombre: str, file_data) -> bool:
        """Upload a new accounting document"""
        response = self.api.request(
            "POST",
            "/accounting_docs/upload_accounting_doc",
            query_params={"movimiento_id": movement_id, "nombre": nombre},
            files={"file": file_data}
        )
        return response.status_code == 201
    
    def download_accounting_doc(self, doc_id: int):
        """Download an accounting document"""
        response = self.api.request(
            "GET",
            "/accounting_docs/download_accounting_doc",
            query_params={"doc_id": doc_id}
        )
        return response