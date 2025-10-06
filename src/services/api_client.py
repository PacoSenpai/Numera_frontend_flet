# services/api_client.py
import httpx
import json
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel
from datetime import datetime
import logging

from config.settings import settings
from core.exceptions import (
    APIError, 
    AuthenticationError,
    NetworkError, 
    ValidationError,
    NotFoundError,
    ServerError
)

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = settings.SERVER_ROUTE.rstrip('/')
        self.timeout = settings.API_TIMEOUT
        self._token = None
        self._session_manager = None
    
    def set_session_manager(self, session_manager):
        """Inject session manager for token management"""
        self._session_manager = session_manager
    
    @property
    def token(self) -> Optional[str]:
        """Get current authentication token"""
        if self._session_manager:
            return self._session_manager.get_token()
        return self._token
    
    def set_token(self, token: str):
        """Set authentication token"""
        self._token = token
    
    def clear_token(self):
        """Clear authentication token"""
        self._token = None
    
    def request(
        self,
        method: str,
        endpoint: str,
        query_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict, BaseModel]] = None,
        files: Optional[Dict] = None,
        requires_auth: bool = True
    ) -> httpx.Response:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (should start with /)
            query_params: Query parameters dict
            json_data: JSON data for request body
            files: Files for multipart upload
            requires_auth: Whether this endpoint requires authentication
            
        Returns:
            httpx.Response object
            
        Raises:
            APIError: For various API-related errors
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            params = query_params or {}

            params = {k: v for k, v in params.items() if v is not None}
            
            if requires_auth and self.token:
                params["token"] = self.token
            
            json_payload = None
            if json_data:
                if isinstance(json_data, BaseModel):
                    json_payload = json_data.model_dump(exclude_unset=True)
                else:
                    json_payload = json_data
                    
                json_payload = {k: v for k, v in json_payload.items() if v is not None}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_payload,
                    files=files
                )
                
                self._handle_response(response)
                return response
                
        except httpx.TimeoutException:
            raise NetworkError("Request timeout - server not responding")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in API request: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")

    
    def _handle_response(self, response: httpx.Response):
        """Handle API response and raise appropriate exceptions"""
        if response.status_code < 400:
            return  # Success
            
        try:
            error_data = response.json()
            detail = error_data.get("detail", "No details provided")
        except:
            detail = response.text or "No error details"
        
        if response.status_code == 401:
            # Token expired or invalid
            self.clear_token()
            if self._session_manager:
                self._session_manager.clear_session()
            raise AuthenticationError("Authentication failed - please login again")
        elif response.status_code == 403:
            raise AuthenticationError("Access forbidden - insufficient permissions")
        elif response.status_code == 404:
            raise NotFoundError("Resource not found")
        elif response.status_code == 422:
            raise ValidationError(f"Validation error: {detail}")
        elif response.status_code >= 500:
            raise ServerError(f"Server error: {detail}")
        else:
            raise APIError(f"API error {response.status_code}: {detail}")