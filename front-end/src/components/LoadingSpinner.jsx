import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
      <div className="spinner-border text-success" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">Chargement...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;
