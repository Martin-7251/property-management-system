# Property Management System - Database Setup

## Prerequisites

✅ Docker Desktop installed and running  
✅ VS Code installed  
✅ Git installed (optional, for version control)

---

## Quick Start Guide

### 1. **Verify Docker is Running**

Open Docker Desktop and make sure it's running (you'll see the whale icon in your system tray).

In VS Code terminal, verify:
```bash
docker --version
docker-compose --version
```

You should see version numbers for both.

---

### 2. **Project Structure**

Make sure your folder structure looks like this:

```
property-management-system/
├── database/
│   └── 001_initial_schema.sql
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md (this file)
```

---

### 3. **Start the Database**

In VS Code terminal (make sure you're in the project root):

```bash
# Start PostgreSQL and pgAdmin
docker-compose up -d

# Check if containers are running
docker-compose ps
```

You should see:
```
NAME                      STATUS
property_mgmt_db         Up (healthy)
property_mgmt_pgadmin    Up
```

**What just happened?**
- PostgreSQL database is now running on `localhost:5432`
- The migration script automatically ran and created all tables
- pgAdmin is running on `localhost:5050` for database management

---

### 4. **Verify Database Setup**

**Option A: Using Command Line**

```bash
# Connect to database
docker exec -it property_mgmt_db psql -U prop_mgmt_user -d property_management

# Inside psql, run these commands:
\dt                    # List all tables (should show 11 tables)
\d users              # Show users table structure
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';  # Should return 11
\q                    # Quit
```

**Option B: Using pgAdmin (Visual Interface)**

1. Open browser and go to: `http://localhost:5050`
2. Login with:
   - Email: `admin@propertymanager.com`
   - Password: `admin123`
3. Click "Add New Server"
4. In "General" tab:
   - Name: `Property Management DB`
5. In "Connection" tab:
   - Host: `postgres` (container name)
   - Port: `5432`
   - Database: `property_management`
   - Username: `prop_mgmt_user`
   - Password: `SecurePassword123!`
6. Click "Save"
7. Navigate: Servers → Property Management DB → Databases → property_management → Schemas → public → Tables

You should see 11 tables!

---

### 5. **Test the Database**

Let's create a test user to make sure everything works:

```bash
# Connect to database
docker exec -it property_mgmt_db psql -U prop_mgmt_user -d property_management

# Run test queries:
```

```sql
-- Create a test landlord
INSERT INTO users (email, password_hash, full_name, phone, role)
VALUES ('test@test.com', 'test_hash_123', 'Test Landlord', '+254712345678', 'landlord')
RETURNING id, email, full_name;

-- You should see the created user with a UUID

-- Verify it was created
SELECT id, email, full_name, role, created_at FROM users WHERE email = 'test@test.com';

-- Clean up test data
DELETE FROM users WHERE email = 'test@test.com';

-- Exit
\q
```

If all queries worked, **your database is ready!** 🎉

---

## Common Commands

### Start Database
```bash
docker-compose up -d
```

### Stop Database
```bash
docker-compose down
```

### Stop and Remove All Data (CAREFUL!)
```bash
docker-compose down -v
# This will delete ALL data in the database!
```

### View Logs
```bash
# All logs
docker-compose logs

# PostgreSQL logs only
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f postgres
```

### Restart Database
```bash
docker-compose restart postgres
```

### Access Database Shell
```bash
docker exec -it property_mgmt_db psql -U prop_mgmt_user -d property_management
```

### Backup Database
```bash
# Create backup
docker exec property_mgmt_db pg_dump -U prop_mgmt_user property_management > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i property_mgmt_db psql -U prop_mgmt_user -d property_management < backup_20260203.sql
```

---

## Troubleshooting

### ❌ "Port 5432 is already in use"

**Solution:** Another PostgreSQL instance is running. Either:

1. Stop the other PostgreSQL:
```bash
# macOS
brew services stop postgresql

# Linux
sudo systemctl stop postgresql

# Windows - stop PostgreSQL service in Services app
```

2. OR change the port in `.env`:
```
POSTGRES_PORT=5433
```

Then restart: `docker-compose down && docker-compose up -d`

---

### ❌ "docker-compose: command not found"

**Solution:** 

For newer Docker Desktop versions, use:
```bash
docker compose up -d
# (without the hyphen)
```

Or install docker-compose:
```bash
# macOS
brew install docker-compose

# Linux
sudo apt install docker-compose
```

---

### ❌ Containers won't start

**Solution:**

```bash
# Check Docker Desktop is running
# Then try:
docker-compose down
docker-compose up -d

# Check logs for errors:
docker-compose logs postgres
```

---

### ❌ Can't connect to pgAdmin

**Solution:**

1. Make sure container is running: `docker-compose ps`
2. Try: `http://localhost:5050` (not https)
3. Clear browser cache
4. Check `.env` file has correct `PGADMIN_PORT=5050`

---

### ❌ "Database already exists" error

**Solution:**

The migration only runs on first startup. If you need to re-run it:

```bash
# Stop and remove everything
docker-compose down -v

# Start fresh (migration will run automatically)
docker-compose up -d
```

---

## Next Steps

✅ **Database is ready!**

Now you can move to:

1. **Backend Development** (Node.js/Python)
   - Set up API server
   - Connect to database
   - Implement authentication

2. **M-Pesa Integration**
   - Set up Daraja API
   - Create webhook endpoints
   - Test payment flows

3. **Frontend Development**
   - Design landlord dashboard
   - Build property management UI
   - Create tenant views

---

## Database Connection Strings

For your backend application:

**PostgreSQL Connection String:**
```
postgresql://prop_mgmt_user:SecurePassword123!@localhost:5432/property_management
```

**Node.js (pg library):**
```javascript
const { Pool } = require('pg');
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'property_management',
  user: 'prop_mgmt_user',
  password: 'SecurePassword123!'
});
```

**Python (psycopg2):**
```python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="property_management",
    user="prop_mgmt_user",
    password="SecurePassword123!"
)
```

---

## Useful pgAdmin Features

Once connected to pgAdmin:

1. **Query Tool**: Write and execute SQL queries
2. **View Data**: Right-click table → View/Edit Data → All Rows
3. **ER Diagram**: Tools → ERD For Database (visual relationships)
4. **Backup/Restore**: Right-click database → Backup/Restore
5. **Import/Export Data**: Right-click table → Import/Export Data

---

**Database Version**: 1.0  
**Last Updated**: 2026-02-03  

Need help? Check the logs: `docker-compose logs postgres`