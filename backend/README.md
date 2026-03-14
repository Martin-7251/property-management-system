# Property Management Backend API

FastAPI-based backend for property management system with M-Pesa integration.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration & environment variables
│   ├── database.py             # Database connection
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── unit.py
│   │   ├── tenant.py
│   │   ├── invoice.py
│   │   └── payment.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response models)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── tenant.py
│   │   └── invoice.py
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencies (auth, db session)
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── properties.py     # Property management endpoints
│   │   ├── units.py          # Unit management endpoints
│   │   ├── tenants.py        # Tenant management endpoints
│   │   ├── invoices.py       # Invoice management endpoints
│   │   ├── payments.py       # Payment endpoints
│   │   └── mpesa.py          # M-Pesa webhook endpoints
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── invoice_service.py
│   │   ├── payment_service.py
│   │   ├── mpesa_service.py
│   │   └── notification_service.py
│   │
│   └── utils/                 # Helper functions
│       ├── __init__.py
│       ├── security.py       # Password hashing, JWT tokens
│       ├── email.py          # Email sending
│       └── sms.py            # SMS sending (Africa's Talking)
│
├── alembic/                   # Database migrations (optional)
│   └── versions/
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not committed)
├── .env.example              # Example environment file
└── README.md                 # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites

- ✅ Python 3.9+ installed
- ✅ PostgreSQL database running (Docker)
- ✅ VS Code or any code editor

---

### Step 1: Set Up Python Virtual Environment

**What is a virtual environment?**
A virtual environment is an isolated Python environment for this project. It keeps dependencies separate from your system Python.

**Create virtual environment:**

```bash
# Navigate to backend folder
cd backend

# Create virtual environment (Mac/Linux)
python3 -m venv venv

# Or Windows
python -m venv venv
```

**Activate virtual environment:**

```bash
# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 2: Install Dependencies

**Install all required Python packages:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL driver
- `pydantic` - Data validation
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `python-multipart` - File uploads
- `requests` - HTTP client (for M-Pesa)
- `python-dotenv` - Environment variables
- And more...

---

### Step 3: Configure Environment Variables

**Copy the example file:**

```bash
cp .env.example .env
```

**Edit `.env` file with your settings:**

```bash
# Open in VS Code
code .env

# Or any editor
nano .env
```

**Important:** Update these values:
- Database credentials
- JWT secret key
- M-Pesa credentials (from Daraja)
- SMS API key (Africa's Talking)

---

### Step 4: Test Database Connection

```bash
# Make sure your PostgreSQL is running
docker-compose ps

# Should show property_mgmt_db as Up
```

---

### Step 5: Run the API Server

```bash
# From backend folder with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**What this does:**
- `uvicorn` - ASGI server
- `app.main:app` - Run the FastAPI app
- `--reload` - Auto-restart on code changes
- `--host 0.0.0.0` - Accept connections from anywhere
- `--port 8000` - Run on port 8000

**Success!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### Step 6: Test the API

**Open your browser:**
- API Docs: http://localhost:8000/docs (interactive)
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Interactive API Documentation:**
FastAPI automatically generates beautiful, interactive API docs where you can test endpoints!

---

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new landlord
- `POST /api/auth/login` - Login (get JWT token)
- `GET /api/auth/me` - Get current user

### Properties
- `GET /api/properties` - List all properties
- `POST /api/properties` - Create property
- `GET /api/properties/{id}` - Get property details
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property

### Units
- `GET /api/units` - List units
- `POST /api/units` - Create unit
- `GET /api/units/{id}` - Get unit details
- `PUT /api/units/{id}` - Update unit

### Tenants
- `GET /api/tenants` - List tenants
- `POST /api/tenants` - Add tenant (auto-creates invoices)
- `GET /api/tenants/{id}` - Get tenant details
- `PUT /api/tenants/{id}` - Update tenant
- `POST /api/tenants/{id}/move-out` - Process move-out

### Invoices
- `GET /api/invoices` - List invoices
- `GET /api/invoices/{id}` - Get invoice details
- `PUT /api/invoices/{id}` - Update invoice (adjust amount)
- `GET /api/invoices/unpaid` - Get unpaid invoices

### Payments
- `GET /api/payments` - List payments
- `GET /api/payments/unmatched` - Get unmatched payments
- `POST /api/payments/{id}/match` - Manually match payment

### M-Pesa Webhooks
- `POST /api/mpesa/validation` - M-Pesa validation callback
- `POST /api/mpesa/confirmation` - M-Pesa confirmation callback
- `GET /api/mpesa/status/{trans_id}` - Check transaction status

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication.

**How it works:**

1. **Register or Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }'
```

2. **Receive token:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Use token in requests:**
```bash
curl -X GET "http://localhost:8000/api/properties" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**In the interactive docs (http://localhost:8000/docs):**
1. Click "Authorize" button
2. Enter: `Bearer YOUR_TOKEN`
3. Click "Authorize"
4. Now all requests will include the token!

---

## 🧪 Testing the API

### Using Interactive Docs (Easiest!)

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See the response!

### Using curl (Command Line)

```bash
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "phone": "+254712345678"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Using Python requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
properties = requests.get(
    "http://localhost:8000/api/properties",
    headers=headers
)
print(properties.json())
```

---

## 🔄 Development Workflow

### Making Changes

1. **Edit code** in VS Code
2. **Save file** (Ctrl+S)
3. **Server auto-reloads** (because of `--reload` flag)
4. **Test in browser** (http://localhost:8000/docs)

### Common Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run server
uvicorn app.main:app --reload

# Install new package
pip install package-name
pip freeze > requirements.txt  # Update requirements

# Deactivate virtual environment
deactivate
```

---

## 📝 Environment Variables Explained

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database
# Format: postgresql://username:password@host:port/database_name

# Security
SECRET_KEY=your-secret-key-min-32-chars
# Generate with: openssl rand -hex 32

# M-Pesa (Get from https://developer.safaricom.co.ke)
MPESA_ENVIRONMENT=sandbox  # or production
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_PASSKEY=your_passkey
MPESA_SHORTCODE=174379  # Your paybill/till

# SMS (Get from https://africastalking.com)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_key

# Email (Get from https://sendgrid.com)
SENDGRID_API_KEY=your_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Solution: Activate virtual environment
source venv/bin/activate
```

### "Connection refused" to database
```bash
# Solution: Make sure PostgreSQL is running
docker-compose ps
docker-compose up -d
```

### "Address already in use"
```bash
# Solution: Port 8000 is taken, use different port
uvicorn app.main:app --reload --port 8001
```

### "ImportError: cannot import name 'app'"
```bash
# Solution: Make sure you're in the backend folder
cd backend
# And all __init__.py files exist
```

---

## 📖 Learning Resources

### FastAPI
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### SQLAlchemy
- Docs: https://docs.sqlalchemy.org/

### Python
- Python.org: https://www.python.org/
- Real Python: https://realpython.com/

---

## 🚀 Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Configure .env file
4. ✅ Run the server
5. ✅ Test endpoints in http://localhost:8000/docs
6. ⏭️ Integrate M-Pesa
7. ⏭️ Set up cron jobs
8. ⏭️ Deploy to production

---

## 📞 Need Help?

If you get stuck:
1. Check the error message carefully
2. Make sure virtual environment is activated
3. Verify database is running
4. Check .env file has correct values
5. Look at server logs in terminal

---

**Ready to start? Follow the Quick Start Guide above!** 🎉
