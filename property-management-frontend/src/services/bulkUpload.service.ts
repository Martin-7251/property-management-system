import api from './api';

export const bulkUploadService = {
  /**
   * Upload properties CSV
   */
  async uploadProperties(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post('/bulk/properties', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  /**
   * Upload units CSV
   */
  async uploadUnits(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post('/bulk/units', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  /**
   * Upload tenants CSV
   */
  async uploadTenants(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post('/bulk/tenants', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  /**
   * Download CSV template
   */
  downloadTemplate(type: 'properties' | 'units' | 'tenants'): void {
    const templates = {
      properties: `name,address,type,total_units
Sunset Apartments,123 Main Street,apartment,10
Green Valley Estate,456 Oak Avenue,house,5
Downtown Plaza,789 Center Street,commercial,20`,
      
      units: `property_name,unit_number,bedrooms,bathrooms,rent_amount,status
Sunset Apartments,A101,2,1,25000,vacant
Sunset Apartments,A102,3,2,35000,vacant
Green Valley Estate,H1,4,3,50000,vacant`,
      
      tenants: `property_name,unit_number,full_name,phone,email,id_number,base_rent,security_deposit_amount,move_in_date
Sunset Apartments,A101,John Doe,+254722123456,john@email.com,12345678,25000,25000,2024-01-01
Sunset Apartments,A102,Jane Smith,+254733987654,jane@email.com,87654321,35000,35000,2024-01-15
Green Valley Estate,H1,Bob Johnson,+254744555666,bob@email.com,11223344,50000,50000,2024-02-01`
    };

    const content = templates[type];
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${type}_template.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};