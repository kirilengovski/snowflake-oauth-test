"""
OAuth authentication module for Snowflake using Azure Service Principal.
Handles token acquisition and validation.
"""

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


class SnowflakeOAuthAuthenticator:
    """OAuth authenticator for Snowflake using Azure Service Principal."""
    
    def __init__(self, config):
        """
        Initialize OAuth authenticator.
        
        Args:
            config: SnowflakeOAuthConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._access_token = None
        self._token_expires_at = None
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            str: Valid access token
            
        Raises:
            Exception: If token acquisition fails
        """
        # Check if we have a valid token
        if (not force_refresh and 
            self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            self.logger.debug("Using cached access token")
            return self._access_token
        
        self.logger.info("Acquiring new access token from Azure AD")
        
        # Prepare token request
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.azure_client_id,
            'client_secret': self.config.azure_client_secret,
            'scope': self.config.snowflake_scope
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Request token from Azure AD
            response = requests.post(
                self.config.azure_token_endpoint,
                data=token_data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            token_response = response.json()
            
            # Extract token and expiration
            self._access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 3600)  # Default 1 hour
            
            if not self._access_token:
                raise Exception("No access token received from Azure AD")
            
            # Calculate expiration time (with 5 minute buffer)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            self.logger.info(f"Successfully acquired access token, expires at {self._token_expires_at}")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP error during token acquisition: {e}")
            raise Exception(f"Failed to acquire access token: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from Azure AD: {e}")
            raise Exception(f"Invalid response from Azure AD: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during token acquisition: {e}")
            raise
    
    def validate_token(self) -> bool:
        """
        Validate the current access token.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self._access_token:
            return False
        
        if not self._token_expires_at:
            return False
        
        return datetime.now() < self._token_expires_at
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current token.
        
        Returns:
            dict: Token information including expiration status
        """
        return {
            'has_token': bool(self._access_token),
            'is_valid': self.validate_token(),
            'expires_at': self._token_expires_at.isoformat() if self._token_expires_at else None,
            'expires_in_seconds': (self._token_expires_at - datetime.now()).total_seconds() if self._token_expires_at else None
        }
    
    def clear_token(self):
        """Clear the cached access token."""
        self._access_token = None
        self._token_expires_at = None
        self.logger.info("Cleared cached access token")
