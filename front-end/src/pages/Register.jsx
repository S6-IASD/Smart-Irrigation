import React, { useState } from 'react';
import { Row, Col, Form, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import axiosInstance from '../api/axios';
import { toast } from 'react-toastify';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Veuillez remplir tous les champs');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await axiosInstance.post('/api/auth/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      toast.success('Inscription réussie ! Vous pouvez maintenant vous connecter.');
      navigate('/login');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erreur lors de l\'inscription.';
      setError(msg);
      toast.error('Erreur lors de l\'inscription.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="d-flex" style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
      {/* Colonne Gauche - Formulaire */}
      <div className="flex-grow-1 d-flex align-items-center justify-content-center p-4">
        <div style={{ width: '100%', maxWidth: '400px' }}>
          
          <div className="mb-4 text-center text-lg-start">
            {/* Affiché sur mobile seulement */}
            <div className="d-lg-none d-flex align-items-center justify-content-center gap-2 fs-3 fw-bold mb-4">
              <span style={{ color: 'var(--color-primary)' }}>🌱</span> 
              <span style={{ color: 'var(--color-sidebar)' }}>Smart Irrigation</span>
            </div>
            <h2 className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>Créer un compte</h2>
            <p className="text-muted">Rejoignez-nous pour gérer vos parcelles.</p>
          </div>

          {error && <Alert variant="danger" className="rounded-3 border-0">{error}</Alert>}

          <Form onSubmit={handleRegister}>
            <Form.Group className="mb-3" controlId="formUsername">
              <Form.Label className="fw-medium text-muted small">Nom d'utilisateur</Form.Label>
              <Form.Control
                type="text"
                name="username"
                placeholder="Ex: olivier42"
                value={formData.username}
                onChange={handleChange}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formEmail">
              <Form.Label className="fw-medium text-muted small">Adresse Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                placeholder="email@example.com"
                value={formData.email}
                onChange={handleChange}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formPassword">
              <Form.Label className="fw-medium text-muted small">Mot de passe</Form.Label>
              <Form.Control
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Form.Group className="mb-4" controlId="formConfirmPassword">
              <Form.Label className="fw-medium text-muted small">Confirmer le mot de passe</Form.Label>
              <Form.Control
                type="password"
                name="confirmPassword"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Button variant="success" type="submit" className="w-100 py-2 mb-4 fw-medium shadow-sm" disabled={isSubmitting} style={{ borderRadius: '8px' }}>
              {isSubmitting ? 'Création en cours...' : 'S\'inscrire'}
            </Button>
          </Form>

          <div className="text-center text-muted small">
            Déjà un compte ? <Link to="/login" className="text-success text-decoration-none fw-bold">Se connecter</Link>
          </div>
          
        </div>
      </div>

      {/* Colonne Droite - Présentation (masquée sur mobile) pour varier de Login */}
      <div 
        className="d-none d-lg-flex flex-column justify-content-between p-5" 
        style={{ 
          width: '45%', 
          background: 'linear-gradient(135deg, #0d4a22 0%, var(--color-sidebar) 100%)',
          color: 'white'
        }}
      >
        <div className="text-end">
          <Link to="/" className="text-white text-decoration-none d-inline-flex align-items-center gap-2 fw-bold fs-4">
            <span style={{ color: 'var(--color-primary)' }}>🌱</span> Smart Irrigation
          </Link>
        </div>
        <div>
          <h1 className="display-5 fw-bold mb-4">La donnée au service<br/>de la terre.</h1>
          <p className="lead text-white-50">
            Augmentez vos rendements tout en réduisant votre empreinte hydrique grâce à des algorithmes de pointe construits spécifiquement pour l'agriculture moderne.
          </p>
        </div>
        <div className="text-white-50 small">
          © 2026 Projet Académique MLOps
        </div>
      </div>
    </div>
  );
};

export default Register;
