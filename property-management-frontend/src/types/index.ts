export interface User {
    id: string;
    email: string;
    full_name: string;
    phone: string;
    role: string;
  }
  
  export interface Property {
    id: string;
    name: string;
    address: string;
    description?: string;
    created_at: string;
  }
  
  export interface Unit {
    id: string;
    property_id: string;
    unit_number: string;
    bedrooms: number;
    bathrooms: number;
    base_rent: number;
    is_available: boolean;
  }
  
  export interface Tenant {
    id: string;
    unit_id: string;
    property_id: string;
    full_name: string;
    phone: string;
    email?: string;
    base_rent: number;
    security_deposit_amount: number;
    security_deposit_paid: boolean;
    move_in_date?: string;
    status: 'pending' | 'active' | 'moved_out';
  }
  
  export interface Invoice {
    id: string;
    tenant_id: string;
    invoice_number: string;
    invoice_type: 'monthly_rent' | 'security_deposit';
    amount: number;
    paid_amount: number;
    due_date: string;
    status: 'unpaid' | 'partially_paid' | 'paid' | 'overdue';
  }
  
  export interface Payment {
    id: string;
    trans_id: string;
    amount: number;
    trans_time: string;
    status: 'matched' | 'unmatched';
    tenant_id?: string;
    invoice_id?: string;
  }
  
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