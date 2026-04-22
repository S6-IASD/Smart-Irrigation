import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Table, Badge } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import axiosInstance from '../api/axios';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';

const ParcelleDetail = () => {
  const { id } = useParams();
  const [parcelle, setParcelle] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  const [sensorData, setSensorData] = useState({
    humidite_sol: 50,
    temperature_sol: 25,
    N: 100,
    P: 50,
    K: 100
  });

  const fetchData = async () => {
    try {
      const [parcelleRes, historyRes] = await Promise.all([
        axiosInstance.get(`/api/parcelles/${id}/`),
        axiosInstance.get(`/api/prediction/history/${id}/`)
      ]);
      setParcelle(parcelleRes.data);
      const sortedHistory = historyRes.data.sort((a, b) => new Date(b.created_at || b.date) - new Date(a.created_at || a.date));
      setHistory(sortedHistory);
    } catch (error) {
      toast.error('Erreur lors du chargement des données de la parcelle');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleChange = (e) => {
    setSensorData({ ...sensorData, [e.target.name]: parseFloat(e.target.value) });
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setPredictionResult(null);
    try {
      const response = await axiosInstance.post('/api/prediction/', {
        parcelle_id: id,
        ...sensorData
      });
      setPredictionResult(response.data);
      toast.success('Calcul effectué avec succès');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la prédiction');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!parcelle) return <Container className="py-5 text-center"><h4>Parcelle introuvable</h4></Container>;

  const chartData = [...history].slice(0, 10).reverse().map(item => ({
    name: new Date(item.created_at || item.date).toLocaleDateString(),
    eau_litres: item.eau_litres || 0
  }));

  return (
    <Container className="py-4">
      <div className="mb-4">
        <Link to="/parcelles" className="text-muted text-decoration-none fw-medium hover-text-success d-inline-flex align-items-center gap-2">
          <span>←</span> <span>Retour aux parcelles</span>
        </Link>
      </div>

      <Row className="mb-4">
        <Col md={4} className="mb-4 mb-md-0">
          {/* Fiche d'identité de la parcelle */}
          <Card className="border-0 shadow-sm rounded-4 h-100" style={{ background: 'linear-gradient(135deg, var(--color-sidebar) 0%, #1e293b 100%)', color: 'white' }}>
            <Card.Body className="p-4 d-flex flex-column">
              <div className="bg-white bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{ width: '48px', height: '48px', fontSize: '1.5rem' }}>
                🌱
              </div>
              <h3 className="fw-bold mb-4">{parcelle.nom}</h3>
              
              <div className="mb-3 d-flex justify-content-between border-bottom border-secondary border-opacity-50 pb-2">
                <span className="text-white-50 small text-uppercase fw-bold">Plante</span>
                <span className="fw-medium">{parcelle.type_plante}</span>
              </div>
              <div className="mb-3 d-flex justify-content-between border-bottom border-secondary border-opacity-50 pb-2">
                <span className="text-white-50 small text-uppercase fw-bold">Stade</span>
                <span className="fw-medium text-capitalize">{parcelle.stade}</span>
              </div>
              <div className="mb-3 d-flex justify-content-between border-bottom border-secondary border-opacity-50 pb-2">
                <span className="text-white-50 small text-uppercase fw-bold">Surface</span>
                <span className="fw-medium">{parcelle.superficie_ha} ha</span>
              </div>
              <div className="d-flex justify-content-between">
                <span className="text-white-50 small text-uppercase fw-bold">GPS</span>
                <span className="fw-medium small font-monospace">{parcelle.latitude}, {parcelle.longitude}</span>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
          {/* Simulateur */}
          <Card className="border-0 shadow-sm rounded-4 h-100">
            <Card.Header className="bg-white border-0 pt-4 px-4 pb-0">
              <h5 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>Simulateur d'environnement</h5>
              <p className="text-muted small">Ajustez les valeurs des capteurs pour tester les modèles ML.</p>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <Form onSubmit={handlePredict}>
                <Row className="gy-3">
                  <Col md={6}>
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Humidité du sol</Form.Label>
                        <span className="fw-bold" style={{ color: 'var(--color-primary)' }}>{sensorData.humidite_sol}%</span>
                      </div>
                      <Form.Range name="humidite_sol" min="0" max="100" value={sensorData.humidite_sol} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Température</Form.Label>
                        <span className="fw-bold" style={{ color: '#ef4444' }}>{sensorData.temperature_sol}°C</span>
                      </div>
                      <Form.Range name="temperature_sol" min="-10" max="60" value={sensorData.temperature_sol} onChange={handleChange} />
                    </Form.Group>
                  </Col>

                  <Col md={4} className="mt-4">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Azote (N)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.N}</span>
                      </div>
                      <Form.Range name="N" min="0" max="500" value={sensorData.N} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={4} className="mt-4">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Phosphore (P)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.P}</span>
                      </div>
                      <Form.Range name="P" min="0" max="300" value={sensorData.P} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={4} className="mt-4">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Potassium (K)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.K}</span>
                      </div>
                      <Form.Range name="K" min="0" max="400" value={sensorData.K} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                </Row>
                <div className="d-flex justify-content-end mt-4 pt-3 border-top">
                  <Button variant="success" type="submit" className="rounded-pill px-5 fw-medium shadow-sm" disabled={submitting}>
                    {submitting ? 'Calcul...' : 'Lancer le diagnostic'}
                  </Button>
                </div>
              </Form>

              {predictionResult && (
                <Alert 
                  variant={predictionResult.declenchement ? 'warning' : 'info'} 
                  className="mt-4 rounded-4 border-0 mb-0 shadow-sm d-flex align-items-center gap-3 p-4"
                  style={{ backgroundColor: predictionResult.declenchement ? '#fffbeb' : '#f0fdfa' }}
                >
                  <div className="fs-1">{predictionResult.declenchement ? '💧' : '✅'}</div>
                  <div className="flex-grow-1">
                    <h5 className="alert-heading fw-bold mb-1" style={{ color: predictionResult.declenchement ? '#b45309' : '#0f766e' }}>
                      Diagnostic terminé
                    </h5>
                    {predictionResult.declenchement ? (
                      <p className="mb-0 text-dark">L'algorithme recommande d'irriguer <strong className="fs-5">{predictionResult.eau_litres.toFixed(2)} litres</strong>.</p>
                    ) : (
                      <p className="mb-0 text-dark">Les conditions sont optimales. Aucune irrigation requise.</p>
                    )}
                  </div>
                  <div className="text-end border-start ps-3 d-none d-sm-block">
                    <div className="small text-muted text-uppercase mb-1">Moteur</div>
                    <Badge bg="" className="bg-dark text-white rounded-pill px-2 py-1 small">{predictionResult.mode}</Badge>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col xs={12}>
          <Card className="border-0 shadow-sm rounded-4 p-2">
            <Card.Body>
              <Card.Title className="fw-bold mb-4" style={{ fontSize: '1.1rem', color: 'var(--color-sidebar)' }}>
                Besoins hydriques (10 dernières prédictions)
              </Card.Title>
              <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{fontSize: 10}} tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} tick={{fontSize: 12}} />
                    <RechartsTooltip cursor={{fill: 'var(--color-bg)'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)'}} />
                    <Bar dataKey="eau_litres" name="Eau (Litres)" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="border-0 shadow-sm rounded-4 overflow-hidden mb-5">
        <Card.Header className="bg-white border-0 pt-4 pb-3">
          <h5 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)' }}>Historique des interventions</h5>
        </Card.Header>
        <Card.Body className="p-0">
          <Table responsive hover className="mb-0 align-middle">
            <thead style={{ backgroundColor: 'var(--color-bg)' }}>
              <tr>
                <th className="px-4 py-3 fw-semibold text-muted font-monospace small border-bottom-0">DATE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">EAU (L)</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">DÉCLENCHEMENT</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MODE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MÉTÉO</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, i) => (
                <tr key={item.id || i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td className="px-4 py-3 text-muted small">{new Date(item.created_at || item.date).toLocaleString()}</td>
                  <td className="py-3 fw-bold" style={{ color: 'var(--color-primary)' }}>{item.eau_litres?.toFixed(2)} L</td>
                  <td className="py-3">
                    {item.declenchement ? (
                      <Badge bg="" className="bg-warning bg-opacity-25 text-dark rounded-pill px-3 py-2 fw-medium border-0">Oui</Badge>
                    ) : (
                      <Badge bg="" className="bg-secondary bg-opacity-10 text-secondary rounded-pill px-3 py-2 fw-medium border-0">Non</Badge>
                    )}
                  </td>
                  <td className="py-3"><Badge bg="" className="bg-info bg-opacity-10 text-info rounded-pill px-3 py-2 fw-medium border-0">{item.mode}</Badge></td>
                  <td className="py-3 text-muted small">{item.weather_source}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted">Aucun historique disponible pour cette parcelle.</td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
      
      <style>{`
        .hover-text-success:hover { color: var(--color-primary) !important; }
      `}</style>
    </Container>
  );
};

export default ParcelleDetail;
