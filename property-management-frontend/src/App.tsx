import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { LoadingPage } from './components/common/LoadingSpinner';
import { Layout } from './components/layout/Layout';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Properties } from './pages/Properties';
import { BulkUpload } from './pages/BulkUpload';
import { Units } from './pages/Units';
import { Tenants } from './pages/Tenants';
import { Invoices } from './pages/Invoices';
import { Payments } from './pages/Payments';
import { PaymentSimulator } from './pages/PaymentSimulator';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

function App(): JSX.Element {
  const { isAuthenticated, isLoading, initialize } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 2000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      <Routes>
        {/* Public Route */}
        <Route
          path="/login"
          element={
            isAuthenticated
              ? <Navigate to="/dashboard" replace />
              : <Login />
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            isAuthenticated
              ? <Layout><Dashboard /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/properties"
          element={
            isAuthenticated
              ? <Layout><Properties /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/bulkupload"
          element={
            isAuthenticated
              ? <Layout><BulkUpload /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/units"
          element={
            isAuthenticated
              ? <Layout><Units /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/tenants"
          element={
            isAuthenticated
              ? <Layout><Tenants /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/invoices"
          element={
            isAuthenticated
              ? <Layout><Invoices /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/payments"
          element={
            isAuthenticated
              ? <Layout><Payments /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/simulator"
          element={
            isAuthenticated
              ? <Layout><PaymentSimulator /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/reports"
          element={
            isAuthenticated
              ? <Layout><Reports /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        <Route
          path="/settings"
          element={
            isAuthenticated
              ? <Layout><Settings /></Layout>
              : <Navigate to="/login" replace />
          }
        />

        {/* Default Redirect */}
        <Route
          path="/"
          element={
            <Navigate
              to={isAuthenticated ? "/dashboard" : "/login"}
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;