import api from './api';

export const reportService = {
  /**
   * Get revenue report
   */
  async getRevenue(startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const { data } = await api.get('/reports/revenue', { params });
      return data;
    } catch (error) {
      console.error('Error fetching revenue report:', error);
      return null;
    }
  },

  /**
   * Get occupancy report
   */
  async getOccupancy(startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const { data } = await api.get('/reports/occupancy', { params });
      return data;
    } catch (error) {
      console.error('Error fetching occupancy report:', error);
      return null;
    }
  },

  /**
   * Get payment analytics
   */
  async getPaymentAnalytics(): Promise<any> {
    try {
      const { data } = await api.get('/reports/payment-analytics');
      return data;
    } catch (error) {
      console.error('Error fetching payment analytics:', error);
      return null;
    }
  },

  /**
   * Get property performance
   */
  async getPropertyPerformance(): Promise<any> {
    try {
      const { data } = await api.get('/reports/property-performance');
      return data;
    } catch (error) {
      console.error('Error fetching property performance:', error);
      return [];
    }
  },
};