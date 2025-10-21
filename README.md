# Snowflake OAuth Authentication Test Project

This project demonstrates how to securely connect to Snowflake using OAuth authentication with an Azure Service Principal. This is the recommended approach for service accounts as Snowflake has moved away from password-based authentication for enhanced security.

## 🏗️ Architecture Overview

The solution implements a secure OAuth flow where:
1. **Azure Service Principal** authenticates with Azure AD
2. **Azure AD** issues an OAuth token
3. **Snowflake** validates the token and grants access
4. **Python Application** uses the token to connect to Snowflake

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Snowflake OAuth Authentication Flow                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │    │                 │
│   Python App    │    │  Azure Service  │    │   Azure AD      │    │   Snowflake     │
│                 │    │   Principal     │    │                 │    │                 │
│                 │    │                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │                      │
          │                      │                      │                      │
          │  1. Request Token    │                      │                      │
          │─────────────────────▶│                      │                      │
          │                      │                      │                      │
          │                      │  2. Client Credentials Grant                │
          │                      │─────────────────────▶│                      │
          │                      │                      │                      │
          │                      │                      │  3. Validate Credentials │
          │                      │                      │◀─────────────────────│
          │                      │                      │                      │
          │                      │  4. Access Token     │                      │
          │                      │◀─────────────────────│                      │
          │                      │                      │                      │
          │  5. Access Token     │                      │                      │
          │◀─────────────────────│                      │                      │
          │                      │                      │                      │
          │  6. Connect to Snowflake with Token         │                      │
          │─────────────────────────────────────────────▶│                      │
          │                      │                      │                      │
          │                      │                      │  7. Validate Token   │
          │                      │                      │◀─────────────────────│
          │                      │                      │                      │
          │  8. Connection Established                   │                      │
          │◀─────────────────────────────────────────────│                      │
          │                      │                      │                      │
          │  9. Execute Queries  │                      │                      │
          │─────────────────────────────────────────────▶│                      │
          │                      │                      │                      │
          │  10. Query Results   │                      │                      │
          │◀─────────────────────────────────────────────│                      │
          │                      │                      │                      │
```

### Component Details

| Component | Role | Key Responsibilities |
|-----------|------|---------------------|
| **Python App** | Client Application | • Request OAuth tokens<br>• Connect to Snowflake<br>• Execute queries<br>• Handle token refresh |
| **Azure Service Principal** | Service Identity | • Authenticate with Azure AD<br>• Request access tokens<br>• Represent application identity |
| **Azure AD** | Identity Provider | • Validate service principal credentials<br>• Issue OAuth access tokens<br>• Manage token lifecycle |
| **Snowflake** | Data Platform | • Validate OAuth tokens<br>• Grant access to resources<br>• Execute queries and return results |

### Security Flow

1. **Token Request**: Python app requests token using client credentials
2. **Authentication**: Azure AD validates service principal credentials
3. **Token Issuance**: Azure AD issues time-limited access token
4. **Connection**: Python app connects to Snowflake using OAuth token
5. **Validation**: Snowflake validates token with Azure AD
6. **Access**: Snowflake grants access based on configured permissions
7. **Operations**: Python app can execute authorized operations

## 📋 Prerequisites

- Python 3.8 or higher
- Access to Azure Active Directory with permissions to create app registrations
- Snowflake account with appropriate privileges to create security integrations
- Network access to both Azure AD and Snowflake endpoints

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone or download this project
cd snowflake-oauth-test

# Install dependencies
pip install -r requirements.txt
```

### 2. Azure AD Configuration

#### Step 2.1: Create App Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: `Snowflake Service Principal`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank
5. Click **Register**

#### Step 2.2: Create Client Secret
1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description and select expiration period
4. Click **Add**
5. **Important**: Copy the secret value immediately (it won't be shown again)

#### Step 2.3: Note Required Values
From your app registration, collect:
- **Application (client) ID**
- **Directory (tenant) ID**
- **Client secret** (from step 2.2)

### 3. Snowflake Configuration

#### Step 3.1: Create Security Integration
Run the SQL commands in `snowflake_setup.sql` in your Snowflake account. Update the placeholders with your actual values:

```sql
CREATE OR REPLACE SECURITY INTEGRATION external_oauth_integration
  TYPE = EXTERNAL_OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT_ID = 'your-azure-client-id-here'
  OAUTH_CLIENT_SECRET = 'your-azure-client-secret-here'
  OAUTH_TOKEN_ENDPOINT = 'https://login.microsoftonline.com/your-tenant-id-here/oauth2/v2.0/token'
  -- ... (see snowflake_setup.sql for complete configuration)
```

#### Step 3.2: Create Service Principal User
```sql
CREATE OR REPLACE USER "your-service-principal-name@your-tenant-domain.com"
  LOGIN_NAME = 'your-service-principal-name@your-tenant-domain.com'
  DEFAULT_ROLE = 'oauth_service_role'
  DEFAULT_WAREHOUSE = 'your-warehouse-name'
  -- ... (see snowflake_setup.sql for complete configuration)
```

### 4. Configuration Setup

#### Step 4.1: Create Environment File
```bash
# Copy the example configuration
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

#### Step 4.2: Update Configuration Values
```env
# Azure AD Configuration
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your-secret-value-here
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account-identifier
SNOWFLAKE_WAREHOUSE=your-warehouse-name
SNOWFLAKE_DATABASE=your-database-name
SNOWFLAKE_SCHEMA=your-schema-name
SNOWFLAKE_ROLE=oauth_service_role
```

### 5. Run the Test

```bash
# Run the comprehensive connection test
python snowflake_connection_test.py
```

## 📁 Project Structure

```
snowflake-oauth-test/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                      # Example configuration file
├── snowflake_setup.sql               # Snowflake setup SQL commands
├── config.py                         # Configuration management
├── oauth_auth.py                     # OAuth authentication logic
├── snowflake_connection_test.py      # Main test script
└── snowflake_oauth_test.log          # Generated log file
```

## 🔧 Components Explained

### Configuration Management (`config.py`)
- Loads configuration from environment variables
- Validates required configuration parameters
- Provides connection parameters for Snowflake connector

### OAuth Authentication (`oauth_auth.py`)
- Handles Azure AD token acquisition
- Manages token caching and refresh
- Validates token expiration

### Connection Testing (`snowflake_connection_test.py`)
- Comprehensive test suite for OAuth authentication
- Tests configuration, OAuth flow, Snowflake connection, and permissions
- Provides detailed logging and error reporting

## 🧪 Test Coverage

The test script validates:

1. **Configuration Validation**: Ensures all required parameters are present
2. **OAuth Authentication**: Tests Azure AD token acquisition
3. **Snowflake Connection**: Establishes connection using OAuth token
4. **Basic Queries**: Executes standard Snowflake queries
5. **Permissions**: Tests access to databases, schemas, and objects

## 📊 Expected Output

When successful, you should see output like:

```
2024-01-15 10:30:00 - __main__ - INFO - Starting comprehensive Snowflake OAuth test...
2024-01-15 10:30:01 - __main__ - INFO - Configuration validation passed
2024-01-15 10:30:02 - __main__ - INFO - OAuth authentication successful
2024-01-15 10:30:03 - __main__ - INFO - Snowflake connection established successfully
2024-01-15 10:30:04 - __main__ - INFO - All basic queries executed successfully
2024-01-15 10:30:05 - __main__ - INFO - Permission tests completed successfully
2024-01-15 10:30:05 - __main__ - INFO - Test Summary: 5/5 tests passed
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` files to version control
2. **Client Secrets**: Rotate Azure client secrets regularly
3. **Least Privilege**: Grant only necessary permissions to the service principal
4. **Network Security**: Ensure proper firewall rules for Azure AD and Snowflake endpoints
5. **Token Management**: Tokens are automatically cached and refreshed

## 🐛 Troubleshooting

### Common Issues

#### 1. Configuration Validation Failed
- Ensure all required environment variables are set
- Check that `.env` file exists and is properly formatted
- Verify no extra spaces or quotes in configuration values

#### 2. OAuth Authentication Failed
- Verify Azure client ID, secret, and tenant ID are correct
- Check that the Azure app registration is properly configured
- Ensure the client secret hasn't expired

#### 3. Snowflake Connection Failed
- Verify the security integration is created and enabled
- Check that the service principal user exists in Snowflake
- Ensure the user has the correct role and permissions

#### 4. Permission Denied Errors
- Verify the service principal role has necessary grants
- Check warehouse, database, and schema permissions
- Ensure the user is assigned to the correct role

### Debug Mode

Enable debug logging for more detailed information:

```python
tester.setup_logging('DEBUG')
```

## 📚 Additional Resources

- [Snowflake OAuth Documentation](https://docs.snowflake.com/en/user-guide/oauth.html)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector.html)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is provided as-is for educational and testing purposes.
