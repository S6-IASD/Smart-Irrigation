import React, { useState, useContext } from 'react';
import { Row, Col, Form, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { loginUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const success = await loginUser(username, password);
      if (success) {
        toast.success(`Bienvenue, ${username} !`);
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      } else {
        setError('Identifiants incorrects');
      }
    } catch (err) {
      setError('Erreur de connexion. Vérifiez vos identifiants.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="d-flex" style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
      {/* Colonne Gauche - Présentation (masquée sur mobile) */}
      <div 
        className="d-none d-lg-flex flex-column justify-content-between p-5" 
        style={{ 
          width: '45%', 
          background: 'linear-gradient(145deg, var(--color-sidebar) 0%, #0d4a22 100%)',
          color: 'white'
        }}
      >
        <div>
          <Link to="/" className="text-white text-decoration-none d-flex align-items-center gap-2 fw-bold fs-4">
            <span style={{ color: 'var(--color-primary)' }}>🌱</span> Smart Irrigation
          </Link>
        </div>
        <div>
          <h1 className="display-5 fw-bold mb-4">L'irrigation de demain,<br/>accessible aujourd'hui.</h1>
          <p className="lead text-white-50">
            Connectez-vous pour accéder à votre espace d'administration, surveiller vos capteurs et gérer les algorithmes prédictifs de votre exploitation.
          </p>
        </div>
        <div className="text-white-50 small">
          © 2026 Projet Académique MLOps
        </div>
      </div>

      {/* Colonne Droite - Formulaire */}
      <div className="flex-grow-1 d-flex align-items-center justify-content-center p-4">
        <div style={{ width: '100%', maxWidth: '400px' }}>
          
          <div className="mb-5 text-center text-lg-start">
            {/* Affiché sur mobile seulement */}
            <div className="d-lg-none d-flex align-items-center justify-content-center gap-2 fs-3 fw-bold mb-4">
              <span style={{ color: 'var(--color-primary)' }}>🌱</span> 
              <span style={{ color: 'var(--color-sidebar)' }}>Smart Irrigation</span>
            </div>
            <h2 className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>Bon retour !</h2>
            <p className="text-muted">Entrez vos identifiants pour continuer.</p>
          </div>

          {error && <Alert variant="danger" className="rounded-3 border-0">{error}</Alert>}

          <Form onSubmit={handleLogin}>
            <Form.Group className="mb-4" controlId="formBasicUsername">
              <Form.Label className="fw-medium text-muted small">Nom d'utilisateur</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ex: admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Form.Group className="mb-5" controlId="formBasicPassword">
              <Form.Label className="fw-medium text-muted small">Mot de passe</Form.Label>
              <Form.Control
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="py-2 bg-light border-0"
                style={{ borderRadius: '8px' }}
              />
            </Form.Group>

            <Button variant="success" type="submit" className="w-100 py-2 mb-4 fw-medium shadow-sm" disabled={isSubmitting} style={{ borderRadius: '8px' }}>
              {isSubmitting ? 'Connexion en cours...' : 'Se connecter'}
            </Button>
          </Form>

          <div className="text-center text-muted small">
            Pas encore de compte ? <Link to="/register" className="text-success text-decoration-none fw-bold">Demander un accès</Link>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default Login;
