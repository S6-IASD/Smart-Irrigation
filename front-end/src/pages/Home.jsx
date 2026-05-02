import React from 'react';
import { Container, Row, Col, Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div style={{ backgroundColor: 'var(--color-bg)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Public Header Minimalist */}
      <div className="py-4 px-4 bg-white border-bottom shadow-sm d-flex justify-content-between align-items-center">
        <h3 className="mb-0 fw-bold d-flex align-items-center gap-2">
          <span style={{ color: 'var(--color-primary)' }}>🌱</span> 
          <span>Smart Irrigation</span>
        </h3>
        <div className="d-flex gap-3">
          <Link to="/login" className="btn btn-link text-decoration-none text-dark fw-medium">Se connecter</Link>
          <Link to="/register" className="btn btn-success px-4 rounded-pill fw-medium">S'inscrire</Link>
        </div>
      </div>

      <Container className="flex-grow-1 py-5 my-md-5">
        
        {/* 1. Hero Section */}
        <Row className="align-items-center mb-5 pb-5 mt-md-4">
          <Col lg={7} className="mb-5 mb-lg-0 text-center text-lg-start pe-lg-5">
            <Badge className="bg-success bg-opacity-10 text-success rounded-pill px-3 py-2 mb-4 fw-medium border border-success border-opacity-25">
              🚀 L'avenir de l'agriculture intelligente
            </Badge>
            <h1 className="display-4 fw-bold mb-4" style={{ color: 'var(--color-sidebar)', lineHeight: '1.2' }}>
              Optimisez chaque goutte d'eau avec précision.
            </h1>
            <p className="lead text-muted mb-5" style={{ fontSize: '1.2rem' }}>
              Un système SaaS propulsé par l'intelligence artificielle pour monitorer, prédire et automatiser l'irrigation de vos parcelles agricoles en temps réel.
            </p>
            <div className="d-grid gap-3 d-md-flex justify-content-md-start">
               <Link to="/register">
                 <Button variant="success" size="lg" className="rounded-pill px-5 shadow-sm fw-medium">
                   Commencer maintenant →
                 </Button>
               </Link>
            </div>
          </Col>
          <Col lg={5}>
            <div className="position-relative">
              <div className="position-absolute bg-success rounded-circle" style={{ width: '300px', height: '300px', top: '-20px', left: '-20px', filter: 'blur(80px)', opacity: '0.15', zIndex: '0' }}></div>
              <img src="https://images.unsplash.com/photo-1628183204940-abeb1d2fd975?auto=format&fit=crop&q=80&w=800" alt="Agriculture Intelligente" className="img-fluid rounded-4 shadow-lg position-relative z-1" style={{ border: '4px solid white' }} />
              {/* Floating info card */}
              <div className="position-absolute bg-white rounded-4 shadow-lg p-3 z-2 d-flex align-items-center gap-3" style={{ bottom: '-20px', left: '-40px', border: '1px solid var(--color-border)' }}>
                <div className="bg-success bg-opacity-10 p-2 rounded-3 text-success fs-4">💧</div>
                <div>
                  <div className="fw-bold fs-5 text-dark">-30%</div>
                  <div className="text-muted small">Économie d'eau moyenne</div>
                </div>
              </div>
            </div>
          </Col>
        </Row>

        {/* 2. Features Section */}
        <div className="text-center mb-5 pt-5">
          <h2 className="fw-bold mb-3" style={{ color: 'var(--color-sidebar)' }}>Tout ce dont vous avez besoin</h2>
          <p className="text-muted mx-auto mb-5" style={{ maxWidth: '600px' }}>Une suite d'outils complète pour piloter votre exploitation de manière moderne et éclairée.</p>
          
          <Row>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 p-4 hover-card" style={{ backgroundColor: 'var(--color-surface)', borderRadius: '16px' }}>
                <Card.Body className="text-start">
                  <div className="bg-success text-white rounded-3 d-inline-flex align-items-center justify-content-center mb-4" style={{ width: '48px', height: '48px', fontSize: '24px' }}>🤖</div>
                  <Card.Title className="fw-bold fs-5 mb-3" style={{ color: 'var(--color-sidebar)' }}>IA & Machine Learning</Card.Title>
                  <Card.Text className="text-muted" style={{ lineHeight: '1.6' }}>
                    Nos modèles prédictifs calculent la quantité exacte d'eau nécessaire en fonction du sol (N, P, K), de la température et de l'humidité afin d'éviter la sécheresse ou le stress hydrique.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 p-4 hover-card" style={{ backgroundColor: 'var(--color-surface)', borderRadius: '16px' }}>
                <Card.Body className="text-start">
                  <div className="bg-success text-white rounded-3 d-inline-flex align-items-center justify-content-center mb-4" style={{ width: '48px', height: '48px', fontSize: '24px' }}>⛅</div>
                  <Card.Title className="fw-bold fs-5 mb-3" style={{ color: 'var(--color-sidebar)' }}>Météo Temps Réel</Card.Title>
                  <Card.Text className="text-muted" style={{ lineHeight: '1.6' }}>
                    Intégration d'API météo ultra-précises par géolocalisation. Le système reporte automatiquement l'irrigation s'il s'apprête à pleuvoir sur votre parcelle.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 p-4 hover-card" style={{ backgroundColor: 'var(--color-surface)', borderRadius: '16px' }}>
                <Card.Body className="text-start">
                  <div className="bg-success text-white rounded-3 d-inline-flex align-items-center justify-content-center mb-4" style={{ width: '48px', height: '48px', fontSize: '24px' }}>📡</div>
                  <Card.Title className="fw-bold fs-5 mb-3" style={{ color: 'var(--color-sidebar)' }}>Capteurs IoT</Card.Title>
                  <Card.Text className="text-muted" style={{ lineHeight: '1.6' }}>
                    Compatible avec le matériel existant. Connectez et gérez vos capteurs d'humidité et d'électroconductivité directement depuis un tableau de bord SaaS unifié.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </div>

        {/* 3. Team Section */}
        <div className="py-5">
          <div className="text-center mb-5">
            <Badge className="bg-secondary bg-opacity-10 text-secondary rounded-pill px-3 py-2 mb-3 fw-medium">
              Notre expertise
            </Badge>
            <h2 className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>L'équipe derrière le projet</h2>
          </div>
          
          <Row className="justify-content-center">
            {/* John Doe Placeholder */}
            <Col md={4} lg={3} className="mb-4">
              <Card className="border-0 shadow-sm text-center p-4 hover-card" style={{ borderRadius: '16px' }}>
                <div className="mx-auto rounded-circle d-flex align-items-center justify-content-center text-white mb-3 shadow-sm" style={{ width: '80px', height: '80px', backgroundColor: '#3b82f6', fontSize: '24px', fontWeight: 'bold' }}>
                  JD
                </div>
                <h5 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>[Prénom Nom]</h5>
                <div className="text-success small fw-medium mb-3">[Rôle MLOps / Backend]</div>
                <p className="text-muted small mb-0">Développeur principal de l'architecture backend et de l'intégration des modèles ML.</p>
              </Card>
            </Col>

            {/* Jane Doe Placeholder */}
            <Col md={4} lg={3} className="mb-4">
              <Card className="border-0 shadow-sm text-center p-4 hover-card" style={{ borderRadius: '16px' }}>
                <div className="mx-auto rounded-circle d-flex align-items-center justify-content-center text-white mb-3 shadow-sm" style={{ width: '80px', height: '80px', backgroundColor: '#8b5cf6', fontSize: '24px', fontWeight: 'bold' }}>
                  JS
                </div>
                <h5 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>[Prénom Nom]</h5>
                <div className="text-success small fw-medium mb-3">[Rôle Frontend / Design]</div>
                <p className="text-muted small mb-0">Créateur de l'interface SaaS réactive et experte en expérience utilisateur (UX).</p>
              </Card>
            </Col>

            {/* Bob Smith Placeholder */}
            <Col md={4} lg={3} className="mb-4">
              <Card className="border-0 shadow-sm text-center p-4 hover-card" style={{ borderRadius: '16px' }}>
                <div className="mx-auto rounded-circle d-flex align-items-center justify-content-center text-white mb-3 shadow-sm" style={{ width: '80px', height: '80px', backgroundColor: '#ec4899', fontSize: '24px', fontWeight: 'bold' }}>
                  BS
                </div>
                <h5 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>[Prénom Nom]</h5>
                <div className="text-success small fw-medium mb-3">[Rôle Data / IoT]</div>
                <p className="text-muted small mb-0">Chargé des pipelines de données et de la configuration des capteurs simulés/réels.</p>
              </Card>
            </Col>
          </Row>
        </div>

      </Container>
      
      {/* 4. Footer */}
      <footer className="mt-auto py-4 border-top bg-white">
        <Container className="text-center">
          <div className="d-flex justify-content-center align-items-center gap-2 mb-2">
            <span style={{ color: 'var(--color-primary)' }}>🌱</span>
            <span className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>Smart Irrigation</span>
          </div>
          <p className="text-muted small mb-0">© 2026 — Projet académique MLOps & IoT. Tous droits réservés.</p>
        </Container>
      </footer>

    </div>
  );
};

// Extracted Badge component to avoid importing from react-bootstrap if missing above
const Badge = ({ children, className }) => <span className={`badge ${className || ''}`}>{children}</span>;

export default Home;
