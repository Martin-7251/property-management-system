import React, { useState } from 'react';
import { Smartphone, Send, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Button } from '../components/common/Button';
import api from '../services/api';
import toast from 'react-hot-toast';

export const PaymentSimulator: React.FC = () => {
  const [formData, setFormData] = useState({
    trans_id: '',
    amount: '',
    msisdn: '',
    bill_ref_number: '',
    first_name: '',
    last_name: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const generateTransactionId = () => {
    const timestamp = Date.now().toString().slice(-6); // Last 6 digits of timestamp
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return `SIM${timestamp}${random}`;
  };

  const handleQuickFill = () => {
    setFormData({
      trans_id: generateTransactionId(), // Generate fresh ID each time
      amount: '25000',
      msisdn: '+254722123456',
      bill_ref_number: 'TENANT001',
      first_name: 'John',
      last_name: 'Doe',
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Simulate M-Pesa confirmation callback format
      const payload = {
        TransactionType: "Pay Bill",
        TransID: formData.trans_id,
        TransTime: new Date().toISOString().replace('T', ' ').substring(0, 19),
        TransAmount: parseFloat(formData.amount),
        BusinessShortCode: "174379", // Default paybill
        BillRefNumber: formData.bill_ref_number,
        InvoiceNumber: "",
        OrgAccountBalance: "",
        ThirdPartyTransID: "",
        MSISDN: formData.msisdn,
        FirstName: formData.first_name,
        MiddleName: "",
        LastName: formData.last_name
      };

      console.log('📤 Sending payment payload:', payload);
      const response = await api.post('/mpesa/confirmation', payload);
      console.log('📥 Payment response:', response.data);
      
      // Check response
      if (response.data.ResultCode === "0" || response.data.ResultCode === 0) {
        toast.success('✅ Payment created! Go to Payments page and click Refresh.');
        console.log('✅ Payment successful - ResultCode: 0');
      } else if (response.data.ResultDesc) {
        toast.success(`✅ ${response.data.ResultDesc}`);
        console.log('📝 Response:', response.data.ResultDesc);
      } else {
        toast.success('✅ Payment processed! Check Payments page.');
        console.log('✅ Payment processed');
      }
      
      // Reset form
      setFormData({
        trans_id: '',
        amount: '',
        msisdn: '',
        bill_ref_number: '',
        first_name: '',
        last_name: '',
      });
    } catch (error: any) {
      console.error('❌ Simulation error:', error);
      console.error('❌ Error response:', error.response?.data);
      
      const message = error.response?.data?.detail || 
                     error.response?.data?.ResultDesc || 
                     error.message ||
                     'Failed to simulate payment';
      toast.error(`❌ ${message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Smartphone className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">M-Pesa Payment Simulator</h1>
              <p className="text-gray-600 mt-1">
                Test M-Pesa payments without actual transactions
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Simulate M-Pesa Payment</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Quick Fill Button */}
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={handleQuickFill}
                >
                  <Zap className="w-4 h-4" />
                  Quick Fill (Test Data)
                </Button>
              </div>

              {/* Transaction ID */}
              <div>
                <label htmlFor="trans_id" className="label">
                  Transaction ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="trans_id"
                  name="trans_id"
                  value={formData.trans_id}
                  onChange={handleInputChange}
                  className="input"
                  placeholder="e.g., SIMABCD1234"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Unique M-Pesa transaction ID
                </p>
              </div>

              {/* Amount */}
              <div>
                <label htmlFor="amount" className="label">
                  Amount (KES) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  className="input"
                  placeholder="e.g., 25000"
                  min="1"
                  required
                />
              </div>

              {/* Phone Number */}
              <div>
                <label htmlFor="msisdn" className="label">
                  Phone Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  id="msisdn"
                  name="msisdn"
                  value={formData.msisdn}
                  onChange={handleInputChange}
                  className="input"
                  placeholder="e.g., +254722123456"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Customer's M-Pesa phone number
                </p>
              </div>

              {/* Bill Reference */}
              <div>
                <label htmlFor="bill_ref_number" className="label">
                  Bill Reference Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="bill_ref_number"
                  name="bill_ref_number"
                  value={formData.bill_ref_number}
                  onChange={handleInputChange}
                  className="input"
                  placeholder="e.g., TENANT001 or Invoice Number"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  This is used to match payment to tenant/invoice
                </p>
              </div>

              {/* Customer Name */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="label">
                    First Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="John"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="last_name" className="label">
                    Last Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Doe"
                    required
                  />
                </div>
              </div>

              {/* Info Box */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">💡 How Auto-Matching Works</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• System matches payments using <strong>Bill Reference Number</strong></li>
                  <li>• Tenants can use their phone number or invoice number</li>
                  <li>• If matched, invoice status updates automatically</li>
                  <li>• Unmatched payments appear in "Unmatched" tab</li>
                </ul>
              </div>

              {/* Submit Button */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  variant="primary"
                  loading={submitting}
                  disabled={submitting}
                  className="flex-1"
                >
                  <Send className="w-4 h-4" />
                  Simulate Payment
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>📋 Testing Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-4 bg-yellow-50 rounded-lg mb-4">
              <h4 className="font-semibold text-yellow-900 mb-2">⚠️ Important: Payment Visibility</h4>
              <p className="text-sm text-yellow-800">
                Payments only appear on the Payments page if they are <strong>matched to an invoice</strong>. 
                Unmatched payments are stored but filtered out by the backend.
              </p>
            </div>
            
            <div className="space-y-4 text-sm text-gray-700">
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Step 1: Register a Tenant</h4>
                <p>Go to Tenants page and register a tenant. Note their phone number.</p>
                <p className="text-xs text-gray-500 mt-1">Example: +254722111111</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Step 2: Check Invoice Number</h4>
                <p>Go to Invoices page. Two invoices will be auto-created for the tenant.</p>
                <p className="text-xs text-gray-500 mt-1">Note the invoice number (e.g., INV-2025-001)</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Step 3: Simulate Payment</h4>
                <p><strong>Critical:</strong> Use the tenant's phone number OR invoice number as the Bill Reference.</p>
                <p className="text-xs text-green-600 mt-1">✅ Bill Reference: +254722111111 (matches tenant's phone)</p>
                <p className="text-xs text-green-600">✅ Bill Reference: INV-2025-001 (matches invoice number)</p>
                <p className="text-xs text-red-600">❌ Bill Reference: TENANT001 (won't match anything)</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Step 4: Check Results</h4>
                <p>Go to Payments page - payment should be "Matched" ✅</p>
                <p>Go to Invoices page - invoice should show payment received 💰</p>
              </div>
              
              <div className="p-3 bg-blue-50 rounded mt-4">
                <p className="text-xs text-blue-900">
                  <strong>Why?</strong> The backend only shows payments linked to your properties. 
                  Matching the payment to an invoice automatically links it to the property.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};