import api from './api';
import type { Payment } from '../types';

export const paymentService = {
  /**
   * Get all payments
   */
  async getAll(status?: string): Promise<Payment[]> {
    try {
      console.log('🔍 Payment Service: Fetching payments with status:', status || 'all');
      const params: any = {};
      if (status) params.status = status;
      
      const { data } = await api.get('/payments', { params });
      console.log('📦 Payment Service: Raw API response:', data);
      
      // Backend might return array directly or wrapped in object
      let payments: Payment[] = [];
      
      if (Array.isArray(data)) {
        console.log('✅ Response is direct array');
        payments = data;
      } else if (data.payments && Array.isArray(data.payments)) {
        console.log('✅ Response has payments property');
        payments = data.payments;
      } else if (data.data && Array.isArray(data.data)) {
        console.log('✅ Response has data property');
        payments = data.data;
      } else {
        console.warn('⚠️ Unexpected payments response format:', data);
        payments = [];
      }
      
      console.log(`✅ Payment Service: Returning ${payments.length} payments`);
      return payments;
    } catch (error) {
      console.error('❌ Payment Service: Error fetching payments:', error);
      return [];
    }
  },

  /**
   * Get single payment
   */
  async getById(id: string): Promise<Payment> {
    const { data } = await api.get(`/payments/${id}`);
    return data;
  },

  /**
   * Manually match payment to invoice
   */
  async matchToInvoice(paymentId: string, invoiceId: string): Promise<any> {
    const { data } = await api.post(`/payments/${paymentId}/match`, {
      invoice_id: invoiceId,
    });
    return data;
  },

  /**
   * Get unmatched payments
   */
  async getUnmatched(): Promise<Payment[]> {
    return this.getAll('unmatched');
  },

  /**
   * Get matched payments
   */
  async getMatched(): Promise<Payment[]> {
    return this.getAll('matched');
  },
};