# Getting Started with Copper CRM Scripts

This guide walks you through setting up and using the Copper CRM API scripts.

## 1. Prerequisites

- Python 3.8 or higher
- Your Copper CRM API key
- Your Copper CRM account email

## 2. Setup

### Step 1: Get Your API Credentials

1. Log into your Copper CRM account
2. Go to **Settings** → **Integrations** → **API**
3. Copy your API key (you may need to generate one if you don't have it)
4. Note your account email address

### Step 2: Create .env File

Copy the example configuration and fill in your credentials:

```bash
cd $HOME/.claude/skills/copper-crm
cp templates/.env.example .env
```

Edit `.env` and add your credentials:

```env
COPPER_API_KEY=your_actual_api_key_here
COPPER_USER_EMAIL=your.email@company.com
COPPER_BASE_URL=https://api.copper.com/developer_api/v1
```

### Step 3: Install Dependencies

```bash
# Using pip
pip install -r scripts/requirements.txt

# Or using uv
uv add -r scripts/requirements.txt
```

## 3. Test Your Connection

Before running bulk imports, test your API connection:

```bash
cd scripts
python test_connection.py
```

Expected output on success:
```
Testing Copper CRM API Connection...
--------------------------------------------------
✓ Credentials loaded
✓ Authentication successful
✓ Account: Your Company Name (ID: 123456)
✓ User: your.email@company.com (Admin permissions)
✓ Rate limit test: 5/5 requests successful
==================================================
CONNECTION TEST SUMMARY
==================================================
✓ Connection ready!
```

## 4. Next Steps

### If Connection Test Passed:
You're ready to use the bulk import scripts:

```bash
python bulk_import.py leads example_leads.csv
```

### If Connection Test Failed:
Review the error messages and check:
1. API key is correct (try regenerating in Copper CRM settings)
2. Email address matches your account
3. Your Copper CRM account is active
4. Network connectivity is working

## 5. Common Tasks

### Import Leads
```bash
python bulk_import.py leads your_leads.csv --mode upsert
```

### Import Contacts
```bash
python bulk_import.py people contacts.csv --mode create
```

### Import Companies
```bash
python bulk_import.py companies companies.csv
```

### Import Opportunities/Deals
```bash
python bulk_import.py opportunities deals.csv --mode upsert
```

## 6. Troubleshooting

### Missing .env File
- Create `.env` in the copper-crm directory
- Add `COPPER_API_KEY` and `COPPER_USER_EMAIL`

### API Key Issues
- Verify key in Copper CRM: Settings → Integrations → API
- Make sure key hasn't expired
- Consider regenerating if unsure

### Timeout Errors
- Check internet connection
- Verify Copper CRM API is accessible
- Try again after a short delay

### Rate Limiting (HTTP 429)
- The scripts automatically handle rate limiting
- If you see this error frequently, contact Copper CRM support

## 7. Documentation

For more details on each script:
- `test_connection.py` - See README.md section on test_connection.py
- `bulk_import.py` - See README.md section on bulk_import.py
- `validate_config.py` - See README.md section on validate_config.py

## 8. Support

If you encounter issues:
1. Run `python test_connection.py` to verify connectivity
2. Check the error messages for specific guidance
3. Review the script README.md for detailed documentation
4. Verify your API key and email are correct
