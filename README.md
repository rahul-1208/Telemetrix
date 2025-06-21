# SaaS Product Usage Data Assistant

AI-powered backend that converts natural language questions to SQL queries for product usage data.

## Quick Start

### 1. Setup
```bash
cd api_server
pip install -r requirements.txt
pip install pydantic-settings
```

### 2. Add API Key
Create `.env` file in `api_server` directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test API
```bash
python test_api.py
```

Or visit: http://localhost:8000/docs

## What It Does

- Takes questions like "How many users signed up last month?"
- Converts to SQL using OpenAI
- Returns generated SQL with explanation
- Includes tenant isolation for security

## API Endpoint

```
POST /api/v1/query
{
    "question": "How many users signed up last month?",
    "tenant_id": "tenant_123"
}
```

## Project Structure
```
api_server/
├── main.py              # FastAPI app
├── config.py            # Settings
├── models.py            # API models
├── services/
│   └── nlq_service.py   # NLQ to SQL conversion
└── test_api.py          # Test script
```

## Troubleshooting

- **Import Error**: `pip install pydantic-settings`
- **Server won't start**: Make sure you're in `api_server` directory
- **API Key Error**: Check your `.env` file has `OPENAI_API_KEY=your_key`
- **PowerShell curl issues**: Use `Invoke-RestMethod` or the test script

## Next Steps
1. Connect to PostgreSQL database
2. Execute generated SQL
3. Add result summarization 