#!/usr/bin/env python3
"""
Simple Snowflake OAuth Connection Test

A minimal example showing how to use the OAuth authentication
to connect to Snowflake and execute a basic query.
"""

import logging
from config import SnowflakeOAuthConfig
from oauth_auth import SnowflakeOAuthAuthenticator
import snowflake.connector

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def simple_connection_test():
    """Simple test to connect to Snowflake using OAuth."""
    
    # Load configuration
    config = SnowflakeOAuthConfig()
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed. Please check your .env file.")
        return False
    
    # Initialize OAuth authenticator
    authenticator = SnowflakeOAuthAuthenticator(config)
    
    try:
        # Get access token
        logger.info("Getting OAuth access token...")
        token = authenticator.get_access_token()
        logger.info("✓ OAuth token acquired successfully")
        
        # Prepare connection parameters
        conn_params = config.get_connection_params()
        conn_params.update({
            'authenticator': 'oauth',
            'token': token
        })
        
        # Remove None values
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        # Connect to Snowflake
        logger.info("Connecting to Snowflake...")
        conn = snowflake.connector.connect(**conn_params)
        logger.info("✓ Connected to Snowflake successfully")
        
        # Execute a simple query
        logger.info("Executing test query...")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_ROLE()")
        result = cursor.fetchone()
        
        logger.info("✓ Query executed successfully")
        logger.info(f"Snowflake Version: {result[0]}")
        logger.info(f"Current User: {result[1]}")
        logger.info(f"Current Role: {result[2]}")
        
        # Clean up
        cursor.close()
        conn.close()
        logger.info("✓ Connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Snowflake OAuth Simple Connection Test")
    print("=" * 60)
    
    success = simple_connection_test()
    
    print("=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("Your OAuth authentication is working correctly.")
    else:
        print("❌ Test failed!")
        print("Please check your configuration and try again.")
    print("=" * 60)
