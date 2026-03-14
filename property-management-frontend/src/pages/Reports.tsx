import React, { useEffect, useState } from 'react';
import { TrendingUp, DollarSign, Users, Home, Calendar, Download, Filter, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ExportButton } from '../components/common/ExportButton';
import { paymentService } from '../services/payment.service';
import { invoiceService } from '../services/invoice.service';
import { propertyService } from '../services/property.service';
import { unitService } from '../services/unit.service';
import { tenantService } from '../services/tenant.service';
import { exportService } from '../services/export.service';
import { formatCurrency, formatDate } from '../utils/formatters';
import toast from 'react-hot-toast';

export const Reports: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });
  
  // Filter state
  const [filters, setFilters] = useState({
    propertyId: '',
    unitId: '',
    tenantId: '',
    invoiceStatus: '',
    paymentStatus: '',
  });
  
  // State for filtered display data
  const [payments, setPayments] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  
  // State for all unfiltered data
  const [allPayments, setAllPayments] = useState<any[]>([]);
  const [allInvoices, setAllInvoices] = useState<any[]>([]);
  const [properties, setProperties] = useState<any[]>([]);
  const [units, setUnits] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [dateRange, filters]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      console.log('🔍 Fetching all data...');

      // Fetch all data in parallel
      const [paymentsData, invoicesData, propertiesData, unitsData, tenantsData] = await Promise.all([
        paymentService.getAll(),
        invoiceService.getAll(),
        propertyService.getAll(),
        unitService.getAll(),
        tenantService.getAll(),
      ]);

      console.log('📦 Raw data fetched:', {
        payments: paymentsData.length,
        invoices: invoicesData.length,
        properties: propertiesData.length,
        units: unitsData.length,
        tenants: tenantsData.length,
      });

      setAllPayments(paymentsData);
      setAllInvoices(invoicesData);
      setProperties(propertiesData);
      setUnits(unitsData);
      setTenants(tenantsData);

    } catch (error) {
      console.error('❌ Error fetching reports:', error);
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    console.log('🔍 Applying filters:', { dateRange, filters });

    // Filter payments
    let filteredPayments = allPayments.filter((payment: any) => {
      // Date filter
      const paymentDate = new Date(payment.created_at || payment.trans_time);
      const startDate = new Date(dateRange.start);
      const endDate = new Date(dateRange.end);
      endDate.setHours(23, 59, 59, 999);
      
      if (paymentDate < startDate || paymentDate > endDate) return false;

      // Payment status filter
      if (filters.paymentStatus && payment.status !== filters.paymentStatus) return false;

      // Property/Unit/Tenant filter (via matched invoice)
      if (filters.propertyId || filters.unitId || filters.tenantId) {
        if (!payment.invoice_id) return false;
        
        const invoice = allInvoices.find((inv: any) => inv.id === payment.invoice_id);
        if (!invoice) return false;
        
        if (filters.propertyId && invoice.property_id !== filters.propertyId) return false;
        if (filters.unitId && invoice.unit_id !== filters.unitId) return false;
        if (filters.tenantId && invoice.tenant_id !== filters.tenantId) return false;
      }

      return true;
    });

    // Filter invoices
    let filteredInvoices = allInvoices.filter((invoice: any) => {
      // Date filter
      const invoiceDate = new Date(invoice.created_at);
      const startDate = new Date(dateRange.start);
      const endDate = new Date(dateRange.end);
      endDate.setHours(23, 59, 59, 999);
      
      if (invoiceDate < startDate || invoiceDate > endDate) return false;

      // Property filter
      if (filters.propertyId && invoice.property_id !== filters.propertyId) return false;

      // Unit filter
      if (filters.unitId && invoice.unit_id !== filters.unitId) return false;

      // Tenant filter
      if (filters.tenantId && invoice.tenant_id !== filters.tenantId) return false;

      // Invoice status filter
      if (filters.invoiceStatus && invoice.status !== filters.invoiceStatus) return false;

      return true;
    });

    console.log('✅ Filtered data:', {
      payments: filteredPayments.length,
      invoices: filteredInvoices.length,
    });

    setPayments(filteredPayments);
    setInvoices(filteredInvoices);
  };

  const handleResetFilters = () => {
    setFilters({
      propertyId: '',
      unitId: '',
      tenantId: '',
      invoiceStatus: '',
      paymentStatus: '',
    });
    setDateRange({
      start: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
    });
    toast.success('Filters reset');
  };

  // Calculate metrics from filtered data
  const totalRevenue = payments
    .filter((p: any) => p.status === 'matched')
    .reduce((sum: number, p: any) => sum + (p.amount || 0), 0);

  const totalInvoiced = invoices.reduce((sum: number, inv: any) => sum + (inv.amount || 0), 0);
  const totalPaid = invoices.reduce((sum: number, inv: any) => sum + (inv.paid_amount || 0), 0);
  const totalArrears = invoices
    .filter((inv: any) => inv.status === 'unpaid' || inv.status === 'overdue' || inv.status === 'partially_paid')
    .reduce((sum: number, inv: any) => sum + ((inv.amount || 0) - (inv.paid_amount || 0)), 0);

  const activeTenants = tenants.filter((t: any) => t.status === 'active').length;
  const collectionRate = totalInvoiced > 0 ? (totalPaid / totalInvoiced) * 100 : 0;

  // Filter units by selected property
  const filteredUnits = filters.propertyId 
    ? units.filter((unit: any) => unit.property_id === filters.propertyId)
    : units;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Get active filter count
  const activeFilterCount = Object.values(filters).filter(v => v !== '').length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
              <p className="text-gray-600 mt-1">
                Filter and analyze your property performance
              </p>
            </div>
            <div className="flex gap-3">
              <ExportButton
                onExportPDF={() => exportService.exportPaymentsPDF(
                  dateRange.start,
                  dateRange.end,
                  filters.propertyId || undefined
                )}
                onExportExcel={() => exportService.exportPaymentsExcel(
                  dateRange.start,
                  dateRange.end,
                  filters.propertyId || undefined
                )}
                pdfFilename={`payments_report_${new Date().toISOString().split('T')[0]}.pdf`}
                excelFilename={`payments_report_${new Date().toISOString().split('T')[0]}.xlsx`}
                label="Export Payments"
              />
              <ExportButton
                onExportPDF={() => exportService.exportInvoicesPDF(
                  filters.invoiceStatus || undefined,
                  filters.propertyId || undefined
                )}
                onExportExcel={() => exportService.exportInvoicesExcel(
                  filters.invoiceStatus || undefined,
                  filters.propertyId || undefined
                )}
                pdfFilename={`invoices_report_${new Date().toISOString().split('T')[0]}.pdf`}
                excelFilename={`invoices_report_${new Date().toISOString().split('T')[0]}.xlsx`}
                label="Export Invoices"
              />
            </div>
          </div>

          {/* Filters Section */}
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Filters {activeFilterCount > 0 && `(${activeFilterCount} active)`}
              </span>
            </div>

            {/* Date Range */}
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-gray-400" />
                <span className="text-sm text-gray-700">Date Range:</span>
              </div>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="input max-w-[180px]"
              />
              <span className="text-gray-500">to</span>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                className="input max-w-[180px]"
              />
            </div>

            {/* Property, Unit, Tenant, Status Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Property Filter */}
              <div>
                <label className="label">Property</label>
                <select
                  value={filters.propertyId}
                  onChange={(e) => {
                    setFilters(prev => ({ 
                      ...prev, 
                      propertyId: e.target.value,
                      unitId: '' // Reset unit when property changes
                    }));
                  }}
                  className="input"
                >
                  <option value="">All Properties</option>
                  {properties.map((property: any) => (
                    <option key={property.id} value={property.id}>
                      {property.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Unit Filter */}
              <div>
                <label className="label">Unit</label>
                <select
                  value={filters.unitId}
                  onChange={(e) => setFilters(prev => ({ ...prev, unitId: e.target.value }))}
                  className="input"
                  disabled={!filters.propertyId && filteredUnits.length === 0}
                >
                  <option value="">All Units</option>
                  {filteredUnits.map((unit: any) => (
                    <option key={unit.id} value={unit.id}>
                      {unit.unit_number}
                    </option>
                  ))}
                </select>
              </div>

              {/* Tenant Filter */}
              <div>
                <label className="label">Tenant</label>
                <select
                  value={filters.tenantId}
                  onChange={(e) => setFilters(prev => ({ ...prev, tenantId: e.target.value }))}
                  className="input"
                >
                  <option value="">All Tenants</option>
                  {tenants.map((tenant: any) => (
                    <option key={tenant.id} value={tenant.id}>
                      {tenant.full_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Invoice Status Filter */}
              <div>
                <label className="label">Invoice Status</label>
                <select
                  value={filters.invoiceStatus}
                  onChange={(e) => setFilters(prev => ({ ...prev, invoiceStatus: e.target.value }))}
                  className="input"
                >
                  <option value="">All Statuses</option>
                  <option value="unpaid">Unpaid</option>
                  <option value="partially_paid">Partially Paid</option>
                  <option value="paid">Paid</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>

              {/* Payment Status Filter */}
              <div>
                <label className="label">Payment Status</label>
                <select
                  value={filters.paymentStatus}
                  onChange={(e) => setFilters(prev => ({ ...prev, paymentStatus: e.target.value }))}
                  className="input"
                >
                  <option value="">All Payments</option>
                  <option value="matched">Matched</option>
                  <option value="unmatched">Unmatched</option>
                </select>
              </div>
            </div>

            {/* Filter Summary & Reset */}
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="text-sm text-gray-600">
                Showing: <strong>{payments.length} payments</strong>, <strong>{invoices.length} invoices</strong>
              </div>
              {activeFilterCount > 0 && (
                <button
                  onClick={handleResetFilters}
                  className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  <X className="w-4 h-4" />
                  Reset All Filters
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Payments Received */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">Payments Received</div>
                <DollarSign className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(totalRevenue)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {payments.filter(p => p.status === 'matched').length} matched payments
              </div>
            </CardContent>
          </Card>

          {/* Total Invoiced */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">Total Invoiced</div>
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(totalInvoiced)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {invoices.length} invoices
              </div>
            </CardContent>
          </Card>

          {/* Collection Rate */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">Collection Rate</div>
                <Users className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {collectionRate.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatCurrency(totalPaid)} collected
              </div>
            </CardContent>
          </Card>

          {/* Outstanding Arrears */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">Arrears</div>
                <Home className="w-5 h-5 text-red-600" />
              </div>
              <div className="text-3xl font-bold text-red-900">
                {formatCurrency(totalArrears)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Unpaid balance</div>
            </CardContent>
          </Card>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Payment Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-sm text-gray-600">Total Invoiced</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(totalInvoiced)}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-sm text-gray-600">Payments Received</span>
                  <span className="font-semibold text-green-600">{formatCurrency(totalRevenue)}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-sm text-gray-600">Outstanding Balance</span>
                  <span className="font-semibold text-red-600">{formatCurrency(totalArrears)}</span>
                </div>
                <div className="flex justify-between items-center pt-3">
                  <span className="text-sm font-medium text-gray-900">Collection Rate</span>
                  <span className="font-bold text-primary-600">{collectionRate.toFixed(1)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Payment Status Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-sm text-gray-600">Matched Payments</span>
                  <div className="text-right">
                    <span className="font-semibold text-green-600 block">
                      {payments.filter(p => p.status === 'matched').length}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatCurrency(payments.filter(p => p.status === 'matched').reduce((s, p) => s + p.amount, 0))}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-sm text-gray-600">Unmatched Payments</span>
                  <div className="text-right">
                    <span className="font-semibold text-yellow-600 block">
                      {payments.filter(p => p.status === 'unmatched').length}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatCurrency(payments.filter(p => p.status === 'unmatched').reduce((s, p) => s + p.amount, 0))}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center pt-3">
                  <span className="text-sm font-medium text-gray-900">Total Payments</span>
                  <div className="text-right">
                    <span className="font-bold text-primary-600 block">{payments.length}</span>
                    <span className="text-xs text-gray-500">
                      {formatCurrency(payments.reduce((s, p) => s + p.amount, 0))}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Filtered Payments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              {payments.length > 0 ? (
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Date</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Transaction ID</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Amount</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.slice(0, 10).map((payment: any) => (
                      <tr key={payment.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm">
                          {formatDate(payment.created_at || payment.trans_time)}
                        </td>
                        <td className="py-3 px-4 text-sm font-mono text-xs">{payment.trans_id}</td>
                        <td className="py-3 px-4 text-sm font-semibold">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${
                            payment.status === 'matched' 
                              ? 'bg-green-100 text-green-700'
                              : 'bg-yellow-100 text-yellow-700'
                          }`}>
                            {payment.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="text-center text-gray-500 py-12">
                  <p className="text-lg">No payments found</p>
                  <p className="text-sm mt-1">Try adjusting your filters</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};