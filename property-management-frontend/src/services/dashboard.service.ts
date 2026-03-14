import api from './api';
import { DashboardStats } from '../types';

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>('/reports/dashboard');
    return data;
  },
};