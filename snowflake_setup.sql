-- Snowflake OAuth Security Integration Setup
-- Run these commands in your Snowflake account to set up OAuth authentication

-- Step 1: Create the security integration for external OAuth
-- Replace the placeholders with your actual Azure AD values
CREATE OR REPLACE SECURITY INTEGRATION external_oauth_integration
  TYPE = EXTERNAL_OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT_ID = 'your-azure-client-id-here'
  OAUTH_CLIENT_SECRET = 'your-azure-client-secret-here'
  OAUTH_TOKEN_ENDPOINT = 'https://login.microsoftonline.com/your-tenant-id-here/oauth2/v2.0/token'
  OAUTH_AUTHORIZATION_ENDPOINT = 'https://login.microsoftonline.com/your-tenant-id-here/oauth2/v2.0/authorize'
  OAUTH_ISSUER = 'https://login.microsoftonline.com/your-tenant-id-here/v2.0'
  OAUTH_SCOPE_MAPPING_ATTRIBUTE = 'upn'
  OAUTH_JWS_KEYS_URL = 'https://login.microsoftonline.com/your-tenant-id-here/discovery/v2.0/keys'
  OAUTH_RSA_PUBLIC_KEY = ''
  OAUTH_RSA_PUBLIC_KEY_2 = ''
  OAUTH_BLOCKED_ROLES_LIST = ()
  OAUTH_ALLOWED_ROLES_LIST = ()
  OAUTH_AUDIENCE_LIST = ('https://your-account-identifier.snowflakecomputing.com')
  OAUTH_ANY_ROLE_MODE = 'ENABLE'
  COMMENT = 'OAuth integration with Azure AD for service principal authentication';

-- Step 2: Create a role for the service principal (optional but recommended)
CREATE OR REPLACE ROLE oauth_service_role
  COMMENT = 'Role for OAuth service principal access';

-- Step 3: Grant necessary privileges to the role
-- Adjust these grants based on your specific requirements

-- Grant usage on warehouse
GRANT USAGE ON WAREHOUSE your-warehouse-name TO ROLE oauth_service_role;

-- Grant usage on database and schema
GRANT USAGE ON DATABASE your-database-name TO ROLE oauth_service_role;
GRANT USAGE ON SCHEMA your-database-name.your-schema-name TO ROLE oauth_service_role;

-- Grant select on tables (adjust as needed)
GRANT SELECT ON ALL TABLES IN SCHEMA your-database-name.your-schema-name TO ROLE oauth_service_role;
GRANT SELECT ON FUTURE TABLES IN SCHEMA your-database-name.your-schema-name TO ROLE oauth_service_role;

-- Grant select on views (adjust as needed)
GRANT SELECT ON ALL VIEWS IN SCHEMA your-database-name.your-schema-name TO ROLE oauth_service_role;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA your-database-name.your-schema-name TO ROLE oauth_service_role;

-- Step 4: Create a user for the service principal
-- The username should match the Azure AD service principal name
CREATE OR REPLACE USER "your-service-principal-name@your-tenant-domain.com"
  LOGIN_NAME = 'your-service-principal-name@your-tenant-domain.com'
  DISPLAY_NAME = 'Azure Service Principal'
  FIRST_NAME = 'Service'
  LAST_NAME = 'Principal'
  EMAIL = 'your-service-principal-name@your-tenant-domain.com'
  DEFAULT_ROLE = 'oauth_service_role'
  DEFAULT_WAREHOUSE = 'your-warehouse-name'
  DEFAULT_NAMESPACE = 'your-database-name.your-schema-name'
  COMMENT = 'Azure AD Service Principal user for OAuth authentication';

-- Step 5: Grant the role to the user
GRANT ROLE oauth_service_role TO USER "your-service-principal-name@your-tenant-domain.com";

-- Step 6: Verify the setup
-- Check the security integration
SHOW SECURITY INTEGRATIONS;

-- Check the user
SHOW USERS LIKE '%your-service-principal-name%';

-- Check role grants
SHOW GRANTS TO ROLE oauth_service_role;

-- Test query (run this after setting up your Python script)
-- SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
