"""
Configuration management for Snowflake OAuth authentication.
Handles loading configuration from environment variables and .env files.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class SnowflakeOAuthConfig:
    """Configuration class for Snowflake OAuth authentication."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    @property
    def azure_client_id(self) -> str:
        """Azure Application (client) ID."""
        return os.getenv('AZURE_CLIENT_ID', '')
    
    @property
    def azure_client_secret(self) -> str:
        """Azure client secret."""
        return os.getenv('AZURE_CLIENT_SECRET', '')
    
    @property
    def azure_tenant_id(self) -> str:
        """Azure Directory (tenant) ID."""
        return os.getenv('AZURE_TENANT_ID', '')
    
    @property
    def snowflake_account(self) -> str:
        """Snowflake account identifier."""
        return os.getenv('SNOWFLAKE_ACCOUNT', '')
    
    @property
    def snowflake_warehouse(self) -> str:
        """Snowflake warehouse name."""
        return os.getenv('SNOWFLAKE_WAREHOUSE', '')
    
    @property
    def snowflake_database(self) -> str:
        """Snowflake database name."""
        return os.getenv('SNOWFLAKE_DATABASE', '')
    
    @property
    def snowflake_schema(self) -> str:
        """Snowflake schema name."""
        return os.getenv('SNOWFLAKE_SCHEMA', '')
    
    @property
    def snowflake_role(self) -> str:
        """Snowflake role name."""
        return os.getenv('SNOWFLAKE_ROLE', '')
    
    @property
    def azure_token_endpoint(self) -> str:
        """Azure OAuth token endpoint."""
        return f"https://login.microsoftonline.com/{self.azure_tenant_id}/oauth2/v2.0/token"
    
    @property
    def snowflake_scope(self) -> str:
        """Snowflake OAuth scope."""
        return f"https://{self.snowflake_account}.snowflakecomputing.com/.default"
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if all required config is present, False otherwise
        """
        required_fields = [
            'azure_client_id',
            'azure_client_secret', 
            'azure_tenant_id',
            'snowflake_account',
            'snowflake_warehouse',
            'snowflake_database',
            'snowflake_schema'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field.upper())
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def get_connection_params(self) -> dict:
        """
        Get connection parameters for Snowflake connector.
        
        Returns:
            dict: Connection parameters
        """
        return {
            'account': self.snowflake_account,
            'warehouse': self.snowflake_warehouse,
            'database': self.snowflake_database,
            'schema': self.snowflake_schema,
            'role': self.snowflake_role if self.snowflake_role else None
        }
