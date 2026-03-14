import React, { useEffect, useState } from 'react';
import { Home, Plus, Edit, Trash2, Bed, Bath, DollarSign, Maximize } from 'lucide-react';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Badge } from '../components/common/Badge';
import { unitService } from '../services/unit.service';
import { propertyService } from '../services/property.service';
import type { Unit, Property } from '../types';
import { formatCurrency } from '../utils/formatters';
import toast from 'react-hot-toast';

interface UnitFormData {
  property_id: string;
  unit_number: string;
  bedrooms: number;
  bathrooms: number;
  size_sqm?: number;
  base_rent: number;
}

export const Units: React.FC = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState<Unit | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<string>('');
  const [formData, setFormData] = useState<UnitFormData>({
    property_id: '',
    unit_number: '',
    bedrooms: 1,
    bathrooms: 1,
    size_sqm: undefined,
    base_rent: 0,
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProperties();
    fetchUnits();
  }, []);

  useEffect(() => {
    if (selectedProperty) {
      fetchUnits(selectedProperty);
    } else {
      fetchUnits();
    }
  }, [selectedProperty]);

  const fetchProperties = async () => {
    try {
      const data = await propertyService.getAll();
      setProperties(data);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const fetchUnits = async (propertyId?: string) => {
    try {
      setLoading(true);
      const data = await unitService.getAll(propertyId);
      setUnits(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching units:', error);
      toast.error('Failed to load units');
      setUnits([]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (unit?: Unit) => {
    if (unit) {
      setEditingUnit(unit);
      setFormData({
        property_id: unit.property_id,
        unit_number: unit.unit_number,
        bedrooms: unit.bedrooms,
        bathrooms: unit.bathrooms,
        size_sqm: unit.size_sqm,
        base_rent: unit.base_rent,
      });
    } else {
      setEditingUnit(null);
      setFormData({
        property_id: selectedProperty || '',
        unit_number: '',
        bedrooms: 1,
        bathrooms: 1,
        size_sqm: undefined,
        base_rent: 0,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingUnit(null);
    setFormData({
      property_id: '',
      unit_number: '',
      bedrooms: 1,
      bathrooms: 1,
      size_sqm: undefined,
      base_rent: 0,
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'bedrooms' || name === 'bathrooms' || name === 'size_sqm' || name === 'base_rent'
        ? parseFloat(value) || 0
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (editingUnit) {
        await unitService.update(editingUnit.id, formData);
        toast.success('Unit updated successfully!');
      } else {
        await unitService.create(formData);
        toast.success('Unit created successfully!');
      }
      
      handleCloseModal();
      await fetchUnits(selectedProperty || undefined);
    } catch (error: any) {
      console.error('Submit error:', error);
      const message = error.response?.data?.detail || 'Failed to save unit';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (unit: Unit) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete unit "${unit.unit_number}"?\n\nThis will also remove any associated tenants.`
    );
    
    if (!confirmed) return;

    try {
      await unitService.delete(unit.id);
      toast.success('Unit deleted successfully!');
      await fetchUnits(selectedProperty || undefined);
    } catch (error: any) {
      console.error('Delete error:', error);
      const message = error.response?.data?.detail || 'Failed to delete unit';
      toast.error(message);
    }
  };

  const getPropertyName = (propertyId: string) => {
    const property = properties.find(p => p.id === propertyId);
    return property?.name || 'Unknown Property';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Units</h1>
              <p className="text-gray-600 mt-1">
                Manage rental units across all properties
              </p>
            </div>
            <Button 
              onClick={() => handleOpenModal()}
              variant="primary"
            >
              <Plus className="w-4 h-4" />
              Add Unit
            </Button>
          </div>

          {/* Filter */}
          {properties.length > 0 && (
            <div className="mt-4">
              <select
                value={selectedProperty}
                onChange={(e) => setSelectedProperty(e.target.value)}
                className="input max-w-xs"
              >
                <option value="">All Properties</option>
                {properties.map((property) => (
                  <option key={property.id} value={property.id}>
                    {property.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {units.length === 0 ? (
          <Card>
            <EmptyState
              icon={Home}
              title="No units yet"
              description={
                properties.length === 0
                  ? "You need to add a property first before creating units."
                  : "Get started by adding units to your properties."
              }
              actionLabel={properties.length > 0 ? "Add Your First Unit" : undefined}
              onAction={properties.length > 0 ? () => handleOpenModal() : undefined}
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {units.map((unit) => (
              <Card key={unit.id} hover className="relative">
                <CardContent>
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Home className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">
                          Unit {unit.unit_number}
                        </h3>
                        <p className="text-xs text-gray-500">
                          {getPropertyName(unit.property_id)}
                        </p>
                      </div>
                    </div>
                    <Badge variant={unit.is_available ? 'success' : 'danger'}>
                      {unit.is_available ? 'Available' : 'Occupied'}
                    </Badge>
                  </div>

                  {/* Details */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Bed className="w-4 h-4" />
                      <span>{unit.bedrooms} Bedroom{unit.bedrooms !== 1 ? 's' : ''}</span>
                      <span className="text-gray-400">•</span>
                      <Bath className="w-4 h-4" />
                      <span>{unit.bathrooms} Bath{unit.bathrooms !== 1 ? 's' : ''}</span>
                    </div>

                    {unit.size_sqm && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Maximize className="w-4 h-4" />
                        <span>{unit.size_sqm} m²</span>
                      </div>
                    )}

                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span>{formatCurrency(unit.base_rent)}/month</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenModal(unit)}
                      className="flex-1"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(unit)}
                      className="text-red-600 hover:bg-red-50 flex-1"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Add/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingUnit ? 'Edit Unit' : 'Add New Unit'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Property */}
          <div>
            <label htmlFor="property_id" className="label">
              Property <span className="text-red-500">*</span>
            </label>
            <select
              id="property_id"
              name="property_id"
              value={formData.property_id}
              onChange={handleInputChange}
              className="input"
              required
              disabled={!!editingUnit}
            >
              <option value="">Select a property</option>
              {properties.map((property) => (
                <option key={property.id} value={property.id}>
                  {property.name}
                </option>
              ))}
            </select>
          </div>

          {/* Unit Number */}
          <div>
            <label htmlFor="unit_number" className="label">
              Unit Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="unit_number"
              name="unit_number"
              value={formData.unit_number}
              onChange={handleInputChange}
              className="input"
              placeholder="e.g., A1, 101, 1B"
              required
              autoFocus
            />
          </div>

          {/* Bedrooms & Bathrooms */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="bedrooms" className="label">
                Bedrooms <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="bedrooms"
                name="bedrooms"
                value={formData.bedrooms}
                onChange={handleInputChange}
                className="input"
                min="0"
                required
              />
            </div>
            <div>
              <label htmlFor="bathrooms" className="label">
                Bathrooms <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="bathrooms"
                name="bathrooms"
                value={formData.bathrooms}
                onChange={handleInputChange}
                className="input"
                min="0"
                step="0.5"
                required
              />
            </div>
          </div>

          {/* Size */}
          <div>
            <label htmlFor="size_sqm" className="label">
              Size (m²)
            </label>
            <input
              type="number"
              id="size_sqm"
              name="size_sqm"
              value={formData.size_sqm || ''}
              onChange={handleInputChange}
              className="input"
              placeholder="Optional"
              min="0"
            />
          </div>

          {/* Base Rent */}
          <div>
            <label htmlFor="base_rent" className="label">
              Monthly Rent (KES) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="base_rent"
              name="base_rent"
              value={formData.base_rent}
              onChange={handleInputChange}
              className="input"
              placeholder="e.g., 25000"
              min="0"
              required
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={handleCloseModal}
              className="flex-1"
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={submitting}
              disabled={submitting}
              className="flex-1"
            >
              {editingUnit ? 'Update Unit' : 'Create Unit'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};