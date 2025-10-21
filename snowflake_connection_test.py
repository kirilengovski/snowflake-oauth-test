"""
Snowflake OAuth Connection Test Script

This script demonstrates how to connect to Snowflake using OAuth authentication
with an Azure Service Principal. It includes comprehensive testing and validation.
"""

import logging
import sys
import time
from typing import Optional, Dict, Any
import snowflake.connector
from snowflake.connector import DictCursor

from config import SnowflakeOAuthConfig
from oauth_auth import SnowflakeOAuthAuthenticator


class SnowflakeConnectionTester:
    """Test class for Snowflake OAuth connections."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the connection tester.
        
        Args:
            config_file: Path to .env configuration file
        """
        self.config = SnowflakeOAuthConfig(config_file)
        self.authenticator = SnowflakeOAuthAuthenticator(self.config)
        self.logger = logging.getLogger(__name__)
        self.connection = None
    
    def setup_logging(self, level: str = 'INFO'):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('snowflake_oauth_test.log')
            ]
        )
    
    def validate_configuration(self) -> bool:
        """
        Validate the configuration before attempting connection.
        
        Returns:
            bool: True if configuration is valid
        """
        self.logger.info("Validating configuration...")
        
        if not self.config.validate():
            self.logger.error("Configuration validation failed")
            return False
        
        self.logger.info("Configuration validation passed")
        return True
    
    def test_oauth_authentication(self) -> bool:
        """
        Test OAuth token acquisition.
        
        Returns:
            bool: True if OAuth authentication succeeds
        """
        self.logger.info("Testing OAuth authentication...")
        
        try:
            # Get access token
            token = self.authenticator.get_access_token()
            
            if not token:
                self.logger.error("Failed to acquire access token")
                return False
            
            # Validate token
            token_info = self.authenticator.get_token_info()
            self.logger.info(f"Token info: {token_info}")
            
            if not token_info['is_valid']:
                self.logger.error("Acquired token is not valid")
                return False
            
            self.logger.info("OAuth authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"OAuth authentication failed: {e}")
            return False
    
    def test_snowflake_connection(self) -> bool:
        """
        Test Snowflake connection using OAuth.
        
        Returns:
            bool: True if connection succeeds
        """
        self.logger.info("Testing Snowflake connection...")
        
        try:
            # Get fresh token
            token = self.authenticator.get_access_token()
            
            # Prepare connection parameters
            conn_params = self.config.get_connection_params()
            conn_params.update({
                'authenticator': 'oauth',
                'token': token
            })
            
            # Remove None values
            conn_params = {k: v for k, v in conn_params.items() if v is not None}
            
            self.logger.info(f"Connecting with parameters: {list(conn_params.keys())}")
            
            # Establish connection
            self.connection = snowflake.connector.connect(**conn_params)
            
            if self.connection:
                self.logger.info("Snowflake connection established successfully")
                return True
            else:
                self.logger.error("Failed to establish Snowflake connection")
                return False
                
        except Exception as e:
            self.logger.error(f"Snowflake connection failed: {e}")
            return False
    
    def test_basic_queries(self) -> bool:
        """
        Test basic Snowflake queries.
        
        Returns:
            bool: True if queries execute successfully
        """
        if not self.connection:
            self.logger.error("No active connection to test queries")
            return False
        
        self.logger.info("Testing basic queries...")
        
        test_queries = [
            ("SELECT CURRENT_VERSION()", "Snowflake version"),
            ("SELECT CURRENT_ACCOUNT()", "Current account"),
            ("SELECT CURRENT_WAREHOUSE()", "Current warehouse"),
            ("SELECT CURRENT_DATABASE()", "Current database"),
            ("SELECT CURRENT_SCHEMA()", "Current schema"),
            ("SELECT CURRENT_ROLE()", "Current role"),
            ("SELECT CURRENT_USER()", "Current user"),
            ("SELECT CURRENT_TIMESTAMP()", "Current timestamp")
        ]
        
        try:
            cursor = self.connection.cursor(DictCursor)
            
            for query, description in test_queries:
                self.logger.info(f"Executing: {description}")
                cursor.execute(query)
                result = cursor.fetchone()
                self.logger.info(f"Result: {result}")
            
            cursor.close()
            self.logger.info("All basic queries executed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return False
    
    def test_permissions(self) -> bool:
        """
        Test basic permissions and access.
        
        Returns:
            bool: True if permissions are adequate
        """
        if not self.connection:
            self.logger.error("No active connection to test permissions")
            return False
        
        self.logger.info("Testing permissions...")
        
        permission_queries = [
            ("SHOW GRANTS", "Show grants"),
            ("SHOW ROLES", "Show roles"),
            ("SHOW WAREHOUSES", "Show warehouses"),
            ("SHOW DATABASES", "Show databases")
        ]
        
        try:
            cursor = self.connection.cursor(DictCursor)
            
            for query, description in permission_queries:
                self.logger.info(f"Testing: {description}")
                cursor.execute(query)
                results = cursor.fetchall()
                self.logger.info(f"Found {len(results)} results")
            
            cursor.close()
            self.logger.info("Permission tests completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Permission test failed: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, bool]:
        """
        Run comprehensive connection and functionality tests.
        
        Returns:
            dict: Test results for each component
        """
        self.logger.info("Starting comprehensive Snowflake OAuth test...")
        
        results = {
            'configuration': False,
            'oauth_auth': False,
            'snowflake_connection': False,
            'basic_queries': False,
            'permissions': False
        }
        
        # Test configuration
        results['configuration'] = self.validate_configuration()
        if not results['configuration']:
            self.logger.error("Configuration test failed, stopping tests")
            return results
        
        # Test OAuth authentication
        results['oauth_auth'] = self.test_oauth_authentication()
        if not results['oauth_auth']:
            self.logger.error("OAuth authentication test failed, stopping tests")
            return results
        
        # Test Snowflake connection
        results['snowflake_connection'] = self.test_snowflake_connection()
        if not results['snowflake_connection']:
            self.logger.error("Snowflake connection test failed, stopping tests")
            return results
        
        # Test basic queries
        results['basic_queries'] = self.test_basic_queries()
        
        # Test permissions
        results['permissions'] = self.test_permissions()
        
        # Summary
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        self.logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed")
        
        for test_name, result in results.items():
            status = "PASSED" if result else "FAILED"
            self.logger.info(f"  {test_name}: {status}")
        
        return results
    
    def cleanup(self):
        """Clean up connections and resources."""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Snowflake connection closed")
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
        
        self.authenticator.clear_token()


def main():
    """Main function to run the Snowflake OAuth connection test."""
    tester = SnowflakeConnectionTester()
    tester.setup_logging('INFO')
    
    try:
        results = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        tester.logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        tester.logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
