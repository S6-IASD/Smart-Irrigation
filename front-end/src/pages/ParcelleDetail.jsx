import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Table, Badge } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
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
  const [alreadyDoneToday, setAlreadyDoneToday] = useState(false);
  const [todayPrediction, setTodayPrediction] = useState(null);

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

      const sorted = [...historyRes.data].sort(
        (a, b) => new Date(b.created_at || b.date) - new Date(a.created_at || a.date)
      );
      setHistory(sorted);

      // Vérifier si une prédiction a déjà été faite aujourd'hui
      const today = new Date().toDateString();
      const todayEntry = sorted.find(item =>
        new Date(item.created_at || item.date).toDateString() === today
      );
      if (todayEntry) {
        setAlreadyDoneToday(true);
        setTodayPrediction(todayEntry);
      }
    } catch (error) {
      toast.error('Erreur lors du chargement des données de la parcelle');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [id]);

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
        ...sensorData   // envoie les valeurs manuelles des sliders
      });
      setPredictionResult(response.data);
      setAlreadyDoneToday(true);
      toast.success('Diagnostic calculé avec succès !');
      fetchData();
    } catch (error) {
      if (error.response?.status === 409) {
        setAlreadyDoneToday(true);
        const existing = error.response.data?.prediction;
        if (existing) setTodayPrediction(existing);
        toast.info("Prédiction déjà effectuée aujourd'hui.");
      } else {
        toast.error('Erreur lors du diagnostic. Veuillez réessayer.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!parcelle) return (
    <Container className="py-5 text-center"><h4>Parcelle introuvable</h4></Container>
  );

  const chartData = [...history].slice(0, 10).reverse().map(item => ({
    name: new Date(item.created_at || item.date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }),
    quantite_predite: item.quantite_predite || 0
  }));

  const displayResult = predictionResult || (alreadyDoneToday && todayPrediction ? {
    quantite_predite: todayPrediction.quantite_predite,
    unite: todayPrediction.unite,
    declenchement: todayPrediction.declenchement,
    mode: todayPrediction.mode,
    prediction_date: todayPrediction.prediction_date,
  } : null);

  const handleUpdateReelle = async (id, val) => {
    try {
      await axiosInstance.patch(`/api/prediction/history/${id}/`, { quantite_reelle: parseFloat(val) });
      toast.success('Quantité réelle mise à jour !');
      setHistory(prev => prev.map(item => item.id === id ? { ...item, quantite_reelle: parseFloat(val) } : item));
    } catch (e) {
      toast.error('Erreur de mise à jour');
    }
  };

  return (
    <Container className="py-4">
      {/* Retour */}
      <div className="mb-4">
        <Link to="/parcelles" className="text-muted text-decoration-none fw-medium d-inline-flex align-items-center gap-2">
          <span>←</span> <span>Retour aux parcelles</span>
        </Link>
      </div>

      <Row className="mb-4">
        {/* Fiche identité */}
        <Col md={4} className="mb-4 mb-md-0">
          <Card className="border-0 shadow-sm rounded-4 h-100"
            style={{ background: 'linear-gradient(135deg, var(--color-sidebar) 0%, #1e293b 100%)', color: 'white' }}>
            <Card.Body className="p-4 d-flex flex-column">
              <div className="bg-white bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                style={{ width: '48px', height: '48px', fontSize: '1.5rem' }}>🌱</div>
              <h3 className="fw-bold mb-4">{parcelle.nom}</h3>
              {[
                ['Plante', parcelle.type_plante],
                ['Stade', parcelle.stade],
                ['Surface', `${parcelle.superficie_ha} ha`],
              ].map(([label, val]) => (
                <div key={label} className="mb-3 d-flex justify-content-between border-bottom border-secondary border-opacity-50 pb-2">
                  <span className="text-white-50 small text-uppercase fw-bold">{label}</span>
                  <span className="fw-medium text-capitalize">{val}</span>
                </div>
              ))}
              <div className="d-flex justify-content-between">
                <span className="text-white-50 small text-uppercase fw-bold">GPS</span>
                <span className="fw-medium small font-monospace">{parcelle.latitude}, {parcelle.longitude}</span>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Simulateur + prédiction */}
        <Col md={8}>
          <Card className="border-0 shadow-sm rounded-4 h-100">
            <Card.Header className="bg-white border-0 pt-4 px-4 pb-0">
              <div className="d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div>
                  <h5 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>
                    Simulateur d'environnement
                  </h5>
                  <p className="text-muted small mb-0">
                    Ajustez les capteurs pour lancer un diagnostic. Le système tourne aussi automatiquement à 22h00.
                  </p>
                </div>
                {alreadyDoneToday && (
                  <Badge bg="" className="bg-success bg-opacity-15 text-success rounded-pill px-3 py-2 fw-medium border-0">
                    ✓ Analyse du jour effectuée
                  </Badge>
                )}
              </div>
            </Card.Header>

            <Card.Body className="px-4 pb-4">
              {/* Info mode automatique */}
              <div className="rounded-3 p-3 mb-4 d-flex align-items-start gap-2"
                style={{ backgroundColor: '#f0f9ff', border: '1px solid #bae6fd' }}>
                <span>🤖</span>
                <p className="mb-0 small" style={{ color: '#0369a1' }}>
                  <strong>Prédiction automatique à 22h00</strong> — utilise la moyenne des capteurs des 24h précédentes
                  et la météo de demain. Ici, vous pouvez entrer des valeurs manuelles pour simuler.
                </p>
              </div>

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
                        <Form.Label className="fw-medium text-muted small">Température du sol</Form.Label>
                        <span className="fw-bold" style={{ color: '#ef4444' }}>{sensorData.temperature_sol}°C</span>
                      </div>
                      <Form.Range name="temperature_sol" min="-10" max="60" value={sensorData.temperature_sol} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={4} className="mt-3">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Azote (N)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.N}</span>
                      </div>
                      <Form.Range name="N" min="0" max="500" value={sensorData.N} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={4} className="mt-3">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Phosphore (P)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.P}</span>
                      </div>
                      <Form.Range name="P" min="0" max="300" value={sensorData.P} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                  <Col md={4} className="mt-3">
                    <Form.Group>
                      <div className="d-flex justify-content-between">
                        <Form.Label className="fw-medium text-muted small">Potassium (K)</Form.Label>
                        <span className="fw-bold text-dark">{sensorData.K}</span>
                      </div>
                      <Form.Range name="K" min="0" max="400" value={sensorData.K} onChange={handleChange} />
                    </Form.Group>
                  </Col>
                </Row>

                <div className="d-flex justify-content-end mt-4 pt-3 border-top gap-2 align-items-center">
                  {alreadyDoneToday && (
                    <span className="text-muted small me-auto">
                      ⚠️ Une analyse existe déjà aujourd'hui — relancer écrasera la prédiction actuelle.
                    </span>
                  )}
                  <Button
                    variant="success"
                    type="submit"
                    className="rounded-pill px-5 fw-medium shadow-sm"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <span className="d-flex align-items-center gap-2">
                        <span className="spinner-border spinner-border-sm" role="status" />
                        Calcul...
                      </span>
                    ) : (
                      '🔬 Lancer le diagnostic'
                    )}
                  </Button>
                </div>
              </Form>

              {/* Résultat */}
              {displayResult && (
                <Alert
                  variant={displayResult.declenchement ? 'warning' : 'info'}
                  className="mt-4 rounded-4 border-0 mb-0 shadow-sm d-flex align-items-center gap-3 p-4"
                  style={{ backgroundColor: displayResult.declenchement ? '#fffbeb' : '#f0fdfa' }}
                >
                  <div style={{ fontSize: '2rem' }}>{displayResult.declenchement ? '💧' : '✅'}</div>
                  <div className="flex-grow-1">
                    <h6 className="fw-bold mb-1" style={{ color: displayResult.declenchement ? '#b45309' : '#0f766e' }}>
                      {displayResult.declenchement ? 'Irrigation recommandée' : 'Conditions optimales'}
                    </h6>
                    {displayResult.declenchement ? (
                      <p className="mb-0 small">
                        {displayResult.unite === 'L/plante' ? 'Besoin en eau par plante :' : 'Besoin en eau par parcelle :'}
                        <strong className="ms-1" style={{ fontSize: '1.05rem' }}>
                          {Number(displayResult.quantite_predite).toFixed(2)} {displayResult.unite}
                        </strong>
                      </p>
                    ) : (
                      <p className="mb-0 small text-muted">Aucune irrigation nécessaire pour demain.</p>
                    )}
                    {displayResult.prediction_date && (
                      <p className="mb-0 mt-1" style={{ fontSize: '0.72rem', color: '#64748b' }}>
                        📅 Prévision pour le {new Date(displayResult.prediction_date).toLocaleDateString('fr-FR')}
                      </p>
                    )}
                  </div>
                  <div className="text-end border-start ps-3 d-none d-sm-block">
                    <div className="small text-muted text-uppercase mb-1">Mode</div>
                    <Badge bg="" className="bg-dark text-white rounded-pill px-2 py-1 small">
                      {displayResult.mode}
                    </Badge>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Graphique */}
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
                    <XAxis dataKey="name" tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                    <RechartsTooltip
                      cursor={{ fill: 'var(--color-bg)' }}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }}
                    />
                    <Bar dataKey="quantite_predite" name="Besoin (Litres)" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Tableau historique */}
      <Card className="border-0 shadow-sm rounded-4 overflow-hidden mb-5">
        <Card.Header className="bg-white border-0 pt-4 pb-3">
          <h5 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)' }}>Historique des prédictions</h5>
        </Card.Header>
        <Card.Body className="p-0">
          <Table responsive hover className="mb-0 align-middle">
            <thead style={{ backgroundColor: 'var(--color-bg)' }}>
              <tr>
                <th className="px-4 py-3 fw-semibold text-muted font-monospace small border-bottom-0">DATE ANALYSE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">PRÉVISION POUR</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">PRÉDITE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">RÉELLE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">DÉCLENCHEMENT</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MODE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MÉTÉO</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, i) => (
                <tr key={item.id || i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td className="px-4 py-3 text-muted small">
                    {new Date(item.created_at || item.date).toLocaleString('fr-FR')}
                  </td>
                  <td className="py-3 small fw-medium">
                    {item.prediction_date
                      ? new Date(item.prediction_date).toLocaleDateString('fr-FR')
                      : '—'}
                  </td>
                  <td className="py-3 fw-bold" style={{ color: 'var(--color-primary)' }}>
                    {Number(item.quantite_predite).toFixed(2)} {item.unite || 'L'}
                  </td>
                  <td className="py-2">
                    <Form.Control
                      type="number"
                      size="sm"
                      defaultValue={item.quantite_reelle ?? item.quantite_predite}
                      onBlur={(e) => handleUpdateReelle(item.id, e.target.value)}
                      style={{ width: '80px', display: 'inline-block' }}
                    />
                  </td>
                  <td className="py-3">
                    {item.declenchement
                      ? <Badge bg="" className="bg-warning bg-opacity-25 text-dark rounded-pill px-3 py-2 fw-medium border-0">Oui</Badge>
                      : <Badge bg="" className="bg-secondary bg-opacity-10 text-secondary rounded-pill px-3 py-2 fw-medium border-0">Non</Badge>
                    }
                  </td>
                  <td className="py-3">
                    <Badge bg="" className="bg-info bg-opacity-10 text-info rounded-pill px-3 py-2 fw-medium border-0">
                      {item.mode}
                    </Badge>
                  </td>
                  <td className="py-3 text-muted small">{item.weather_source}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-5 text-muted">
                    Aucune prédiction — la première analyse automatique aura lieu ce soir à 22h00.
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ParcelleDetail;
