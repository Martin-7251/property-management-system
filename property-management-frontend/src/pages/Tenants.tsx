import React, { useEffect, useState } from 'react';
import { Users, Plus, UserX, Mail, Phone, Home, Calendar, DollarSign, Trash2 } from 'lucide-react';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Badge } from '../components/common/Badge';
import { ExportButton } from '../components/common/ExportButton';
import { tenantService } from '../services/tenant.service';
import { propertyService } from '../services/property.service';
import { unitService } from '../services/unit.service';
import { exportService } from '../services/export.service';
import type { Tenant, Property, Unit } from '../types';
import { formatCurrency, formatDate, getInitials } from '../utils/formatters';
import toast from 'react-hot-toast';

interface TenantFormData {
  unit_id: string;
  property_id: string;
  full_name: string;
  phone: string;
  email?: string;
  id_number?: string;
  base_rent: number;
  security_deposit_amount: number;
  move_in_date?: string;
}

export const Tenants: React.FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [formData, setFormData] = useState<TenantFormData>({
    unit_id: '',
    property_id: '',
    full_name: '',
    phone: '',
    email: '',
    id_number: '',
    base_rent: 0,
    security_deposit_amount: 0,
    move_in_date: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProperties();
    fetchTenants();
  }, []);

  useEffect(() => {
    if (selectedProperty) {
      fetchTenants(selectedProperty);
    } else {
      fetchTenants();
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

  const fetchTenants = async (propertyId?: string) => {
    try {
      setLoading(true);
      const data = await tenantService.getAll(propertyId);
      setTenants(data);
    } catch (error) {
      console.error('Error fetching tenants:', error);
      toast.error('Failed to load tenants');
      setTenants([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchUnitsForProperty = async (propertyId: string) => {
    try {
      const data = await unitService.getAll(propertyId, true); // Only available units
      setUnits(data);
    } catch (error) {
      console.error('Error fetching units:', error);
      setUnits([]);
    }
  };

  const handleOpenModal = () => {
    setFormData({
      unit_id: '',
      property_id: '',
      full_name: '',
      phone: '',
      email: '',
      id_number: '',
      base_rent: 0,
      security_deposit_amount: 0,
      move_in_date: '',
    });
    setUnits([]);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({
      unit_id: '',
      property_id: '',
      full_name: '',
      phone: '',
      email: '',
      id_number: '',
      base_rent: 0,
      security_deposit_amount: 0,
      move_in_date: '',
    });
    setUnits([]);
  };

  const handlePropertyChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const propertyId = e.target.value;
    setFormData(prev => ({
      ...prev,
      property_id: propertyId,
      unit_id: '',
      base_rent: 0,
      security_deposit_amount: 0,
    }));

    if (propertyId) {
      await fetchUnitsForProperty(propertyId);
    } else {
      setUnits([]);
    }
  };

  const handleUnitChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const unitId = e.target.value;
    const selectedUnit = units.find(u => u.id === unitId);
    
    setFormData(prev => ({
      ...prev,
      unit_id: unitId,
      base_rent: selectedUnit?.base_rent || 0,
      security_deposit_amount: selectedUnit?.base_rent || 0, // Default deposit = 1 month rent
    }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'base_rent' || name === 'security_deposit_amount'
        ? parseFloat(value) || 0
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await tenantService.create(formData);
      toast.success('Tenant registered successfully! Invoices created automatically.');
      handleCloseModal();
      await fetchTenants(selectedProperty || undefined);
    } catch (error: any) {
      console.error('Submit error:', error);
      const message = error.response?.data?.detail || 'Failed to register tenant';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleMoveOut = async (tenant: Tenant) => {
    const confirmed = window.confirm(
      `Move out ${tenant.full_name}?\n\nThis will:\n- Calculate final bills\n- Process security deposit refund\n- Mark unit as available`
    );
    
    if (!confirmed) return;

    try {
      await tenantService.moveOut(tenant.id, {
        move_out_date: new Date().toISOString().split('T')[0],
        damages_amount: 0,
        other_charges: 0,
      });
      toast.success('Tenant moved out successfully!');
      await fetchTenants(selectedProperty || undefined);
    } catch (error: any) {
      console.error('Move out error:', error);
      const message = error.response?.data?.detail || 'Failed to process move-out';
      toast.error(message);
    }
  };

  const handleDelete = async (tenant: Tenant) => {
    if (!window.confirm(`Are you sure you want to permanently delete ${tenant.full_name}?\n\nThis will:\n- Remove the tenant record\n- Delete all associated invoices\n- Delete payment history\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      await tenantService.delete(tenant.id);
      toast.success('Tenant deleted successfully');
      await fetchTenants(selectedProperty || undefined);
    } catch (error: any) {
      console.error('Delete error:', error);
      const message = error.response?.data?.detail || 'Failed to delete tenant';
      toast.error(message);
    }
  };

  const getPropertyName = (propertyId: string) => {
    const property = properties.find(p => p.id === propertyId);
    return property?.name || 'Unknown';
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      active: 'success',
      pending: 'warning',
      moved_out: 'gray',
    };
    return <Badge variant={variants[status] || 'gray'}>{status.replace('_', ' ')}</Badge>;
  };

  const filteredTenants = selectedStatus
    ? tenants.filter(t => t.status === selectedStatus)
    : tenants;

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
              <h1 className="text-3xl font-bold text-gray-900">Tenants</h1>
              <p className="text-gray-600 mt-1">
                Manage tenants and their rental agreements
              </p>
            </div>
            <div className="flex gap-3">
              {tenants.length > 0 && (
                <ExportButton
                  onExportPDF={() => exportService.exportTenantsPDF(selectedProperty, selectedStatus)}
                  onExportExcel={() => exportService.exportTenantsExcel(selectedProperty, selectedStatus)}
                  pdfFilename={`tenants_${new Date().toISOString().split('T')[0]}.pdf`}
                  excelFilename={`tenants_${new Date().toISOString().split('T')[0]}.xlsx`}
                />
              )}
              <Button 
                onClick={handleOpenModal}
                variant="primary"
                disabled={properties.length === 0}
              >
                <Plus className="w-4 h-4" />
                Register Tenant
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className="mt-4 flex gap-4">
            {properties.length > 0 && (
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
            )}

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="input max-w-xs"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="moved_out">Moved Out</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredTenants.length === 0 ? (
          <Card>
            <EmptyState
              icon={Users}
              title="No tenants yet"
              description={
                properties.length === 0
                  ? "You need to add properties and units first before registering tenants."
                  : "Get started by registering your first tenant."
              }
              actionLabel={properties.length > 0 ? "Register Your First Tenant" : undefined}
              onAction={properties.length > 0 ? handleOpenModal : undefined}
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTenants.map((tenant) => (
              <Card key={tenant.id} hover>
                <CardContent>
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <span className="text-purple-600 font-semibold text-lg">
                          {getInitials(tenant.full_name)}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {tenant.full_name}
                        </h3>
                        <p className="text-xs text-gray-500">
                          {getPropertyName(tenant.property_id)}
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(tenant.status)}
                  </div>

                  {/* Contact Info */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Phone className="w-4 h-4" />
                      <span>{tenant.phone}</span>
                    </div>
                    {tenant.email && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Mail className="w-4 h-4" />
                        <span className="truncate">{tenant.email}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Home className="w-4 h-4" />
                      <span>Unit {tenant.unit_id}</span>
                    </div>
                  </div>

                  {/* Financial Info */}
                  <div className="space-y-2 mb-4 pt-3 border-t border-gray-100">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Monthly Rent</span>
                      <span className="font-semibold">{formatCurrency(tenant.base_rent)}</span>
                    </div>
                    {tenant.move_in_date && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Move-in</span>
                        <span className="font-semibold">{formatDate(tenant.move_in_date)}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {tenant.status === 'active' && (
                    <div className="pt-3 border-t border-gray-100">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMoveOut(tenant)}
                        className="text-red-600 hover:bg-red-50 w-full"
                      >
                        <UserX className="w-4 h-4" />
                        Move Out
                      </Button>
                    </div>
                  )}
                  
                  {tenant.status === 'moved_out' && (
                    <div className="pt-3 border-t border-gray-100">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(tenant)}
                        className="text-red-600 hover:bg-red-50 w-full"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete Tenant
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Add Tenant Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Register New Tenant"
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Property Selection */}
          <div>
            <label htmlFor="property_id" className="label">
              Property <span className="text-red-500">*</span>
            </label>
            <select
              id="property_id"
              value={formData.property_id}
              onChange={handlePropertyChange}
              className="input"
              required
            >
              <option value="">Select a property</option>
              {properties.map((property) => (
                <option key={property.id} value={property.id}>
                  {property.name}
                </option>
              ))}
            </select>
          </div>

          {/* Unit Selection */}
          <div>
            <label htmlFor="unit_id" className="label">
              Unit <span className="text-red-500">*</span>
            </label>
            <select
              id="unit_id"
              value={formData.unit_id}
              onChange={handleUnitChange}
              className="input"
              required
              disabled={!formData.property_id || units.length === 0}
            >
              <option value="">
                {!formData.property_id 
                  ? 'Select property first' 
                  : units.length === 0 
                    ? 'No available units' 
                    : 'Select a unit'}
              </option>
              {units.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  Unit {unit.unit_number} - {formatCurrency(unit.base_rent)}/month
                </option>
              ))}
            </select>
          </div>

          {/* Personal Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label htmlFor="full_name" className="label">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className="input"
                placeholder="John Doe"
                required
              />
            </div>

            <div>
              <label htmlFor="phone" className="label">
                Phone <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className="input"
                placeholder="+254722123456"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="label">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="input"
                placeholder="john@example.com"
              />
            </div>

            <div className="col-span-2">
              <label htmlFor="id_number" className="label">
                ID Number
              </label>
              <input
                type="text"
                id="id_number"
                name="id_number"
                value={formData.id_number}
                onChange={handleInputChange}
                className="input"
                placeholder="12345678"
              />
            </div>
          </div>

          {/* Financial Info */}
          <div className="grid grid-cols-2 gap-4">
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
                min="0"
                required
              />
            </div>

            <div>
              <label htmlFor="security_deposit_amount" className="label">
                Security Deposit (KES) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="security_deposit_amount"
                name="security_deposit_amount"
                value={formData.security_deposit_amount}
                onChange={handleInputChange}
                className="input"
                min="0"
                required
              />
            </div>
          </div>

          {/* Move-in Date */}
          <div>
            <label htmlFor="move_in_date" className="label">
              Move-in Date
            </label>
            <input
              type="date"
              id="move_in_date"
              name="move_in_date"
              value={formData.move_in_date}
              onChange={handleInputChange}
              className="input"
            />
          </div>

          {/* Info Note */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-900">
              💡 <strong>Auto-invoicing:</strong> Deposit and first month rent invoices will be created automatically upon registration.
            </p>
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
              Register Tenant
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};