# SaaS Product Usage Data Assistant

🚀 **AI-powered backend that converts natural language questions to SQL queries for product usage data.**

Transform questions like "How many users do we have?" into SQL queries and get natural language responses with data insights.

## ✨ Features

- **Natural Language to SQL**: Convert questions to SQL using OpenAI GPT
- **Tenant Isolation**: Secure multi-tenant data access
- **Complete Flow**: Question → SQL → Data → Natural Language Response
- **RESTful API**: Easy integration with FastAPI

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### 1. Setup
```bash
git clone <your-repo-url>
cd telemetrix
cd api_server
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` file in `api_server` directory:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Test & Start
```bash
# Test setup
python setup_and_test.py

# Start server
python -m api_server.main
```

Server starts at: http://localhost:8000

### 4. Test API
```bash
python test_complete_flow.py
```

## 📡 API Usage

### Endpoint
```http
POST /api/v1/query
Content-Type: application/json

{
    "question": "How many users do we have?",
    "tenant_id": "tenant_123"
}
```

### Example Response
```json
{
    "success": true,
    "question": "How many users do we have?",
    "sql_query": "SELECT COUNT(*) AS total_users FROM users WHERE tenant_id = 'tenant_123';",
    "natural_language_response": "You have 1250 users in your system.",
    "data": [{"total_users": 1250}],
    "row_count": 1
}
```

## 🏗️ Project Structure
```
telemetrix/
├── api_server/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings & environment
│   ├── models.py               # API models & schemas
│   ├── requirements.txt        # Python dependencies
│   ├── setup_and_test.py       # Setup & testing script
│   ├── test_complete_flow.py   # Integration tests
│   └── services/
│       ├── nlq_service.py      # Natural Language → SQL
│       └── complete_service.py # End-to-end flow orchestration
├── sqlexecutor/
│   ├── db_config.py            # Database configuration
│   └── db_service.py           # Database operations
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |

## 🐛 Troubleshooting

**❌ "Connection error" or "Failed to generate SQL"**
- Check your `OPENAI_API_KEY` in `.env` file
- Verify the API key is valid and has credits

**❌ "Module not found" errors**
- Make sure you're running from the project root
- Use `python -m api_server.main` instead of `python main.py`

## 🔒 Security

- **Tenant Isolation**: All queries include `tenant_id` filtering
- **SQL Injection Protection**: Generated SQL is validated for safety
- **Environment Variables**: Sensitive data stored in `.env` (gitignored)
- **Read-Only Queries**: Only SELECT statements are allowed

---

**Happy querying! 🎉** 