# Property Management System - Database Schema

## Overview
PostgreSQL database schema for a multi-landlord property management system with M-Pesa payment integration, automated invoicing, and SMS notifications.

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     USERS       │
│─────────────────│
│ id (PK)         │
│ email           │
│ password_hash   │
│ full_name       │
│ phone           │
│ role            │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────────┐
│    PROPERTIES           │
│─────────────────────────│
│ id (PK)                 │
│ landlord_id (FK)        │
│ name                    │
│ address                 │
│ description             │
│ created_at              │
│ updated_at              │
│ created_by (FK)         │
│ updated_by (FK)         │
└────────┬────────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────────┐          ┌──────────────────────┐
│    UNITS                 │          │  MPESA_CONFIGS       │
│──────────────────────────│          │──────────────────────│
│ id (PK)                  │          │ id (PK)              │
│ property_id (FK)         │          │ property_id (FK)     │
│ unit_number              │◄─────────│ paybill_shortcode    │
│ bedrooms                 │    1:1   │ consumer_key         │
│ bathrooms                │          │ consumer_secret      │
│ size_sqm                 │          │ passkey              │
│ base_rent                │          │ environment          │
│ is_available             │          │ is_active            │
│ created_at               │          │ validation_url       │
│ updated_at               │          │ confirmation_url     │
│ created_by (FK)          │          │ created_at           │
│ updated_by (FK)          │          │ updated_at           │
└────────┬─────────────────┘          └──────────────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────────┐
│    TENANTS               │
│──────────────────────────│
│ id (PK)                  │
│ unit_id (FK)             │
│ property_id (FK)         │
│ full_name                │
│ phone                    │
│ email                    │
│ id_number                │
│ base_rent                │
│ security_deposit_amount  │
│ security_deposit_paid    │
│ security_deposit_paid_date│
│ move_in_date             │
│ move_out_date            │
│ move_out_damages         │
│ move_out_unpaid_rent     │
│ security_deposit_refund  │
│ status                   │──┐
│ created_at               │  │
│ updated_at               │  │
│ created_by (FK)          │  │
│ updated_by (FK)          │  │
└────────┬─────────────────┘  │
         │                     │
         │ 1:N                 │
         │                     │
┌────────▼─────────────────┐  │
│    INVOICES              │  │
│──────────────────────────│  │
│ id (PK)                  │  │
│ tenant_id (FK)           │──┘
│ property_id (FK)         │
│ unit_id (FK)             │
│ invoice_number           │
│ invoice_type             │
│ amount                   │
│ paid_amount              │
│ credit_applied           │
│ due_date                 │
│ month                    │
│ year                     │
│ status                   │
│ notes                    │
│ created_at               │
│ updated_at               │
│ created_by (FK)          │
│ updated_by (FK)          │
└────────┬─────────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────────┐
│    PAYMENTS              │
│──────────────────────────│
│ id (PK)                  │
│ invoice_id (FK)          │
│ tenant_id (FK)           │
│ property_id (FK)         │
│ trans_id                 │
│ amount                   │
│ msisdn                   │
│ paybill_shortcode        │
│ bill_ref_number          │
│ first_name               │
│ middle_name              │
│ last_name                │
│ trans_time               │
│ payment_method           │
│ status                   │
│ raw_payload              │
│ matched_at               │
│ created_at               │
│ updated_at               │
│ created_by (FK)          │
│ updated_by (FK)          │
└────────┬─────────────────┘
         │
         │
┌────────▼─────────────────┐
│  PAYMENT_RECEIPTS        │
│──────────────────────────│
│ id (PK)                  │
│ payment_id (FK)          │
│ invoice_id (FK)          │
│ tenant_id (FK)           │
│ receipt_number           │
│ amount                   │
│ payment_date             │
│ email_sent               │
│ sms_sent                 │
│ created_at               │
└──────────────────────────┘


┌──────────────────────────┐
│  NOTIFICATIONS           │
│──────────────────────────│
│ id (PK)                  │
│ tenant_id (FK)           │
│ invoice_id (FK)          │
│ notification_type        │
│ channel                  │
│ recipient                │
│ message                  │
│ status                   │
│ sent_at                  │
│ delivered_at             │
│ cost                     │
│ error_message            │
│ created_at               │
└──────────────────────────┘


┌──────────────────────────┐
│  TENANT_CREDITS          │
│──────────────────────────│
│ id (PK)                  │
│ tenant_id (FK)           │
│ property_id (FK)         │
│ amount                   │
│ source_payment_id (FK)   │
│ applied_to_invoice_id(FK)│
│ status                   │
│ notes                    │
│ created_at               │
│ applied_at               │
└──────────────────────────┘


┌──────────────────────────┐
│  AUDIT_LOGS              │
│──────────────────────────│
│ id (PK)                  │
│ user_id (FK)             │
│ entity_type              │
│ entity_id                │
│ action                   │
│ old_values               │
│ new_values               │
│ ip_address               │
│ user_agent               │
│ created_at               │
└──────────────────────────┘
```

---

## Table Specifications

### 1. USERS
Stores landlord accounts and system administrators.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier         |
| email         | VARCHAR(255)          | UNIQUE, NOT NULL               | User email (login)                    |
| password_hash | VARCHAR(255)          | NOT NULL                       | Bcrypt hashed password                |
| full_name     | VARCHAR(255)          | NOT NULL                       | Full name                             |
| phone         | VARCHAR(20)           | NOT NULL                       | Phone with country code (+254...)     |
| role          | VARCHAR(50)           | NOT NULL, DEFAULT 'landlord'   | Role: 'landlord', 'admin'             |
| is_active     | BOOLEAN               | DEFAULT TRUE                   | Account status                        |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |

**Indexes:**
- `idx_users_email` on (email)
- `idx_users_phone` on (phone)

---

### 2. PROPERTIES
Stores property/building information.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique property identifier     |
| landlord_id   | UUID                  | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | Property owner      |
| name          | VARCHAR(255)          | NOT NULL                       | Property name                         |
| address       | TEXT                  | NOT NULL                       | Full address                          |
| description   | TEXT                  | NULL                           | Additional details                    |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |
| created_by    | UUID                  | REFERENCES users(id)           | User who created record               |
| updated_by    | UUID                  | REFERENCES users(id)           | User who last updated record          |

**Indexes:**
- `idx_properties_landlord` on (landlord_id)
- `idx_properties_name` on (name)

---

### 3. MPESA_CONFIGS
Stores M-Pesa Daraja API configuration per property.

| Column             | Type                  | Constraints                    | Description                           |
|--------------------|-----------------------|--------------------------------|---------------------------------------|
| id                 | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique config identifier      |
| property_id        | UUID                  | NOT NULL, UNIQUE, REFERENCES properties(id) ON DELETE CASCADE | Associated property |
| paybill_shortcode  | VARCHAR(20)           | NOT NULL                       | M-Pesa Paybill number                 |
| consumer_key       | VARCHAR(255)          | NOT NULL                       | Daraja consumer key (encrypted)       |
| consumer_secret    | VARCHAR(255)          | NOT NULL                       | Daraja consumer secret (encrypted)    |
| passkey            | VARCHAR(255)          | NULL                           | Lipa Na M-Pesa passkey (encrypted)    |
| environment        | VARCHAR(20)           | NOT NULL, DEFAULT 'sandbox'    | 'sandbox' or 'production'             |
| is_active          | BOOLEAN               | DEFAULT TRUE                   | Config active status                  |
| validation_url     | VARCHAR(500)          | NULL                           | Registered validation URL             |
| confirmation_url   | VARCHAR(500)          | NULL                           | Registered confirmation URL           |
| created_at         | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at         | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |

**Indexes:**
- `idx_mpesa_property` on (property_id)
- `idx_mpesa_shortcode` on (paybill_shortcode)

---

### 4. UNITS
Stores individual rental units within properties.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique unit identifier         |
| property_id   | UUID                  | NOT NULL, REFERENCES properties(id) ON DELETE CASCADE | Parent property    |
| unit_number   | VARCHAR(50)           | NOT NULL                       | Unit identifier (A5, 12, etc.)        |
| bedrooms      | INTEGER               | NULL                           | Number of bedrooms                    |
| bathrooms     | INTEGER               | NULL                           | Number of bathrooms                   |
| size_sqm      | DECIMAL(10,2)         | NULL                           | Size in square meters                 |
| base_rent     | DECIMAL(10,2)         | NOT NULL                       | Default monthly rent (KES)            |
| is_available  | BOOLEAN               | DEFAULT TRUE                   | Availability status                   |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |
| created_by    | UUID                  | REFERENCES users(id)           | User who created record               |
| updated_by    | UUID                  | REFERENCES users(id)           | User who last updated record          |

**Constraints:**
- UNIQUE (property_id, unit_number)

**Indexes:**
- `idx_units_property` on (property_id)
- `idx_units_number` on (unit_number)
- `idx_units_available` on (is_available)

---

### 5. TENANTS
Stores tenant information and lease details.

| Column                      | Type                  | Constraints                    | Description                           |
|-----------------------------|-----------------------|--------------------------------|---------------------------------------|
| id                          | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique tenant identifier       |
| unit_id                     | UUID                  | NOT NULL, REFERENCES units(id) ON DELETE RESTRICT | Current/last unit    |
| property_id                 | UUID                  | NOT NULL, REFERENCES properties(id) ON DELETE CASCADE | Property          |
| full_name                   | VARCHAR(255)          | NOT NULL                       | Tenant full name                      |
| phone                       | VARCHAR(20)           | NOT NULL                       | Phone with country code (+254...)     |
| email                       | VARCHAR(255)          | NOT NULL                       | Tenant email                          |
| id_number                   | VARCHAR(50)           | NULL                           | National ID or passport               |
| base_rent                   | DECIMAL(10,2)         | NOT NULL                       | Monthly rent amount (KES)             |
| security_deposit_amount     | DECIMAL(10,2)         | NOT NULL                       | Security deposit amount (KES)         |
| security_deposit_paid       | BOOLEAN               | DEFAULT FALSE                  | Whether deposit is paid               |
| security_deposit_paid_date  | DATE                  | NULL                           | Date deposit was paid                 |
| move_in_date                | DATE                  | NULL                           | Actual move-in date                   |
| move_out_date               | DATE                  | NULL                           | Move-out date                         |
| move_out_damages            | DECIMAL(10,2)         | NULL                           | Damages amount at move-out            |
| move_out_unpaid_rent        | DECIMAL(10,2)         | NULL                           | Unpaid rent at move-out               |
| security_deposit_refund     | DECIMAL(10,2)         | NULL                           | Final refund amount (can be negative) |
| status                      | VARCHAR(20)           | NOT NULL, DEFAULT 'pending'    | 'pending', 'active', 'moved_out'      |
| created_at                  | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at                  | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |
| created_by                  | UUID                  | REFERENCES users(id)           | User who created record               |
| updated_by                  | UUID                  | REFERENCES users(id)           | User who last updated record          |

**Indexes:**
- `idx_tenants_unit` on (unit_id)
- `idx_tenants_property` on (property_id)
- `idx_tenants_phone` on (phone)
- `idx_tenants_status` on (status)
- `idx_tenants_email` on (email)

---

### 6. INVOICES
Stores rent and security deposit invoices.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique invoice identifier      |
| tenant_id     | UUID                  | NOT NULL, REFERENCES tenants(id) ON DELETE CASCADE | Invoice recipient     |
| property_id   | UUID                  | NOT NULL, REFERENCES properties(id) ON DELETE CASCADE | Property          |
| unit_id       | UUID                  | NOT NULL, REFERENCES units(id) ON DELETE RESTRICT | Unit                   |
| invoice_number| VARCHAR(50)           | UNIQUE, NOT NULL               | Human-readable invoice number         |
| invoice_type  | VARCHAR(30)           | NOT NULL                       | 'monthly_rent' or 'security_deposit'  |
| amount        | DECIMAL(10,2)         | NOT NULL                       | Total invoice amount (KES)            |
| paid_amount   | DECIMAL(10,2)         | DEFAULT 0.00                   | Amount paid so far (KES)              |
| credit_applied| DECIMAL(10,2)         | DEFAULT 0.00                   | Credit applied from overpayments      |
| due_date      | DATE                  | NOT NULL                       | Payment due date                      |
| month         | INTEGER               | NULL                           | Month (1-12) for monthly_rent         |
| year          | INTEGER               | NULL                           | Year for monthly_rent                 |
| status        | VARCHAR(20)           | NOT NULL, DEFAULT 'unpaid'     | 'unpaid', 'partially_paid', 'paid', 'overdue' |
| notes         | TEXT                  | NULL                           | Additional notes                      |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |
| created_by    | UUID                  | REFERENCES users(id)           | User who created record               |
| updated_by    | UUID                  | REFERENCES users(id)           | User who last updated record          |

**Constraints:**
- UNIQUE (tenant_id, invoice_type, month, year) for monthly_rent invoices
- CHECK (invoice_type IN ('monthly_rent', 'security_deposit'))
- CHECK (status IN ('unpaid', 'partially_paid', 'paid', 'overdue'))

**Indexes:**
- `idx_invoices_tenant` on (tenant_id)
- `idx_invoices_property` on (property_id)
- `idx_invoices_status` on (status)
- `idx_invoices_due_date` on (due_date)
- `idx_invoices_number` on (invoice_number)
- `idx_invoices_type` on (invoice_type)
- `idx_invoices_month_year` on (month, year)

---

### 7. PAYMENTS
Stores all payment transactions (M-Pesa and manual).

| Column            | Type                  | Constraints                    | Description                           |
|-------------------|-----------------------|--------------------------------|---------------------------------------|
| id                | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique payment identifier      |
| invoice_id        | UUID                  | NULL, REFERENCES invoices(id) ON DELETE SET NULL | Linked invoice (if matched) |
| tenant_id         | UUID                  | NULL, REFERENCES tenants(id) ON DELETE SET NULL | Linked tenant (if matched)  |
| property_id       | UUID                  | NULL, REFERENCES properties(id) ON DELETE CASCADE | Property              |
| trans_id          | VARCHAR(100)          | UNIQUE, NOT NULL               | M-Pesa TransID or manual ref          |
| amount            | DECIMAL(10,2)         | NOT NULL                       | Payment amount (KES)                  |
| msisdn            | VARCHAR(20)           | NULL                           | Payer phone number                    |
| paybill_shortcode | VARCHAR(20)           | NOT NULL                       | Paybill used                          |
| bill_ref_number   | VARCHAR(100)          | NULL                           | Account number from M-Pesa (A5, A5-DEP) |
| first_name        | VARCHAR(100)          | NULL                           | Payer first name (M-Pesa)             |
| middle_name       | VARCHAR(100)          | NULL                           | Payer middle name (M-Pesa)            |
| last_name         | VARCHAR(100)          | NULL                           | Payer last name (M-Pesa)              |
| trans_time        | TIMESTAMP             | NULL                           | M-Pesa transaction timestamp          |
| payment_method    | VARCHAR(50)           | NOT NULL, DEFAULT 'mpesa'      | 'mpesa', 'cash', 'bank_transfer'      |
| status            | VARCHAR(30)           | NOT NULL, DEFAULT 'unmatched'  | 'matched', 'unmatched', 'duplicate', 'failed' |
| raw_payload       | JSONB                 | NULL                           | Full M-Pesa callback payload          |
| matched_at        | TIMESTAMP             | NULL                           | When payment was matched              |
| created_at        | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |
| updated_at        | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Last update time                      |
| created_by        | UUID                  | REFERENCES users(id)           | User who created record (manual)      |
| updated_by        | UUID                  | REFERENCES users(id)           | User who last updated record          |

**Indexes:**
- `idx_payments_invoice` on (invoice_id)
- `idx_payments_tenant` on (tenant_id)
- `idx_payments_property` on (property_id)
- `idx_payments_trans_id` on (trans_id)
- `idx_payments_status` on (status)
- `idx_payments_paybill` on (paybill_shortcode)
- `idx_payments_bill_ref` on (bill_ref_number)
- `idx_payments_msisdn` on (msisdn)

---

### 8. PAYMENT_RECEIPTS
Stores generated receipts for payments.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique receipt identifier      |
| payment_id    | UUID                  | NOT NULL, REFERENCES payments(id) ON DELETE CASCADE | Linked payment        |
| invoice_id    | UUID                  | NULL, REFERENCES invoices(id) ON DELETE SET NULL | Linked invoice           |
| tenant_id     | UUID                  | NOT NULL, REFERENCES tenants(id) ON DELETE CASCADE | Recipient             |
| receipt_number| VARCHAR(50)           | UNIQUE, NOT NULL               | Human-readable receipt number         |
| amount        | DECIMAL(10,2)         | NOT NULL                       | Receipt amount (KES)                  |
| payment_date  | TIMESTAMP             | NOT NULL                       | Payment date/time                     |
| email_sent    | BOOLEAN               | DEFAULT FALSE                  | Email sent status                     |
| sms_sent      | BOOLEAN               | DEFAULT FALSE                  | SMS sent status                       |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |

**Indexes:**
- `idx_receipts_payment` on (payment_id)
- `idx_receipts_tenant` on (tenant_id)
- `idx_receipts_number` on (receipt_number)

---

### 9. NOTIFICATIONS
Stores all sent notifications (SMS, Email).

| Column            | Type                  | Constraints                    | Description                           |
|-------------------|-----------------------|--------------------------------|---------------------------------------|
| id                | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique notification identifier |
| tenant_id         | UUID                  | NULL, REFERENCES tenants(id) ON DELETE CASCADE | Recipient tenant      |
| invoice_id        | UUID                  | NULL, REFERENCES invoices(id) ON DELETE SET NULL | Related invoice      |
| notification_type | VARCHAR(50)           | NOT NULL                       | 'invoice_generated', 'payment_reminder', 'payment_received' |
| channel           | VARCHAR(20)           | NOT NULL                       | 'sms', 'email'                        |
| recipient         | VARCHAR(255)          | NOT NULL                       | Phone or email                        |
| message           | TEXT                  | NOT NULL                       | Message content                       |
| status            | VARCHAR(20)           | NOT NULL, DEFAULT 'pending'    | 'pending', 'sent', 'delivered', 'failed' |
| sent_at           | TIMESTAMP             | NULL                           | When notification was sent            |
| delivered_at      | TIMESTAMP             | NULL                           | When notification was delivered       |
| cost              | DECIMAL(10,4)         | NULL                           | SMS cost in KES                       |
| error_message     | TEXT                  | NULL                           | Error details if failed               |
| created_at        | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | Record creation time                  |

**Indexes:**
- `idx_notifications_tenant` on (tenant_id)
- `idx_notifications_invoice` on (invoice_id)
- `idx_notifications_status` on (status)
- `idx_notifications_type` on (notification_type)
- `idx_notifications_channel` on (channel)

---

### 10. TENANT_CREDITS
Stores credit balances from overpayments.

| Column                | Type                  | Constraints                    | Description                           |
|-----------------------|-----------------------|--------------------------------|---------------------------------------|
| id                    | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique credit identifier       |
| tenant_id             | UUID                  | NOT NULL, REFERENCES tenants(id) ON DELETE CASCADE | Credit owner          |
| property_id           | UUID                  | NOT NULL, REFERENCES properties(id) ON DELETE CASCADE | Property          |
| amount                | DECIMAL(10,2)         | NOT NULL                       | Credit amount (KES)                   |
| source_payment_id     | UUID                  | NULL, REFERENCES payments(id) ON DELETE SET NULL | Payment that created credit |
| applied_to_invoice_id | UUID                  | NULL, REFERENCES invoices(id) ON DELETE SET NULL | Invoice where applied |
| status                | VARCHAR(20)           | NOT NULL, DEFAULT 'available'  | 'available', 'applied', 'expired'     |
| notes                 | TEXT                  | NULL                           | Additional notes                      |
| created_at            | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | When credit was created               |
| applied_at            | TIMESTAMP             | NULL                           | When credit was applied               |

**Indexes:**
- `idx_credits_tenant` on (tenant_id)
- `idx_credits_status` on (status)
- `idx_credits_property` on (property_id)

---

### 11. AUDIT_LOGS
Comprehensive audit trail for all critical operations.

| Column        | Type                  | Constraints                    | Description                           |
|---------------|-----------------------|--------------------------------|---------------------------------------|
| id            | UUID                  | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique log identifier          |
| user_id       | UUID                  | NULL, REFERENCES users(id) ON DELETE SET NULL | User who performed action |
| entity_type   | VARCHAR(100)          | NOT NULL                       | Table name (invoices, payments, etc.) |
| entity_id     | UUID                  | NOT NULL                       | Record ID that was modified           |
| action        | VARCHAR(50)           | NOT NULL                       | 'CREATE', 'UPDATE', 'DELETE'          |
| old_values    | JSONB                 | NULL                           | Previous state (for UPDATE/DELETE)    |
| new_values    | JSONB                 | NULL                           | New state (for CREATE/UPDATE)         |
| ip_address    | VARCHAR(50)           | NULL                           | User IP address                       |
| user_agent    | TEXT                  | NULL                           | Browser/client info                   |
| created_at    | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP      | When action occurred                  |

**Indexes:**
- `idx_audit_user` on (user_id)
- `idx_audit_entity` on (entity_type, entity_id)
- `idx_audit_action` on (action)
- `idx_audit_created` on (created_at)

---

## Key Business Rules & Constraints

### Invoice Generation Rules
1. **Security Deposit Invoice**: Created once when tenant is added, due in 5 days
2. **First Month Rent Invoice**: Created when tenant is added, due on 1st of month
3. **Monthly Rent Invoices**: Auto-generated on 1st of each month for 'active' tenants
4. **Credit Application**: Credits auto-applied to new invoices before due date

### Payment Matching Logic
1. Match by: `paybill_shortcode` + `bill_ref_number`
2. If `bill_ref_number` ends with `-DEP`: match to security_deposit invoice
3. Else: match to most recent unpaid monthly_rent invoice
4. Partial payments allowed - update `paid_amount` until invoice.amount reached
5. Overpayments: create credit in `tenant_credits` table

### Tenant Status Transitions
- **pending** → **active**: When both security_deposit AND first_month_rent invoices are paid
- **active** → **moved_out**: When landlord initiates move-out process
- **moved_out**: No new invoices generated

### Notification Triggers
1. **Invoice Generated**: Send SMS + Email with invoice details
2. **Payment Received**: Send SMS + Email receipt
3. **Payment Reminder**: Day 5 & Day 9 for unpaid invoices (SMS only)

---

## Data Types Reference

| PostgreSQL Type | Description                          | Example                    |
|-----------------|--------------------------------------|----------------------------|
| UUID            | 128-bit identifier                   | 550e8400-e29b-41d4-a716... |
| VARCHAR(n)      | Variable character, max n            | "John Doe"                 |
| TEXT            | Unlimited text                       | Long descriptions          |
| DECIMAL(10,2)   | Decimal with 10 digits, 2 decimal    | 15000.50                   |
| BOOLEAN         | True/False                           | TRUE, FALSE                |
| TIMESTAMP       | Date + Time                          | 2026-02-03 14:30:00        |
| DATE            | Date only                            | 2026-02-03                 |
| INTEGER         | Whole number                         | 3, 150                     |
| JSONB           | Binary JSON (indexed, queryable)     | {"key": "value"}           |

---

## Security & Encryption Notes

**Encrypted Fields** (Application-level encryption recommended):
- `mpesa_configs.consumer_key`
- `mpesa_configs.consumer_secret`
- `mpesa_configs.passkey`
- `users.password_hash` (bcrypt hashing, not encryption)

**Sensitive Data**:
- Store API credentials encrypted at rest
- Use environment variables for encryption keys
- Implement row-level security for multi-tenant isolation
- Regular automated backups with encryption

---

## Next Steps

1. ✅ Schema design complete
2. ⏭️ Create SQL migration files
3. ⏭️ Set up database triggers for `updated_at` auto-update
4. ⏭️ Create database functions for invoice generation
5. ⏭️ Implement audit logging triggers

---

**Schema Version**: 1.0  
**Last Updated**: 2026-02-03  
**Database**: PostgreSQL 14+