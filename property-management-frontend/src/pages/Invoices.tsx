import React, { useEffect, useState } from 'react';
import { FileText, Filter, Calendar, DollarSign, User } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { ExportButton } from '../components/common/ExportButton';
import { invoiceService } from '../services/invoice.service';
import { propertyService } from '../services/property.service';
import { exportService } from '../services/export.service';
import type { Invoice, Property } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import toast from 'react-hot-toast';

export const Invoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProperty, setSelectedProperty] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  useEffect(() => {
    fetchProperties();
    fetchInvoices();
  }, []);

  useEffect(() => {
    fetchInvoices();
  }, [selectedProperty, selectedStatus]);

  const fetchProperties = async () => {
    try {
      const data = await propertyService.getAll();
      setProperties(data);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const data = await invoiceService.getAll(
        selectedProperty || undefined,
        selectedStatus || undefined
      );
      setInvoices(data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      toast.error('Failed to load invoices');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      paid: 'success',
      unpaid: 'warning',
      overdue: 'danger',
      partially_paid: 'info',
    };
    return <Badge variant={variants[status] || 'gray'}>{status.replace('_', ' ')}</Badge>;
  };

  const getPaymentProgress = (invoice: Invoice) => {
    const total = invoice.amount;
    const paid = invoice.paid_amount;
    const percentage = total > 0 ? (paid / total) * 100 : 0;
    
    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${
            percentage === 100 ? 'bg-green-600' : 'bg-blue-600'
          }`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    );
  };

  const getPropertyName = (propertyId: string) => {
    const property = properties.find(p => p.id === propertyId);
    return property?.name || 'Unknown';
  };

  // Calculate summary stats
  const totalAmount = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const totalPaid = invoices.reduce((sum, inv) => sum + inv.paid_amount, 0);
  const totalUnpaid = totalAmount - totalPaid;
  const unpaidCount = invoices.filter(inv => inv.status === 'unpaid' || inv.status === 'overdue').length;

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
              <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
              <p className="text-gray-600 mt-1">
                View and manage all invoices
              </p>
            </div>
            <ExportButton
              onExportPDF={() => exportService.exportInvoicesPDF(selectedStatus, selectedProperty)}
              onExportExcel={() => exportService.exportInvoicesExcel(selectedStatus, selectedProperty)}
              pdfFilename={`invoices_${new Date().toISOString().split('T')[0]}.pdf`}
              excelFilename={`invoices_${new Date().toISOString().split('T')[0]}.xlsx`}
            />
          </div>

          {/* Summary Stats */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-600 font-medium">Total Invoices</div>
              <div className="text-2xl font-bold text-blue-900">{invoices.length}</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-sm text-green-600 font-medium">Total Amount</div>
              <div className="text-2xl font-bold text-green-900">{formatCurrency(totalAmount)}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-sm text-yellow-600 font-medium">Unpaid</div>
              <div className="text-2xl font-bold text-yellow-900">{formatCurrency(totalUnpaid)}</div>
              <div className="text-xs text-yellow-600">{unpaidCount} invoices</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-sm text-purple-600 font-medium">Collected</div>
              <div className="text-2xl font-bold text-purple-900">{formatCurrency(totalPaid)}</div>
            </div>
          </div>

          {/* Filters */}
          <div className="mt-4 flex gap-4">
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

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="input max-w-xs"
            >
              <option value="">All Statuses</option>
              <option value="unpaid">Unpaid</option>
              <option value="partially_paid">Partially Paid</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {invoices.length === 0 ? (
          <Card>
            <EmptyState
              icon={FileText}
              title="No invoices found"
              description="Invoices are automatically created when you register tenants."
            />
          </Card>
        ) : (
          <div className="space-y-4">
            {invoices.map((invoice) => {
              const balance = invoice.amount - invoice.paid_amount - invoice.credit_applied;
              
              return (
                <Card key={invoice.id} hover>
                  <CardContent>
                    <div className="flex items-start justify-between">
                      {/* Left Section */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <FileText className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">
                              {invoice.invoice_number}
                            </h3>
                            <p className="text-xs text-gray-500">
                              {getPropertyName(invoice.property_id)} • {invoice.invoice_type.replace('_', ' ')}
                            </p>
                          </div>
                        </div>

                        {/* Details Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <div className="text-gray-600 flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Due Date
                            </div>
                            <div className="font-semibold text-gray-900">
                              {formatDate(invoice.due_date)}
                            </div>
                          </div>

                          <div>
                            <div className="text-gray-600 flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              Amount
                            </div>
                            <div className="font-semibold text-gray-900">
                              {formatCurrency(invoice.amount)}
                            </div>
                          </div>

                          <div>
                            <div className="text-gray-600">Paid</div>
                            <div className="font-semibold text-green-600">
                              {formatCurrency(invoice.paid_amount)}
                            </div>
                          </div>

                          <div>
                            <div className="text-gray-600">Balance</div>
                            <div className={`font-semibold ${balance === 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(balance)}
                            </div>
                          </div>
                        </div>

                        {/* Payment Progress */}
                        <div className="mt-3">
                          {getPaymentProgress(invoice)}
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>
                              {((invoice.paid_amount / invoice.amount) * 100).toFixed(0)}% paid
                            </span>
                            <span>{formatCurrency(balance)} remaining</span>
                          </div>
                        </div>
                      </div>

                      {/* Right Section - Status */}
                      <div className="ml-4">
                        {getStatusBadge(invoice.status)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};