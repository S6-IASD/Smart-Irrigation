import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import PrivateRoute from './components/PrivateRoute';

import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Parcelles from './pages/Parcelles';
import ParcelleDetail from './pages/ParcelleDetail';
import Historique from './pages/Historique';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';
import AdminParcelles from './pages/AdminParcelles';
import AdminCapteurs from './pages/AdminCapteurs';

const MainLayout = ({ children }) => {
  const { user } = useContext(AuthContext);
  const location = useLocation();
  const isPublicPage = ['/', '/login', '/register'].includes(location.pathname);

  // If user is not logged in or we are strictly on a public page that doesn't need sidebar layout
  // (Though if logged in, / points to Home, which shouldn't have sidebar margin ideally, but let's say public pages never have sidebar layout)
  if (!user || isPublicPage) {
    return (
      <>
        {user && !isPublicPage && <Sidebar />}
        <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
          {children}
        </div>
      </>
    );
  }

  // Authenticated layout with sidebar
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/parcelles" element={<PrivateRoute><Parcelles /></PrivateRoute>} />
            <Route path="/parcelles/:id" element={<PrivateRoute><ParcelleDetail /></PrivateRoute>} />
            <Route path="/historique" element={<PrivateRoute><Historique /></PrivateRoute>} />
            
            <Route path="/admin/dashboard" element={<PrivateRoute><AdminDashboard /></PrivateRoute>} />
            <Route path="/admin/users" element={<PrivateRoute><AdminUsers /></PrivateRoute>} />
            <Route path="/admin/parcelles" element={<PrivateRoute><AdminParcelles /></PrivateRoute>} />
            <Route path="/admin/capteurs" element={<PrivateRoute><AdminCapteurs /></PrivateRoute>} />
          </Routes>
        </MainLayout>
        <ToastContainer position="bottom-right" autoClose={3000} theme="colored" />
      </AuthProvider>
    </Router>
  );
}

export default App;
