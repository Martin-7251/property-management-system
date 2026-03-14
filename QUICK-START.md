# 🚀 Quick Start Checklist

Follow these steps to get your database running in VS Code with Docker Desktop:

## ✅ Step-by-Step Setup

### 1. **Check Prerequisites**
- [ ] Docker Desktop is installed and running (check system tray for whale icon)
- [ ] VS Code is installed
- [ ] Open VS Code

---

### 2. **Create Project Folder**
- [ ] Open VS Code
- [ ] Create new folder: `property-management-system`
- [ ] Open this folder in VS Code (File → Open Folder)
- [ ] Open Terminal in VS Code (View → Terminal or Ctrl+`)

---

### 3. **Download Files**
- [ ] Download all the files I provided
- [ ] Place them in your project folder like this:

```
property-management-system/
├── database/
│   └── 001_initial_schema.sql    ← Put the SQL file here
├── docker-compose.yml            ← Root level
├── .env                          ← Root level
├── .gitignore                    ← Root level
├── README-DATABASE.md            ← Root level
├── db.sh                         ← Root level (Mac/Linux)
└── db.bat                        ← Root level (Windows)
```

---

### 4. **Make Helper Script Executable** (Mac/Linux only)
In VS Code terminal:
```bash
chmod +x db.sh
```

(Windows users: skip this step, use `db.bat` instead)

---

### 5. **Start Database**

**Option A: Using Helper Script (Recommended)**

**Mac/Linux:**
```bash
./db.sh start
```

**Windows:**
```
db.bat
# Then choose option 1
```

**Option B: Direct Docker Command**
```bash
docker-compose up -d
```

---

### 6. **Verify Setup**

Wait 10-20 seconds, then check status:

**Using helper script:**
```bash
./db.sh status        # Mac/Linux
db.bat                # Windows → option 4
```

**Or direct command:**
```bash
docker-compose ps
```

You should see:
```
NAME                      STATUS
property_mgmt_db         Up (healthy)
property_mgmt_pgadmin    Up
```

---

### 7. **Access Database**

**Option A: pgAdmin (Visual Interface)**
- [ ] Open browser: http://localhost:5050
- [ ] Login: `admin@propertymanager.com` / `admin123`
- [ ] Add Server:
  - Name: `Property Management DB`
  - Host: `postgres`
  - Port: `5432`
  - Database: `property_management`
  - Username: `prop_mgmt_user`
  - Password: `SecurePassword123!`
- [ ] Navigate to Tables and verify 11 tables exist

**Option B: Command Line**
```bash
./db.sh connect       # Mac/Linux
db.bat                # Windows → option 6
```

Then run:
```sql
\dt    -- List tables (should show 11)
\q     -- Quit
```

---

### 8. **Test Database**

Run this test query to make sure everything works:

```bash
./db.sh connect       # or db.bat → option 6
```

```sql
-- Create test user
INSERT INTO users (email, password_hash, full_name, phone, role)
VALUES ('test@test.com', 'hash123', 'Test User', '+254712345678', 'landlord')
RETURNING id, email, full_name;

-- Should return the created user with UUID

-- Clean up
DELETE FROM users WHERE email = 'test@test.com';

-- Exit
\q
```

If this works, **you're all set!** ✅

---

## 🎉 Success!

Your database is now running with:
- ✅ 11 tables created
- ✅ All indexes and triggers active
- ✅ pgAdmin for visual management
- ✅ Ready for backend connection

---

## 📝 Common Commands

### Start/Stop Database
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart postgres
```

### View Logs
```bash
docker-compose logs postgres
docker-compose logs -f postgres    # Follow logs
```

### Backup Database
```bash
./db.sh backup        # Mac/Linux
db.bat                # Windows → option 9
```

### Connect to Database
```bash
./db.sh connect       # Mac/Linux
db.bat                # Windows → option 6
```

---

## ⚠️ Troubleshooting

### "Port 5432 already in use"
- Stop other PostgreSQL: `brew services stop postgresql` (Mac)
- Or change port in `.env`: `POSTGRES_PORT=5433`

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running
- Check system tray for whale icon

### "Error response from daemon"
- Restart Docker Desktop
- Try: `docker-compose down && docker-compose up -d`

### Want to start fresh?
```bash
docker-compose down -v    # Deletes all data
docker-compose up -d      # Fresh start
```

---

## 🔜 Next Steps

Once database is running:

1. **Choose Backend Framework**
   - Node.js (Express/NestJS)
   - Python (FastAPI/Django)
   - Your preference?

2. **Set Up Backend Project**
   - Authentication
   - API endpoints
   - Database connection

3. **M-Pesa Integration**
   - Daraja API setup
   - Webhook endpoints
   - Payment matching

4. **Frontend Development**
   - Dashboard UI
   - Property management
   - Reports

---

**Need Help?**
- Check `README-DATABASE.md` for detailed instructions
- View logs: `docker-compose logs postgres`
- Database not working? Try: `docker-compose down -v && docker-compose up -d`

---

Ready to proceed? Let me know which step you're on! 🚀