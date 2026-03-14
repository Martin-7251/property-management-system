import React, { useEffect, useState } from 'react';
import { Building2, Plus, Edit, Trash2, MapPin } from 'lucide-react';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { propertyService } from '../services/property.service';
import type { Property } from '../types';
import { formatDate } from '../utils/formatters';
import toast from 'react-hot-toast';

interface PropertyFormData {
  name: string;
  address: string;
  description?: string;
}

export const Properties: React.FC = () => {
  console.log('Properties component rendering'); // Debug
  
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProperty, setEditingProperty] = useState<Property | null>(null);
  const [formData, setFormData] = useState<PropertyFormData>({
    name: '',
    address: '',
    description: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    console.log('Fetching properties...'); // Debug
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      console.log('Fetching properties from API...');
      const data = await propertyService.getAll();
      console.log('API Response:', data);
      
      // Ensure data is an array
      if (Array.isArray(data)) {
        setProperties(data);
      } else {
        console.error('API did not return an array:', data);
        setProperties([]);
        toast.error('Unexpected response format from server');
      }
    } catch (error) {
      console.error('Error fetching properties:', error);
      toast.error('Failed to load properties');
      setProperties([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (property?: Property) => {
    console.log('Opening modal', property); // Debug log
    if (property) {
      setEditingProperty(property);
      setFormData({
        name: property.name,
        address: property.address,
        description: property.description || '',
      });
    } else {
      setEditingProperty(null);
      setFormData({
        name: '',
        address: '',
        description: '',
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProperty(null);
    setFormData({
      name: '',
      address: '',
      description: '',
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submitting form:', formData); // Debug log
    setSubmitting(true);

    try {
      if (editingProperty) {
        // Update
        const updated = await propertyService.update(editingProperty.id, formData);
        console.log('Updated:', updated);
        toast.success('Property updated successfully!');
      } else {
        // Create
        const created = await propertyService.create(formData);
        console.log('Created:', created);
        toast.success('Property created successfully!');
      }
      
      handleCloseModal();
      await fetchProperties(); // Refresh list
    } catch (error: any) {
      console.error('Submit error:', error);
      const message = error.response?.data?.detail || 'Failed to save property';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (property: Property) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${property.name}"?\n\nThis will also delete all units and tenants in this property.`
    );
    
    if (!confirmed) return;

    try {
      await propertyService.delete(property.id);
      toast.success('Property deleted successfully!');
      await fetchProperties(); // Refresh list
    } catch (error: any) {
      console.error('Delete error:', error);
      const message = error.response?.data?.detail || 'Failed to delete property';
      toast.error(message);
    }
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
              <h1 className="text-3xl font-bold text-gray-900">Properties</h1>
              <p className="text-gray-600 mt-1">
                Manage your buildings and properties
              </p>
            </div>
            <Button 
              onClick={() => handleOpenModal()}
              variant="primary"
            >
              <Plus className="w-4 h-4" />
              Add Property
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {properties.length === 0 ? (
          <Card>
            <EmptyState
              icon={Building2}
              title="No properties yet"
              description="Get started by adding your first property. You can then add units and tenants to each property."
              actionLabel="Add Your First Property"
              onAction={() => handleOpenModal()}
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <Card key={property.id} hover className="relative">
                <CardContent>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">
                          {property.name}
                        </h3>
                        <p className="text-xs text-gray-500">
                          Added {formatDate(property.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-2 text-sm text-gray-600 mb-4">
                    <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span>{property.address}</span>
                  </div>

                  {property.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {property.description}
                    </p>
                  )}

                  <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenModal(property)}
                      className="flex-1"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(property)}
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
        title={editingProperty ? 'Edit Property' : 'Add New Property'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="label">
              Property Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="input"
              placeholder="e.g., Sunset Apartments"
              required
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="address" className="label">
              Address <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              className="input"
              placeholder="e.g., 123 Kilimani Road, Nairobi"
              required
            />
          </div>

          <div>
            <label htmlFor="description" className="label">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="input resize-none"
              rows={3}
              placeholder="Optional description..."
            />
          </div>

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
              {editingProperty ? 'Update Property' : 'Create Property'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};