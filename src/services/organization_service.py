# services/organization_service.py
from typing import List
from models.organization import (
    OrganizationShortView,
    OrganizationDetail,
    OrganizationCreate,
    OrganizationUpdate
)
from .api_client import APIClient

class OrganizationService:
    def __init__(self, api_client: APIClient):
        self.api = api_client
    
    def get_organizations_list(self) -> List[OrganizationShortView]:
        """Get list of all organizations"""
        response = self.api.request("GET", "/organization/organizations_list")
        return [OrganizationShortView(**org) for org in response.json()]
    
    def get_organization_details(self, org_id: int) -> OrganizationDetail:
        """Get detailed information about a specific organization"""
        response = self.api.request(
            "GET",
            "/organization/organization_details",
            query_params={"organization_id": org_id}
        )
        return OrganizationDetail(**response.json())
    
    def create_organization(self, org_data: OrganizationCreate) -> bool:
        """Create a new organization"""
        response = self.api.request(
            "POST",
            "/organization/create_organization",
            json_data=org_data
        )
        return response.status_code == 201
    
    def update_organization(self, org_data: OrganizationUpdate) -> bool:
        """Update existing organization"""
        response = self.api.request(
            "POST",
            "/organization/organization_update",
            json_data=org_data
        )
        return response.status_code == 200