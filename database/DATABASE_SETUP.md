# Database Setup Guide

## Prerequisites

- PostgreSQL 14+ installed
- Database admin access
- `psql` command-line tool

## Step 1: Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE property_management;

# Create dedicated user (recommended for production)
CREATE USER prop_mgmt_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE property_management TO prop_mgmt_user;

# Exit
\q
```

## Step 2: Run Migration

```bash
# Run the initial schema migration
psql -U prop_mgmt_user -d property_management -f 001_initial_schema.sql

# Or if using postgres user:
sudo -u postgres psql -d property_management -f 001_initial_schema.sql
```

## Step 3: Verify Installation

```bash
# Connect to database
psql -U prop_mgmt_user -d property_management

# Run verification queries (see below)
```

### Verification Queries

```sql
-- 1. Check all tables are created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected: 11 tables
-- audit_logs, invoices, mpesa_configs, notifications, payment_receipts, 
-- payments, properties, tenant_credits, tenants, units, users

-- 2. Check triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- Expected: 8 triggers

-- 3. Check functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION'
ORDER BY routine_name;

-- Expected: 5+ functions

-- 4. Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Expected: 50+ indexes

-- 5. Verify constraints
SELECT conname, contype, conrelid::regclass AS table_name
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text, contype;

-- 6. Test invoice number generation
INSERT INTO users (email, password_hash, full_name, phone, role)
VALUES ('test@test.com', 'hash', 'Test User', '+254712345678', 'landlord')
RETURNING id;

-- Use the returned user ID in next queries
-- (Replace {user_id} with actual UUID from above)

INSERT INTO properties (landlord_id, name, address)
VALUES ('{user_id}', 'Test Property', '123 Test St')
RETURNING id;

-- Use the returned property ID
-- (Replace {property_id} with actual UUID from above)

INSERT INTO units (property_id, unit_number, base_rent)
VALUES ('{property_id}', 'A1', 10000.00)
RETURNING id;

-- Use the returned unit ID
-- (Replace {unit_id} with actual UUID from above)

INSERT INTO tenants (unit_id, property_id, full_name, phone, email, base_rent, security_deposit_amount)
VALUES ('{unit_id}', '{property_id}', 'Test Tenant', '+254722222222', 'tenant@test.com', 10000.00, 10000.00)
RETURNING id;

-- Use the returned tenant ID
-- (Replace {tenant_id} with actual UUID from above)

-- Test invoice creation with auto-generated invoice_number
INSERT INTO invoices (tenant_id, property_id, unit_id, invoice_type, amount, due_date, month, year)
VALUES ('{tenant_id}', '{property_id}', '{unit_id}', 'monthly_rent', 10000.00, CURRENT_DATE, 2, 2026)
RETURNING invoice_number;

-- Should return something like: INV-2026-02-000001

-- Clean up test data
DELETE FROM invoices WHERE tenant_id = '{tenant_id}';
DELETE FROM tenants WHERE id = '{tenant_id}';
DELETE FROM units WHERE id = '{unit_id}';
DELETE FROM properties WHERE id = '{property_id}';
DELETE FROM users WHERE email = 'test@test.com';
```

## Step 4: Security Configuration

### 1. Change Default Admin Password

```sql
-- Update admin user password
-- First, generate bcrypt hash for your password using a tool or library
-- Then update:
UPDATE users 
SET password_hash = 'your_bcrypt_hash_here'
WHERE email = 'admin@propertymanager.com';
```

### 2. Set Up Row-Level Security (Optional but Recommended)

```sql
-- Enable RLS on sensitive tables
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Create policies (example for properties)
CREATE POLICY landlord_properties_policy ON properties
    FOR ALL
    TO prop_mgmt_user
    USING (landlord_id = current_setting('app.current_user_id')::UUID);

-- Note: Requires setting current_user_id in application:
-- SET LOCAL app.current_user_id = 'user-uuid-here';
```

### 3. Configure Encryption for Sensitive Fields

Your application should encrypt these fields before storing:
- `mpesa_configs.consumer_key`
- `mpesa_configs.consumer_secret`
- `mpesa_configs.passkey`

Example Python code using cryptography library:

```python
from cryptography.fernet import Fernet
import os

# Store this key in environment variable, NOT in code
ENCRYPTION_KEY = os.getenv('DB_ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY)

# Encrypt
def encrypt_value(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()

# Decrypt
def decrypt_value(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()
```

## Step 5: Backup Configuration

### Automated Daily Backups

```bash
# Create backup script
cat > /usr/local/bin/backup_property_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/property_management"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="property_management"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U prop_mgmt_user $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Delete backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
EOF

# Make executable
chmod +x /usr/local/bin/backup_property_db.sh

# Add to crontab (runs daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_property_db.sh") | crontab -
```

### Manual Backup

```bash
# Backup
pg_dump -U prop_mgmt_user property_management > backup.sql

# Restore
psql -U prop_mgmt_user property_management < backup.sql
```

## Step 6: Performance Optimization

```sql
-- Analyze tables for query optimization
ANALYZE;

-- Update table statistics
VACUUM ANALYZE;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Step 7: Monitoring Queries

```sql
-- Active connections
SELECT * FROM pg_stat_activity WHERE datname = 'property_management';

-- Slow queries (queries taking > 1 second)
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Table bloat check
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
```

## Common Operations

### Add New Landlord

```sql
INSERT INTO users (email, password_hash, full_name, phone, role)
VALUES (
    'landlord@example.com',
    '$2b$10$...', -- bcrypt hash of password
    'John Doe',
    '+254712345678',
    'landlord'
);
```

### Add Property with M-Pesa Config

```sql
-- First, get landlord_id from users table
-- Then insert property
INSERT INTO properties (landlord_id, name, address)
VALUES ('{landlord_id}', 'Sunset Apartments', 'Nairobi, Kenya')
RETURNING id;

-- Add M-Pesa configuration
INSERT INTO mpesa_configs (
    property_id,
    paybill_shortcode,
    consumer_key,
    consumer_secret,
    environment
)
VALUES (
    '{property_id}',
    '123456',
    'encrypted_consumer_key_here',
    'encrypted_consumer_secret_here',
    'sandbox'
);
```

### Query Unpaid Invoices

```sql
SELECT 
    i.invoice_number,
    i.invoice_type,
    t.full_name AS tenant_name,
    u.unit_number,
    i.amount,
    i.paid_amount,
    i.due_date,
    i.status
FROM invoices i
JOIN tenants t ON i.tenant_id = t.id
JOIN units u ON i.unit_id = u.id
WHERE i.status IN ('unpaid', 'partially_paid', 'overdue')
ORDER BY i.due_date;
```

### Query Unmatched Payments

```sql
SELECT 
    p.trans_id,
    p.amount,
    p.msisdn,
    p.bill_ref_number,
    p.first_name,
    p.last_name,
    p.created_at
FROM payments p
WHERE p.status = 'unmatched'
ORDER BY p.created_at DESC;
```

## Troubleshooting

### Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Permission Issues

```sql
-- Grant all privileges to user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prop_mgmt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO prop_mgmt_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO prop_mgmt_user;
```

### Reset Sequences

```sql
-- If invoice or receipt numbers are out of sync
SELECT setval('invoice_number_seq', (SELECT MAX(id) FROM invoices));
SELECT setval('receipt_number_seq', (SELECT MAX(id) FROM payment_receipts));
```

## Environment Variables

Create a `.env` file for your application:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=property_management
DB_USER=prop_mgmt_user
DB_PASSWORD=your_secure_password_here

# Encryption
DB_ENCRYPTION_KEY=your_fernet_key_here

# M-Pesa (Daraja)
MPESA_ENVIRONMENT=sandbox  # or production
MPESA_CALLBACK_BASE_URL=https://yourdomain.com

# SMS (Africa's Talking)
AFRICASTALKING_USERNAME=sandbox  # or your username
AFRICASTALKING_API_KEY=your_api_key_here

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_key_here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Application
APP_SECRET_KEY=your_app_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

## Next Steps

1. ✅ Database schema created
2. ⏭️ Set up application backend (Node.js/Python)
3. ⏭️ Implement authentication system
4. ⏭️ Build M-Pesa integration
5. ⏭️ Create API endpoints
6. ⏭️ Build frontend interface

---

**Database Version**: 1.0  
**Last Updated**: 2026-02-03