// User & Authentication
export interface User {
    id: string;
    email: string;
    full_name: string;
    phone: string;
    role: string;
    is_active: boolean;
    created_at: string;
  }
  
  export interface LoginRequest {
    username: string;
    password: string;
  }
  
  export interface RegisterRequest {
    email: string;
    full_name: string;
    phone: string;
    password: string;
  }
  
  export interface AuthResponse {
    access_token: string;
    token_type: string;
  }
  
  // Property
  export interface Property {
    id: string;
    landlord_id: string;
    name: string;
    address: string;
    description?: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface PropertyCreate {
    name: string;
    address: string;
    description?: string;
  }
  
  // Unit
  export interface Unit {
    id: string;
    property_id: string;
    unit_number: string;
    bedrooms: number;
    bathrooms: number;
    size_sqm?: number;
    base_rent: number;
    is_available: boolean;
    created_at: string;
  }
  
  export interface UnitCreate {
    property_id: string;
    unit_number: string;
    bedrooms: number;
    bathrooms: number;
    size_sqm?: number;
    base_rent: number;
  }
  
  // Tenant
  export interface Tenant {
    id: string;
    unit_id: string;
    property_id: string;
    full_name: string;
    phone: string;
    email?: string;
    id_number?: string;
    base_rent: number;
    security_deposit_amount: number;
    security_deposit_paid: boolean;
    security_deposit_paid_date?: string;
    move_in_date?: string;
    move_out_date?: string;
    status: 'pending' | 'active' | 'moved_out';
    created_at: string;
  }
  
  export interface TenantCreate {
    unit_id: string;
    property_id: string;
    full_name: string;
    phone: string;
    email?: string;
    id_number?: string;
    base_rent: number;
    security_deposit_amount: number;
    move_in_date?: string;
  }
  
  // Invoice
  export interface Invoice {
    id: string;
    tenant_id: string;
    property_id: string;
    unit_id: string;
    invoice_number: string;
    invoice_type: 'monthly_rent' | 'security_deposit';
    amount: number;
    paid_amount: number;
    credit_applied: number;
    due_date: string;
    month?: number;
    year?: number;
    status: 'unpaid' | 'partially_paid' | 'paid' | 'overdue';
    created_at: string;
  }
  
  // Payment
  export interface Payment {
    id: string;
    trans_id: string;
    amount: number;
    msisdn?: string;
    paybill_shortcode?: string;
    bill_ref_number?: string;
    first_name?: string;
    last_name?: string;
    trans_time?: string;
    payment_method: string;
    status: 'matched' | 'unmatched' | 'duplicate' | 'failed';
    matched_at?: string;
    invoice_id?: string;
    tenant_id?: string;
    property_id?: string;
    created_at: string;
  }
  
  // Dashboard
  export interface DashboardStats {
    properties: number;
    units: {
      total: number;
      occupied: number;
      vacant: number;
      occupancy_rate: number;
    };
    tenants: {
      active: number;
    };
    revenue: {
      this_month: number;
    };
    arrears: {
      total: number;
    };
  }
  
  // Reports
  export interface RevenueReport {
    summary: {
      total_revenue: number;
      payment_count: number;
      period: {
        start?: string;
        end?: string;
      };
    };
    by_property: Array<{
      property_name: string;
      property_id: string;
      revenue: number;
    }>;
    recent_payments: Array<{
      trans_id: string;
      amount: number;
      date?: string;
      tenant_id?: string;
    }>;
  }
  
  export interface OccupancyReport {
    summary: {
      total_units: number;
      occupied_units: number;
      vacant_units: number;
      occupancy_rate: number;
      total_tenants: number;
      potential_monthly_rent: number;
      actual_monthly_rent: number;
    };
    by_property: Array<{
      property_id: string;
      property_name: string;
      total_units: number;
      occupied_units: number;
      vacant_units: number;
      occupancy_rate: number;
      potential_monthly_rent: number;
      actual_monthly_rent: number;
      vacancy_loss: number;
    }>;
  }
  
  export interface ArrearsReport {
    summary: {
      total_arrears: number;
      total_overdue: number;
      total_unpaid_invoices: number;
      total_overdue_invoices: number;
      tenants_in_arrears: number;
    };
    tenants: Array<{
      tenant_id: string;
      tenant_name: string;
      phone: string;
      unit_number: string;
      total_arrears: number;
      invoices: Array<{
        invoice_number: string;
        invoice_type: string;
        amount: number;
        paid: number;
        balance: number;
        due_date: string;
        status: string;
      }>;
    }>;
  }
  
  // API Response
  export interface ApiResponse<T> {
    data: T;
    message?: string;
  }
  
  export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
  }