import React, { useContext, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Offcanvas } from 'react-bootstrap';

const Sidebar = () => {
  const { user, logoutUser } = useContext(AuthContext);
  const location = useLocation();
  const [showMobile, setShowMobile] = useState(false);

  if (!user) return null;

  const handleClose = () => setShowMobile(false);
  const handleShow = () => setShowMobile(true);

  const agriculteurNavItems = [
    { path: '/dashboard', label: 'Tableau de bord', icon: '📊' },
    { path: '/parcelles', label: 'Mes Parcelles', icon: '🌱' },
    { path: '/historique', label: 'Historique', icon: '📈' },
  ];

  const adminNavItems = [
    { path: '/admin/dashboard', label: 'Vue d\'ensemble', icon: '👁️' },
    { path: '/admin/users', label: 'Utilisateurs', icon: '👥' },
    { path: '/admin/parcelles', label: 'Parcelles', icon: '🌍' },
    { path: '/admin/capteurs', label: 'Capteurs', icon: '🎛️' },
  ];

  const currentNavItems = user.role === 'admin' ? adminNavItems : agriculteurNavItems;

  const SidebarContent = () => (
    <div className="d-flex flex-column h-100 text-white" style={{ backgroundColor: 'var(--color-sidebar)' }}>
      <div className="p-4 mb-3">
        <span className="fs-5 fw-bold d-flex align-items-center gap-2">
          <span style={{ color: 'var(--color-primary)' }}>{user.role === 'admin' ? '🛡️' : '🌱'}</span> 
          <span>{user.role === 'admin' ? 'Admin Console' : 'Smart Irrigation'}</span>
        </span>
      </div>

      <div className="flex-grow-1 px-3">
        <ul className="nav nav-pills flex-column mb-auto gap-2">
          <li className="nav-item mb-2 px-1">
            <small className="text-uppercase text-secondary fw-bold" style={{ letterSpacing: '0.05em' }}>
              {user.role === 'admin' ? 'Administration' : 'Mon Espace'}
            </small>
          </li>
          
          {currentNavItems.map((item) => (
            <li className="nav-item" key={item.path}>
              <Link
                to={item.path}
                onClick={handleClose}
                className={`nav-link text-white d-flex align-items-center gap-3 py-2 px-3 rounded-3 transition-colors ${
                  location.pathname === item.path || (location.pathname.startsWith(item.path) && item.path !== '/dashboard' && item.path !== '/admin/dashboard')
                    ? 'active-nav-item'
                    : 'inactive-nav-item'
                }`}
                style={{ 
                  backgroundColor: location.pathname === item.path || (location.pathname.startsWith(item.path) && item.path !== '/dashboard' && item.path !== '/admin/dashboard') ? 'var(--color-primary)' : 'transparent',
                  transition: 'background-color 0.2s ease'
                }}
              >
                <span>{item.icon}</span>
                <span className="fw-medium">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <div className="p-4 mt-auto border-top border-secondary border-opacity-25">
        <div className="d-flex align-items-center gap-3 mb-3">
          <div className="rounded-circle bg-success text-white d-flex justify-content-center align-items-center fw-bold" style={{ width: '40px', height: '40px' }}>
            {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="text-truncate">
            <div className="fw-bold fs-6">{user.username || 'Utilisateur'}</div>
            <div className="text-white-50 small">{user.role === 'admin' ? 'Administrateur' : 'Agriculteur'}</div>
          </div>
        </div>
        <button 
          onClick={logoutUser} 
          className="btn btn-outline-light w-100 rounded-3 text-start px-3 py-2 border-secondary border-opacity-50 hover-bg-secondary"
        >
          🚪 Déconnexion
        </button>
      </div>
      <style>{`
        .inactive-nav-item:hover { background-color: var(--color-sidebar-hover) !important; }
        .hover-bg-secondary:hover { background-color: rgba(255,255,255,0.1) !important; color: white !important; }
      `}</style>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <div 
        className="d-none d-md-block position-fixed top-0 bottom-0 start-0 z-3" 
        style={{ width: '240px' }}
      >
        <SidebarContent />
      </div>

      {/* Mobile Top Header */}
      <div className="d-md-none position-fixed top-0 start-0 end-0 z-3 d-flex justify-content-between align-items-center px-3 py-2 shadow-sm" style={{ backgroundColor: 'var(--color-sidebar)', height: '60px' }}>
        <div className="fs-5 fw-bold text-white">🌱 Smart Irrigation</div>
        <button onClick={handleShow} className="btn btn-link text-white p-0 text-decoration-none fs-3">
          ☰
        </button>
      </div>

      {/* Mobile Offcanvas Sidebar */}
      <Offcanvas show={showMobile} onHide={handleClose} placement="start" style={{ width: '280px', backgroundColor: 'var(--color-sidebar)' }}>
        <SidebarContent />
      </Offcanvas>
    </>
  );
};

export default Sidebar;
