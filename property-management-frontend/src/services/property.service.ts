import api from './api';
import { Property, PropertyCreate } from '../types';

/**
 * Backend list response shape
 */
interface PropertyListResponse {
  total: number;
  properties: Property[];
}

export const propertyService = {
  /**
   * Get all properties
   * Backend returns: { total: number, properties: Property[] }
   * We return only Property[] to keep components clean.
   */
  async getAll(): Promise<Property[]> {
    const { data } = await api.get<PropertyListResponse>('/properties');
    return data.properties;
  },

  /**
   * Get single property
   */
  async getById(id: string): Promise<Property> {
    const { data } = await api.get<Property>(`/properties/${id}`);
    return data;
  },

  /**
   * Create new property
   */
  async create(property: PropertyCreate): Promise<Property> {
    const { data } = await api.post<Property>('/properties', property);
    return data;
  },

  /**
   * Update property
   */
  async update(
    id: string,
    property: Partial<PropertyCreate>
  ): Promise<Property> {
    const { data } = await api.put<Property>(`/properties/${id}`, property);
    return data;
  },

  /**
   * Delete property
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/properties/${id}`);
  },

  /**
   * Get property summary
   */
  async getSummary(id: string): Promise<any> {
    const { data } = await api.get(`/properties/${id}/summary`);
    return data;
  },
};