import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Form } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import axiosInstance from '../api/axios';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';

const Historique = () => {
  const [history, setHistory] = useState([]);
  const [parcelles, setParcelles] = useState([]);
  const [loading, setLoading] = useState(true);

  const [filterParcelle, setFilterParcelle] = useState('all');
  const [filterDeclenchement, setFilterDeclenchement] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [histRes, parcRes] = await Promise.all([
          axiosInstance.get('/api/prediction/history/'),
          axiosInstance.get('/api/parcelles/')
        ]);
        const sortedHistory = histRes.data.sort((a, b) => new Date(b.created_at || b.date) - new Date(a.created_at || a.date));
        setHistory(sortedHistory);
        setParcelles(parcRes.data);
      } catch (error) {
        toast.error('Erreur lors du chargement de l\'historique');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  const filteredHistory = history.filter(item => {
    const matchParcelle = filterParcelle === 'all' || item.parcelle === filterParcelle || item.parcelle_nom === filterParcelle || item.parcelle_id === filterParcelle;
    
    let matchDeclenchement = true;
    if (filterDeclenchement === 'oui') matchDeclenchement = item.declenchement === true;
    if (filterDeclenchement === 'non') matchDeclenchement = item.declenchement === false;

    return matchParcelle && matchDeclenchement;
  });

  const handleUpdateReelle = async (id, val) => {
    try {
      await axiosInstance.patch(`/api/prediction/history/${id}/`, { quantite_reelle: parseFloat(val) });
      toast.success('Quantité réelle mise à jour !');
      setHistory(prev => prev.map(item => item.id === id ? { ...item, quantite_reelle: parseFloat(val) } : item));
    } catch (e) {
      toast.error('Erreur de mise à jour');
    }
  };

  const chartData = [...filteredHistory].slice(0, 50).reverse().map(item => ({
    name: new Date(item.created_at || item.date).toLocaleDateString(),
    quantite_predite: item.quantite_predite || 0
  }));

  return (
    <Container className="py-4">
      <div className="mb-4 d-flex align-items-center justify-content-between">
        <div>
          <h2 className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)' }}>Historique Global</h2>
          <p className="text-muted mb-0">Analysez toutes les prédictions du système ML.</p>
        </div>
      </div>

      {/* Filters */}
      <Card className="border-0 shadow-sm rounded-4 mb-4" style={{ backgroundColor: 'white' }}>
        <Card.Body className="p-4">
          <Row className="gy-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label className="fw-medium text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Filtrer par Parcelle</Form.Label>
                <Form.Select 
                  value={filterParcelle} 
                  onChange={(e) => setFilterParcelle(e.target.value)}
                  className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                >
                  <option value="all">Toutes les parcelles</option>
                  {parcelles.map(p => (
                    <option key={p.id} value={p.id}>{p.nom}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
                <Form.Label className="fw-medium text-muted small text-uppercase" style={{ letterSpacing: '0.5px' }}>Déclenchement</Form.Label>
                <Form.Select 
                  value={filterDeclenchement} 
                  onChange={(e) => setFilterDeclenchement(e.target.value)}
                  className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                >
                  <option value="all">Tous les états</option>
                  <option value="oui">Oui (Irrigué)</option>
                  <option value="non">Non (Pas d'irrigation)</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Chart */}
      <Card className="border-0 shadow-sm rounded-4 mb-4 p-2">
        <Card.Body>
          <Card.Title className="fw-bold mb-4" style={{ fontSize: '1.1rem', color: 'var(--color-sidebar)' }}>
            Évolution des besoins hydriques (50 derniers enregistrements max)
          </Card.Title>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{fontSize: 10}} tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} tick={{fontSize: 12}} />
                <RechartsTooltip cursor={{stroke: 'var(--color-border)'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)'}} />
                <Line type="monotone" dataKey="quantite_predite" name="Besoin (L)" stroke="#16a34a" strokeWidth={3} dot={{r: 0}} activeDot={{r: 6, strokeWidth: 0}} fillOpacity={1} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card.Body>
      </Card>

      {/* Table */}
      <Card className="border-0 shadow-sm rounded-4 overflow-hidden mb-5">
        <Card.Header className="bg-white border-0 pt-4 pb-3 d-flex justify-content-between align-items-center">
          <h5 className="mb-0 fw-bold" style={{ color: 'var(--color-sidebar)' }}>Base de données</h5>
          <span className="text-muted small fw-medium">{filteredHistory.length} résultat(s)</span>
        </Card.Header>
        <Card.Body className="p-0">
          <Table responsive hover className="mb-0 align-middle">
            <thead style={{ backgroundColor: 'var(--color-bg)' }}>
              <tr>
                <th className="px-4 py-3 fw-semibold text-muted font-monospace small border-bottom-0">DATE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">PARCELLE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">PRÉDITE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">RÉELLE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">STATUT</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">MODE</th>
                <th className="py-3 fw-semibold text-muted font-monospace small border-bottom-0">SOURCE MÉTÉO</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.map((item, i) => (
                <tr key={item.id || i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td className="px-4 py-3 text-muted small">{new Date(item.created_at || item.date).toLocaleString()}</td>
                  <td className="py-3 fw-medium text-dark">
                    {parcelles.find(p => p.id === item.parcelle || p.id === item.parcelle_id)?.nom || item.parcelle_nom || item.parcelle}
                  </td>
                  <td className="py-3 fw-bold" style={{ color: 'var(--color-primary)' }}>{item.quantite_predite?.toFixed(2)} {item.unite || 'L'}</td>
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
                    {item.declenchement ? (
                      <Badge bg="" className="bg-success bg-opacity-25 text-success rounded-pill px-3 py-2 fw-medium border-0">Irrigué</Badge>
                    ) : (
                      <Badge bg="" className="bg-secondary bg-opacity-10 text-secondary rounded-pill px-3 py-2 fw-medium border-0">Non</Badge>
                    )}
                  </td>
                  <td className="py-3"><Badge bg="" className="bg-info bg-opacity-10 text-info rounded-pill px-3 py-2 fw-medium border-0">{item.mode}</Badge></td>
                  <td className="py-3 text-muted small">{item.weather_source}</td>
                </tr>
              ))}
              {filteredHistory.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-5 text-muted">
                    Aucun résultat correspondant à vos filtres.
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

export default Historique;
