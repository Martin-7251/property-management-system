import api from './api';
import type { Invoice } from '../types';

export const invoiceService = {
  /**
   * Get all invoices
   */
  async getAll(propertyId?: string, status?: string): Promise<Invoice[]> {
    try {
      const params: any = {};
      if (propertyId) params.property_id = propertyId;
      if (status) params.status = status;
      
      const { data } = await api.get('/invoices', { params });
      return Array.isArray(data) ? data : (data.invoices || []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      return [];
    }
  },

  /**
   * Get single invoice
   */
  async getById(id: string): Promise<Invoice> {
    const { data } = await api.get(`/invoices/${id}`);
    return data;
  },

  /**
   * Update invoice
   */
  async update(id: string, invoice: any): Promise<Invoice> {
    const { data } = await api.put(`/invoices/${id}`, invoice);
    return data;
  },

  /**
   * Get unpaid summary
   */
  async getUnpaidSummary(propertyId?: string): Promise<any> {
    const params: any = {};
    if (propertyId) params.property_id = propertyId;
    
    const { data } = await api.get('/invoices/unpaid/summary', { params });
    return data;
  },
};