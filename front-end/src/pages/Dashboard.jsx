import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts';
import axiosInstance from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [stats, setStats] = useState({
    nbParcelles: 0,
    nbPredictions: 0,
    nbIrrigations: 0
  });
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [waterData, setWaterData] = useState([]);
  const [triggerData, setTriggerData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [parcellesRes, historyRes] = await Promise.all([
          axiosInstance.get('/api/parcelles/'),
          axiosInstance.get('/api/prediction/history/')
        ]);

        const parcelles = parcellesRes.data;
        const history = historyRes.data;

        const nbParcelles = parcelles.length;
        const nbPredictions = history.length;
        const nbIrrigations = history.filter(p => p.declenchement).length;

        setStats({ nbParcelles, nbPredictions, nbIrrigations });

        const sortedHistory = [...history].sort((a, b) => new Date(b.created_at || b.date) - new Date(a.created_at || a.date));
        setRecentPredictions(sortedHistory.slice(0, 5));

        const last10 = sortedHistory.slice(0, 10).reverse();
        
        const wData = last10.map(item => ({
          name: new Date(item.created_at || item.date).toLocaleDateString() + ' ' + new Date(item.created_at || item.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
          eau_litres: item.eau_litres || 0
        }));

        const tData = last10.map(item => ({
          name: new Date(item.created_at || item.date).toLocaleDateString(),
          declenchement: item.declenchement ? 1 : 0
        }));

        setWaterData(wData);
        setTriggerData(tData);

      } catch (error) {
        console.error("Error fetching dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <Container className="py-4">
      <div className="mb-4 d-flex align-items-center justify-content-between">
        <div>
          <h2 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>Tableau de bord</h2>
          <p className="text-muted mb-0">Surveillez l'activité globale de vos parcelles.</p>
        </div>
      </div>
      
      {/* Cards Stats */}
      <Row className="mb-4">
        <Col md={4} className="mb-3 mb-md-0">
          <Card className="hover-card h-100 p-2">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <h6 className="text-muted text-uppercase fw-bold mb-0" style={{ fontSize: '0.8rem', letterSpacing: '0.5px' }}>Parcelles</h6>
                <span className="bg-success bg-opacity-10 text-success rounded px-2 py-1 small">Total</span>
              </div>
              <h2 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)', fontSize: '2.5rem' }}>{stats.nbParcelles}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-3 mb-md-0">
          <Card className="hover-card h-100 p-2">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <h6 className="text-muted text-uppercase fw-bold mb-0" style={{ fontSize: '0.8rem', letterSpacing: '0.5px' }}>Prédictions</h6>
                <span className="bg-primary bg-opacity-10 text-primary rounded px-2 py-1 small">Total</span>
              </div>
              <h2 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)', fontSize: '2.5rem' }}>{stats.nbPredictions}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="hover-card h-100 p-2">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <h6 className="text-muted text-uppercase fw-bold mb-0" style={{ fontSize: '0.8rem', letterSpacing: '0.5px' }}>Irrigations</h6>
                <span className="bg-warning bg-opacity-10 text-warning rounded px-2 py-1 small">Déclenchées</span>
              </div>
              <h2 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)', fontSize: '2.5rem' }}>{stats.nbIrrigations}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col lg={6} className="mb-4 mb-lg-0">
          <Card className="h-100 p-2">
            <Card.Body>
              <Card.Title className="fw-bold mb-4" style={{ fontSize: '1.1rem', color: 'var(--color-sidebar)' }}>Volume d'eau (10 dernières prédictions)</Card.Title>
              <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={waterData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{fontSize: 10}} tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} tick={{fontSize: 12}} />
                    <RechartsTooltip cursor={{fill: 'var(--color-bg)'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)'}} />
                    <Bar dataKey="eau_litres" name="Eau (Litres)" fill="#16a34a" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className="h-100 p-2">
            <Card.Body>
              <Card.Title className="fw-bold mb-4" style={{ fontSize: '1.1rem', color: 'var(--color-sidebar)' }}>Historique des déclenchements</Card.Title>
              <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <LineChart data={triggerData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{fontSize: 10}} tickLine={false} axisLine={false} />
                    <YAxis ticks={[0, 1]} domain={[0, 1]} tickLine={false} axisLine={false} tick={{fontSize: 12}} tickFormatter={val => val === 1 ? 'Oui' : 'Non'} />
                    <RechartsTooltip cursor={{stroke: 'var(--color-border)'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)'}} />
                    <Line type="stepAfter" dataKey="declenchement" name="Déclenchement" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6', strokeWidth: 0}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card className="overflow-hidden p-2">
        <Card.Header className="bg-white border-0 pt-4 pb-3">
          <h5 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)' }}>Activité Récente</h5>
        </Card.Header>
        <Card.Body className="p-0">
          <Table responsive hover className="mb-0 align-middle">
            <thead style={{ backgroundColor: 'var(--color-bg)' }}>
              <tr>
                <th className="px-4 py-3 fw-semibold text-muted font-monospace small border-bottom-0">DATE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">PARCELLE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">EAU (L)</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">STATUT</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MODE</th>
              </tr>
            </thead>
            <tbody>
              {recentPredictions.map((pred, i) => (
                <tr key={pred.id || i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td className="px-4 py-3 text-muted small">{new Date(pred.created_at || pred.date).toLocaleString()}</td>
                  <td className="py-3 fw-medium">{pred.parcelle_nom || pred.parcelle}</td>
                  <td className="py-3 fw-bold" style={{ color: 'var(--color-primary)' }}>{pred.eau_litres?.toFixed(2)} L</td>
                  <td className="py-3">
                    {pred.declenchement ? (
                      <Badge bg="" className="bg-success bg-opacity-25 text-success rounded-pill px-3 py-2 fw-medium border-0">Irrigué</Badge>
                    ) : (
                      <Badge bg="" className="bg-secondary bg-opacity-10 text-secondary rounded-pill px-3 py-2 fw-medium border-0">Non</Badge>
                    )}
                  </td>
                  <td className="py-3"><Badge bg="" className="bg-info bg-opacity-10 text-info rounded-pill px-3 py-2 fw-medium border-0">{pred.mode}</Badge></td>
                </tr>
              ))}
              {recentPredictions.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted">Aucune prédiction récente</td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Dashboard;
