import api from './api';

export const exportService = {
  /**
   * Export tenants to PDF
   */
  async exportTenantsPDF(propertyId?: string, status?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (propertyId) params.append('property_id', propertyId);
    if (status) params.append('status', status);

    const { data } = await api.get(`/export/tenants/pdf?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Export tenants to Excel
   */
  async exportTenantsExcel(propertyId?: string, status?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (propertyId) params.append('property_id', propertyId);
    if (status) params.append('status', status);

    const { data } = await api.get(`/export/tenants/excel?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Export payments to PDF
   */
  async exportPaymentsPDF(
    startDate?: string,
    endDate?: string,
    propertyId?: string
  ): Promise<Blob> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (propertyId) params.append('property_id', propertyId);

    const { data } = await api.get(`/export/payments/pdf?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Export payments to Excel
   */
  async exportPaymentsExcel(
    startDate?: string,
    endDate?: string,
    propertyId?: string
  ): Promise<Blob> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (propertyId) params.append('property_id', propertyId);

    const { data } = await api.get(`/export/payments/excel?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Export invoices to PDF
   */
  async exportInvoicesPDF(status?: string, propertyId?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (propertyId) params.append('property_id', propertyId);

    const { data } = await api.get(`/export/invoices/pdf?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Export invoices to Excel
   */
  async exportInvoicesExcel(status?: string, propertyId?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (propertyId) params.append('property_id', propertyId);

    const { data } = await api.get(`/export/invoices/excel?${params.toString()}`, {
      responseType: 'blob',
    });
    return data;
  },

  /**
   * Download blob as file
   */
  downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};