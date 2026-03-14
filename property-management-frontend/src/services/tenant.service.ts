import api from './api';
import type { Tenant } from '../types';

export const tenantService = {
  /**
   * Get all tenants
   */
  async getAll(propertyId?: string): Promise<Tenant[]> {
    try {
      const params: any = {};
      if (propertyId) params.property_id = propertyId;
      
      const { data } = await api.get('/tenants', { params });
      return Array.isArray(data) ? data : (data.tenants || []);
    } catch (error) {
      console.error('Error fetching tenants:', error);
      return [];
    }
  },

  /**
   * Get single tenant
   */
  async getById(id: string): Promise<Tenant> {
    const { data } = await api.get(`/tenants/${id}`);
    return data;
  },

  /**
   * Create new tenant
   */
  async create(tenant: any): Promise<Tenant> {
    const { data } = await api.post('/tenants', tenant);
    return data;
  },

  /**
   * Update tenant
   */
  async update(id: string, tenant: any): Promise<Tenant> {
    const { data } = await api.put(`/tenants/${id}`, tenant);
    return data;
  },

  /**
   * Move out tenant
   */
  async moveOut(id: string, moveOutData: any): Promise<any> {
    const { data } = await api.post(`/tenants/${id}/move-out`, moveOutData);
    return data;
  },

  /**
   * Get tenant invoices
   */
  async getInvoices(id: string): Promise<any[]> {
    const { data } = await api.get(`/tenants/${id}/invoices`);
    return Array.isArray(data) ? data : [];
  },

  /**
   * Delete tenant
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/tenants/${id}`);
  },
};