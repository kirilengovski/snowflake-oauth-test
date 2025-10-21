# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit with your values
nano .env
```

### 3. Set Up Snowflake (One-time)
Run the SQL commands in `snowflake_setup.sql` in your Snowflake account.

### 4. Test Connection
```bash
# Simple test
python simple_test.py

# Comprehensive test
python snowflake_connection_test.py
```

## 📝 Required Configuration

Update your `.env` file with these values:

```env
# From Azure App Registration
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# From Snowflake Account
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_WAREHOUSE=your-warehouse
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=your-schema
```

## ✅ Success Indicators

You'll know it's working when you see:
- ✓ OAuth token acquired successfully
- ✓ Connected to Snowflake successfully
- ✓ Query executed successfully

## 🆘 Need Help?

Check the full [README.md](README.md) for detailed setup instructions and troubleshooting.
