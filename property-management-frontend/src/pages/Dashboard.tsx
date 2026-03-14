import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/common/Button';
import { Card, CardTitle, CardContent } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Building2, Home, Users, DollarSign, TrendingUp } from 'lucide-react';
import { dashboardService } from '../services/dashboard.service';
import { DashboardStats } from '../types';
import { formatCurrency } from '../utils/formatters';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await dashboardService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name}! 👋
          </h2>
          <p className="text-gray-600">
            Here's what's happening with your properties today.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Properties Card */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">
                  Total Properties
                </div>
                <Building2 className="w-5 h-5 text-primary-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {stats?.properties || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats?.properties === 0 ? 'No properties yet' : 'Buildings managed'}
              </div>
            </CardContent>
          </Card>

          {/* Units Card */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">
                  Total Units
                </div>
                <Home className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {stats?.units.total || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats?.units.occupancy_rate.toFixed(1)}% occupied
              </div>
              <div className="mt-2 flex items-center gap-2 text-xs">
                <span className="text-green-600 font-medium">
                  {stats?.units.occupied || 0} occupied
                </span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-600">
                  {stats?.units.vacant || 0} vacant
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Tenants Card */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">
                  Active Tenants
                </div>
                <Users className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {stats?.tenants.active || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats?.tenants.active === 0 ? 'No tenants yet' : 'Currently renting'}
              </div>
            </CardContent>
          </Card>

          {/* Revenue Card */}
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-600">
                  This Month Revenue
                </div>
                <DollarSign className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(stats?.revenue.this_month || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats?.revenue.this_month === 0 ? 'No payments yet' : 'Collected this month'}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Arrears Warning */}
        {stats && stats.arrears.total > 0 && (
          <div className="mb-8">
            <Card className="border-l-4 border-l-red-500 bg-red-50">
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    <TrendingUp className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-red-900">Outstanding Arrears</h4>
                    <p className="text-sm text-red-700">
                      Total unpaid: <strong>{formatCurrency(stats.arrears.total)}</strong>
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Getting Started or Quick Actions */}
        {stats?.properties === 0 ? (
          <Card>
            <CardTitle>🚀 Getting Started</CardTitle>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-semibold">1</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Add Your Properties</h4>
                    <p className="text-sm text-gray-600">
                      Start by adding your buildings or properties to the system.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-semibold">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Create Units</h4>
                    <p className="text-sm text-gray-600">
                      Add units (apartments/rooms) to each property with rent details.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-semibold">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Add Tenants</h4>
                    <p className="text-sm text-gray-600">
                      Register your tenants and invoices will be generated automatically!
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-900">
                  💡 <strong>Tip:</strong> Once you add a tenant, the system will automatically create deposit and rent invoices. M-Pesa payments will be matched automatically!
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Stats */}
            <Card>
              <CardTitle>📊 Quick Overview</CardTitle>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Occupancy Rate</span>
                    <span className="font-semibold text-gray-900">
                      {stats?.units.occupancy_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Total Units</span>
                    <span className="font-semibold text-gray-900">
                      {stats?.units.total}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Occupied Units</span>
                    <span className="font-semibold text-green-600">
                      {stats?.units.occupied}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-sm text-gray-600">Vacant Units</span>
                    <span className="font-semibold text-gray-600">
                      {stats?.units.vacant}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardTitle>⚡ Quick Actions</CardTitle>
              <CardContent>
                <div className="space-y-3">
                  <Button 
                    variant="primary" 
                    className="w-full justify-start"
                    onClick={() => navigate('/properties')}
                  >
                    <Building2 className="w-4 h-4" />
                    View Properties
                  </Button>
                  <Button 
                    variant="secondary" 
                    className="w-full justify-start"
                    onClick={() => navigate('/units')}
                  >
                    <Home className="w-4 h-4" />
                    Manage Units
                  </Button>
                  <Button 
                    variant="secondary" 
                    className="w-full justify-start"
                    onClick={() => navigate('/tenants')}
                  >
                    <Users className="w-4 h-4" />
                    Register Tenant
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};