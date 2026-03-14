import api from './api';
import type { Unit } from '../types';

export const unitService = {
  /**
   * Get all units (across all properties or for specific property)
   */
  async getAll(propertyId?: string, availableOnly?: boolean): Promise<Unit[]> {
    try {
      if (propertyId) {
        // Get units for specific property
        const params: any = {};
        if (availableOnly !== undefined) params.available_only = availableOnly;
        
        const { data } = await api.get(`/properties/${propertyId}/units`, { params });
        return Array.isArray(data) ? data : [];
      } else {
        // Get all units across all properties
        // We need to fetch all properties first, then get their units
        const propertiesResponse = await api.get('/properties');
        const properties = propertiesResponse.data.properties || propertiesResponse.data;
        
        if (!Array.isArray(properties) || properties.length === 0) {
          return [];
        }
        
        // Fetch units for each property
        const unitsPromises = properties.map((prop: any) => 
          api.get(`/properties/${prop.id}/units`)
            .then(res => res.data)
            .catch(() => [])
        );
        
        const allUnitsArrays = await Promise.all(unitsPromises);
        const allUnits = allUnitsArrays.flat();
        
        return Array.isArray(allUnits) ? allUnits : [];
      }
    } catch (error) {
      console.error('Error in unitService.getAll:', error);
      return [];
    }
  },

  /**
   * Get single unit
   */
  async getById(id: string): Promise<Unit> {
    const { data } = await api.get(`/units/${id}`);
    return data;
  },

  /**
   * Create new unit
   */
  async create(unit: any): Promise<Unit> {
    const { data } = await api.post('/units', unit);
    return data;
  },

  /**
   * Update unit
   */
  async update(id: string, unit: any): Promise<Unit> {
    const { data } = await api.put(`/units/${id}`, unit);
    return data;
  },

  /**
   * Delete unit
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/units/${id}`);
  },
};