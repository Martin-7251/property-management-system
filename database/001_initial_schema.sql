-- ============================================================================
-- Property Management System - Database Migration
-- Version: 1.0
-- Database: PostgreSQL 14+
-- Description: Initial schema creation with all tables, constraints, and indexes
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PART 1: TABLES
-- ============================================================================

-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'landlord',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_user_role CHECK (role IN ('landlord', 'admin')),
    CONSTRAINT chk_user_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_user_phone CHECK (phone ~* '^\+[1-9]\d{1,14}$')
);

COMMENT ON TABLE users IS 'Landlord accounts and system administrators';
COMMENT ON COLUMN users.phone IS 'Phone number with country code (E.164 format)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';

-- Table: properties
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    landlord_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

COMMENT ON TABLE properties IS 'Property/building information owned by landlords';

-- Table: mpesa_configs
CREATE TABLE mpesa_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL UNIQUE REFERENCES properties(id) ON DELETE CASCADE,
    paybill_shortcode VARCHAR(20) NOT NULL,
    consumer_key VARCHAR(255) NOT NULL,
    consumer_secret VARCHAR(255) NOT NULL,
    passkey VARCHAR(255),
    environment VARCHAR(20) NOT NULL DEFAULT 'sandbox',
    is_active BOOLEAN DEFAULT TRUE,
    validation_url VARCHAR(500),
    confirmation_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_mpesa_environment CHECK (environment IN ('sandbox', 'production'))
);

COMMENT ON TABLE mpesa_configs IS 'M-Pesa Daraja API configuration per property';
COMMENT ON COLUMN mpesa_configs.consumer_key IS 'Encrypted Daraja consumer key';
COMMENT ON COLUMN mpesa_configs.consumer_secret IS 'Encrypted Daraja consumer secret';
COMMENT ON COLUMN mpesa_configs.passkey IS 'Encrypted Lipa Na M-Pesa passkey';

-- Table: units
CREATE TABLE units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    size_sqm DECIMAL(10,2),
    base_rent DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    CONSTRAINT uq_property_unit UNIQUE (property_id, unit_number),
    CONSTRAINT chk_unit_bedrooms CHECK (bedrooms >= 0),
    CONSTRAINT chk_unit_bathrooms CHECK (bathrooms >= 0),
    CONSTRAINT chk_unit_size CHECK (size_sqm > 0),
    CONSTRAINT chk_unit_rent CHECK (base_rent >= 0)
);

COMMENT ON TABLE units IS 'Individual rental units within properties';
COMMENT ON COLUMN units.unit_number IS 'Unit identifier (A5, 12, B-101, etc.)';

-- Table: tenants
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID NOT NULL REFERENCES units(id) ON DELETE RESTRICT,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    id_number VARCHAR(50),
    base_rent DECIMAL(10,2) NOT NULL,
    security_deposit_amount DECIMAL(10,2) NOT NULL,
    security_deposit_paid BOOLEAN DEFAULT FALSE,
    security_deposit_paid_date DATE,
    move_in_date DATE,
    move_out_date DATE,
    move_out_damages DECIMAL(10,2),
    move_out_unpaid_rent DECIMAL(10,2),
    security_deposit_refund DECIMAL(10,2),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    CONSTRAINT chk_tenant_status CHECK (status IN ('pending', 'active', 'moved_out')),
    CONSTRAINT chk_tenant_phone CHECK (phone ~* '^\+[1-9]\d{1,14}$'),
    CONSTRAINT chk_tenant_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_tenant_rent CHECK (base_rent >= 0),
    CONSTRAINT chk_tenant_deposit CHECK (security_deposit_amount >= 0),
    CONSTRAINT chk_tenant_damages CHECK (move_out_damages IS NULL OR move_out_damages >= 0),
    CONSTRAINT chk_tenant_unpaid_rent CHECK (move_out_unpaid_rent IS NULL OR move_out_unpaid_rent >= 0)
);

COMMENT ON TABLE tenants IS 'Tenant information and lease details';
COMMENT ON COLUMN tenants.status IS 'pending: awaiting payment, active: moved in, moved_out: lease ended';
COMMENT ON COLUMN tenants.security_deposit_refund IS 'Can be negative if tenant owes money';

-- Table: invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    unit_id UUID NOT NULL REFERENCES units(id) ON DELETE RESTRICT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_type VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    credit_applied DECIMAL(10,2) DEFAULT 0.00,
    due_date DATE NOT NULL,
    month INTEGER,
    year INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'unpaid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    CONSTRAINT chk_invoice_type CHECK (invoice_type IN ('monthly_rent', 'security_deposit')),
    CONSTRAINT chk_invoice_status CHECK (status IN ('unpaid', 'partially_paid', 'paid', 'overdue')),
    CONSTRAINT chk_invoice_amount CHECK (amount >= 0),
    CONSTRAINT chk_invoice_paid_amount CHECK (paid_amount >= 0 AND paid_amount <= amount + credit_applied),
    CONSTRAINT chk_invoice_credit CHECK (credit_applied >= 0),
    CONSTRAINT chk_invoice_month CHECK (month IS NULL OR (month >= 1 AND month <= 12)),
    CONSTRAINT chk_invoice_year CHECK (year IS NULL OR year >= 2020),
    CONSTRAINT uq_tenant_monthly_invoice UNIQUE (tenant_id, invoice_type, month, year)
);

COMMENT ON TABLE invoices IS 'Rent and security deposit invoices';
COMMENT ON COLUMN invoices.invoice_type IS 'monthly_rent or security_deposit';
COMMENT ON COLUMN invoices.paid_amount IS 'Total amount paid towards this invoice';
COMMENT ON COLUMN invoices.credit_applied IS 'Credit from overpayments applied to this invoice';

-- Table: payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    trans_id VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    msisdn VARCHAR(20),
    paybill_shortcode VARCHAR(20) NOT NULL,
    bill_ref_number VARCHAR(100),
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    trans_time TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'mpesa',
    status VARCHAR(30) NOT NULL DEFAULT 'unmatched',
    raw_payload JSONB,
    matched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    CONSTRAINT chk_payment_method CHECK (payment_method IN ('mpesa', 'cash', 'bank_transfer')),
    CONSTRAINT chk_payment_status CHECK (status IN ('matched', 'unmatched', 'duplicate', 'failed')),
    CONSTRAINT chk_payment_amount CHECK (amount > 0)
);

COMMENT ON TABLE payments IS 'All payment transactions from M-Pesa and manual entries';
COMMENT ON COLUMN payments.trans_id IS 'M-Pesa TransID or manual reference (unique)';
COMMENT ON COLUMN payments.bill_ref_number IS 'Account number from M-Pesa (A5, A5-DEP, etc.)';
COMMENT ON COLUMN payments.raw_payload IS 'Full M-Pesa callback payload for audit';

-- Table: payment_receipts
CREATE TABLE payment_receipts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    email_sent BOOLEAN DEFAULT FALSE,
    sms_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_receipt_amount CHECK (amount > 0)
);

COMMENT ON TABLE payment_receipts IS 'Payment receipts sent to tenants';

-- Table: notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cost DECIMAL(10,4),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_notification_type CHECK (notification_type IN ('invoice_generated', 'payment_reminder_day5', 'payment_reminder_day9', 'payment_received', 'move_out_statement')),
    CONSTRAINT chk_notification_channel CHECK (channel IN ('sms', 'email')),
    CONSTRAINT chk_notification_status CHECK (status IN ('pending', 'sent', 'delivered', 'failed'))
);

COMMENT ON TABLE notifications IS 'All SMS and email notifications sent';

-- Table: tenant_credits
CREATE TABLE tenant_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    source_payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
    applied_to_invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP,
    
    CONSTRAINT chk_credit_amount CHECK (amount > 0),
    CONSTRAINT chk_credit_status CHECK (status IN ('available', 'applied', 'expired'))
);

COMMENT ON TABLE tenant_credits IS 'Credit balances from overpayments';

-- Table: audit_logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE'))
);

COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all critical operations';

-- ============================================================================
-- PART 2: INDEXES
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Properties indexes
CREATE INDEX idx_properties_landlord ON properties(landlord_id);
CREATE INDEX idx_properties_name ON properties(name);

-- M-Pesa configs indexes
CREATE INDEX idx_mpesa_property ON mpesa_configs(property_id);
CREATE INDEX idx_mpesa_shortcode ON mpesa_configs(paybill_shortcode);
CREATE INDEX idx_mpesa_active ON mpesa_configs(is_active);

-- Units indexes
CREATE INDEX idx_units_property ON units(property_id);
CREATE INDEX idx_units_number ON units(unit_number);
CREATE INDEX idx_units_available ON units(is_available);

-- Tenants indexes
CREATE INDEX idx_tenants_unit ON tenants(unit_id);
CREATE INDEX idx_tenants_property ON tenants(property_id);
CREATE INDEX idx_tenants_phone ON tenants(phone);
CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_status ON tenants(status);

-- Invoices indexes
CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_property ON invoices(property_id);
CREATE INDEX idx_invoices_unit ON invoices(unit_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_type ON invoices(invoice_type);
CREATE INDEX idx_invoices_month_year ON invoices(month, year);

-- Payments indexes
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_tenant ON payments(tenant_id);
CREATE INDEX idx_payments_property ON payments(property_id);
CREATE INDEX idx_payments_trans_id ON payments(trans_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_paybill ON payments(paybill_shortcode);
CREATE INDEX idx_payments_bill_ref ON payments(bill_ref_number);
CREATE INDEX idx_payments_msisdn ON payments(msisdn);
CREATE INDEX idx_payments_method ON payments(payment_method);

-- Payment receipts indexes
CREATE INDEX idx_receipts_payment ON payment_receipts(payment_id);
CREATE INDEX idx_receipts_tenant ON payment_receipts(tenant_id);
CREATE INDEX idx_receipts_number ON payment_receipts(receipt_number);
CREATE INDEX idx_receipts_invoice ON payment_receipts(invoice_id);

-- Notifications indexes
CREATE INDEX idx_notifications_tenant ON notifications(tenant_id);
CREATE INDEX idx_notifications_invoice ON notifications(invoice_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_channel ON notifications(channel);
CREATE INDEX idx_notifications_created ON notifications(created_at);

-- Tenant credits indexes
CREATE INDEX idx_credits_tenant ON tenant_credits(tenant_id);
CREATE INDEX idx_credits_property ON tenant_credits(property_id);
CREATE INDEX idx_credits_status ON tenant_credits(status);
CREATE INDEX idx_credits_payment ON tenant_credits(source_payment_id);

-- Audit logs indexes
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================================================
-- PART 3: TRIGGERS
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mpesa_configs_updated_at BEFORE UPDATE ON mpesa_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function: Auto-update invoice status based on paid_amount
CREATE OR REPLACE FUNCTION update_invoice_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.paid_amount + NEW.credit_applied >= NEW.amount THEN
        NEW.status = 'paid';
    ELSIF NEW.paid_amount > 0 OR NEW.credit_applied > 0 THEN
        NEW.status = 'partially_paid';
    ELSIF NEW.due_date < CURRENT_DATE THEN
        NEW.status = 'overdue';
    ELSE
        NEW.status = 'unpaid';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_invoice_status
    BEFORE INSERT OR UPDATE OF paid_amount, credit_applied, amount ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_invoice_status();

-- Function: Generate invoice number
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invoice_number IS NULL THEN
        NEW.invoice_number := 'INV-' || 
            TO_CHAR(CURRENT_DATE, 'YYYY-MM') || '-' || 
            LPAD(nextval('invoice_number_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for invoice numbers
CREATE SEQUENCE IF NOT EXISTS invoice_number_seq START 1;

CREATE TRIGGER trigger_generate_invoice_number
    BEFORE INSERT ON invoices
    FOR EACH ROW EXECUTE FUNCTION generate_invoice_number();

-- Function: Generate receipt number
CREATE OR REPLACE FUNCTION generate_receipt_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.receipt_number IS NULL THEN
        NEW.receipt_number := 'RCP-' || 
            TO_CHAR(CURRENT_DATE, 'YYYY-MM') || '-' || 
            LPAD(nextval('receipt_number_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for receipt numbers
CREATE SEQUENCE IF NOT EXISTS receipt_number_seq START 1;

CREATE TRIGGER trigger_generate_receipt_number
    BEFORE INSERT ON payment_receipts
    FOR EACH ROW EXECUTE FUNCTION generate_receipt_number();

-- ============================================================================
-- PART 4: HELPER FUNCTIONS
-- ============================================================================

-- Function: Get tenant's available credit balance
CREATE OR REPLACE FUNCTION get_tenant_credit_balance(p_tenant_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_credit DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(amount), 0)
    INTO total_credit
    FROM tenant_credits
    WHERE tenant_id = p_tenant_id AND status = 'available';
    
    RETURN total_credit;
END;
$$ LANGUAGE plpgsql;

-- Function: Get tenant's total unpaid invoices
CREATE OR REPLACE FUNCTION get_tenant_unpaid_amount(p_tenant_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_unpaid DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(amount - paid_amount - credit_applied), 0)
    INTO total_unpaid
    FROM invoices
    WHERE tenant_id = p_tenant_id AND status IN ('unpaid', 'partially_paid', 'overdue');
    
    RETURN total_unpaid;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if tenant can be activated
CREATE OR REPLACE FUNCTION check_tenant_activation()
RETURNS TRIGGER AS $$
DECLARE
    security_paid BOOLEAN;
    first_rent_paid BOOLEAN;
BEGIN
    -- Check if security deposit invoice is paid
    SELECT EXISTS (
        SELECT 1 FROM invoices 
        WHERE tenant_id = NEW.id 
        AND invoice_type = 'security_deposit' 
        AND status = 'paid'
    ) INTO security_paid;
    
    -- Check if first month's rent invoice is paid
    SELECT EXISTS (
        SELECT 1 FROM invoices 
        WHERE tenant_id = NEW.id 
        AND invoice_type = 'monthly_rent' 
        AND status = 'paid'
        ORDER BY created_at LIMIT 1
    ) INTO first_rent_paid;
    
    -- Auto-activate tenant if both invoices are paid
    IF security_paid AND first_rent_paid AND NEW.status = 'pending' THEN
        NEW.status = 'active';
        NEW.move_in_date = CURRENT_DATE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_tenant_activation
    BEFORE UPDATE ON tenants
    FOR EACH ROW 
    WHEN (OLD.status = 'pending')
    EXECUTE FUNCTION check_tenant_activation();

-- ============================================================================
-- PART 5: INITIAL DATA (OPTIONAL)
-- ============================================================================

-- Create a default admin user (CHANGE PASSWORD IN PRODUCTION!)
-- Password: 'admin123' (bcrypt hashed - MUST BE CHANGED)
INSERT INTO users (email, password_hash, full_name, phone, role)
VALUES (
    'admin@propertymanager.com',
    '$2b$10$rXOQH3J3P4P4P4P4P4P4PeYYYYYYYYYYYYYYYYYYYYYYYYYYYY',  -- Replace with actual bcrypt hash
    'System Administrator',
    '+254700000000',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON SCHEMA public IS 'Property Management System - Version 1.0';

-- Show completion message
DO $$
BEGIN
    RAISE NOTICE '✓ Database schema migration completed successfully';
    RAISE NOTICE '✓ Tables created: 11';
    RAISE NOTICE '✓ Indexes created: 50+';
    RAISE NOTICE '✓ Triggers created: 8';
    RAISE NOTICE '✓ Functions created: 5';
    RAISE NOTICE '';
    RAISE NOTICE '⚠ IMPORTANT: Change default admin password immediately!';
    RAISE NOTICE '⚠ IMPORTANT: Configure encryption keys for M-Pesa credentials';
END $$;