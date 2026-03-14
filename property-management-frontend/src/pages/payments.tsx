import React, { useEffect, useState } from 'react';
import { Banknote, CheckCircle, AlertCircle, Phone, Hash, Calendar, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { ExportButton } from '../components/common/ExportButton';
import { paymentService } from '../services/payment.service';
import { exportService } from '../services/export.service';
import type { Payment } from '../types';
import { formatCurrency, formatDateTime } from '../utils/formatters';
import toast from 'react-hot-toast';

export const Payments: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [allPayments, setAllPayments] = useState<Payment[]>([]); // Store all payments
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'matched' | 'unmatched'>('all');

  useEffect(() => {
    fetchAllPayments(); // Fetch all on mount
  }, []);

  useEffect(() => {
    filterPayments(); // Filter when tab changes
  }, [activeTab, allPayments]);

  const fetchAllPayments = async () => {
    try {
      console.log('🔄 Fetching all payments...');
      setLoading(true);
      const data = await paymentService.getAll();
      console.log('📥 Received payments data:', data);
      console.log('📊 Number of payments:', data.length);
      setAllPayments(data); // Store all payments
      setPayments(data); // Initially show all
    } catch (error) {
      console.error('❌ Error fetching payments:', error);
      toast.error('Failed to load payments');
      setAllPayments([]);
      setPayments([]);
    } finally {
      setLoading(false);
    }
  };

  const filterPayments = () => {
    if (activeTab === 'matched') {
      setPayments(allPayments.filter(p => p.status === 'matched'));
    } else if (activeTab === 'unmatched') {
      setPayments(allPayments.filter(p => p.status === 'unmatched'));
    } else {
      setPayments(allPayments);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      matched: 'success',
      unmatched: 'warning',
      duplicate: 'gray',
      failed: 'danger',
    };
    return <Badge variant={variants[status] || 'gray'}>{status}</Badge>;
  };

  // Calculate summary stats from ALL payments (not filtered)
  const totalAmount = allPayments.reduce((sum, p) => sum + p.amount, 0);
  const matchedCount = allPayments.filter(p => p.status === 'matched').length;
  const unmatchedCount = allPayments.filter(p => p.status === 'unmatched').length;
  const matchedAmount = allPayments
    .filter(p => p.status === 'matched')
    .reduce((sum, p) => sum + p.amount, 0);

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
              <h1 className="text-3xl font-bold text-gray-900">M-Pesa Payments</h1>
              <p className="text-gray-600 mt-1">
                View and manage M-Pesa payment transactions
              </p>
            </div>
            <div className="flex gap-3">
              <ExportButton
                onExportPDF={() => exportService.exportPaymentsPDF()}
                onExportExcel={() => exportService.exportPaymentsExcel()}
                pdfFilename={`payments_${new Date().toISOString().split('T')[0]}.pdf`}
                excelFilename={`payments_${new Date().toISOString().split('T')[0]}.xlsx`}
              />
              <Button 
                onClick={fetchAllPayments}
                variant="secondary"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </Button>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-600 font-medium">Total Payments</div>
              <div className="text-2xl font-bold text-blue-900">{allPayments.length}</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-sm text-green-600 font-medium">Matched</div>
              <div className="text-2xl font-bold text-green-900">{matchedCount}</div>
              <div className="text-xs text-green-600">{formatCurrency(matchedAmount)}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-sm text-yellow-600 font-medium">Unmatched</div>
              <div className="text-2xl font-bold text-yellow-900">{unmatchedCount}</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-sm text-purple-600 font-medium">Total Amount</div>
              <div className="text-2xl font-bold text-purple-900">{formatCurrency(totalAmount)}</div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex gap-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('all')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'all'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              All Payments
            </button>
            <button
              onClick={() => setActiveTab('matched')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'matched'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Matched ({matchedCount})
            </button>
            <button
              onClick={() => setActiveTab('unmatched')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'unmatched'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Unmatched ({unmatchedCount})
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {payments.length === 0 ? (
          <Card>
            <EmptyState
              icon={Banknote}
              title="No payments found"
              description={
                activeTab === 'matched'
                  ? 'No matched payments yet. Payments are automatically matched to invoices.'
                  : activeTab === 'unmatched'
                  ? 'No unmatched payments. All payments have been matched!'
                  : 'No M-Pesa payments received yet.'
              }
            />
          </Card>
        ) : (
          <div className="space-y-4">
            {payments.map((payment) => (
              <Card key={payment.id} hover>
                <CardContent>
                  <div className="flex items-start justify-between">
                    {/* Left Section */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          payment.status === 'matched' ? 'bg-green-100' : 'bg-yellow-100'
                        }`}>
                          {payment.status === 'matched' ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <AlertCircle className="w-5 h-5 text-yellow-600" />
                          )}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {formatCurrency(payment.amount)}
                          </h3>
                          <p className="text-xs text-gray-500">
                            {payment.first_name} {payment.last_name}
                          </p>
                        </div>
                      </div>

                      {/* Details Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-gray-600 flex items-center gap-1">
                            <Hash className="w-4 h-4" />
                            Transaction ID
                          </div>
                          <div className="font-semibold text-gray-900 font-mono text-xs">
                            {payment.trans_id}
                          </div>
                        </div>

                        <div>
                          <div className="text-gray-600 flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            Phone Number
                          </div>
                          <div className="font-semibold text-gray-900">
                            {payment.msisdn || 'N/A'}
                          </div>
                        </div>

                        <div>
                          <div className="text-gray-600 flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            Date
                          </div>
                          <div className="font-semibold text-gray-900">
                            {payment.trans_time ? formatDateTime(payment.trans_time) : formatDateTime(payment.created_at)}
                          </div>
                        </div>

                        <div>
                          <div className="text-gray-600">Bill Ref</div>
                          <div className="font-semibold text-gray-900">
                            {payment.bill_ref_number || 'N/A'}
                          </div>
                        </div>
                      </div>

                      {/* M-Pesa Details */}
                      {payment.paybill_shortcode && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <div className="text-xs text-gray-600 mb-1">M-Pesa Details</div>
                          <div className="flex gap-4 text-xs">
                            <span className="text-gray-600">
                              Paybill: <span className="font-semibold text-gray-900">{payment.paybill_shortcode}</span>
                            </span>
                            <span className="text-gray-600">
                              Method: <span className="font-semibold text-gray-900">{payment.payment_method}</span>
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Right Section - Status */}
                    <div className="ml-4">
                      {getStatusBadge(payment.status)}
                      {payment.matched_at && (
                        <div className="text-xs text-gray-500 mt-1">
                          Matched {formatDateTime(payment.matched_at)}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};