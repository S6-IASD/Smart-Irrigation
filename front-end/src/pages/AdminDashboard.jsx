import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Row, Col, Card, Table, Spinner, Badge } from 'react-bootstrap';
import { toast } from 'react-toastify';

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axiosInstance.get('/api/auth/admin/dashboard/');
                setStats(response.data);
            } catch (error) {
                console.error("Erreur lors de la récupération des statistiques admin", error);
                toast.error("Erreur de chargement du dashboard admin");
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
                <Spinner animation="border" variant="success" />
            </Container>
        );
    }

    if (!stats) return null;

    const kpiCards = [
        { title: 'Utilisateurs', value: stats.total_users, sub: `+${stats.new_users_30d} ce mois`, icon: '👥', color: '#3b82f6' },
        { title: 'Parcelles', value: stats.total_parcelles, sub: `+${stats.new_parcelles_30d} ce mois`, icon: '🌱', color: '#10b981' },
        { title: 'Capteurs', value: stats.total_capteurs, sub: `${stats.lectures_7d} lectures (7j)`, icon: '🎛️', color: '#8b5cf6' },
        { title: 'Prédictions', value: stats.total_predictions, sub: `+${stats.predictions_30d} ce mois`, icon: '🤖', color: '#f59e0b' },
    ];

    const getStatusVariant = (status) => {
        switch (status) {
            case 'success': return 'success';
            case 'pending': return 'warning';
            case 'failed': return 'danger';
            default: return 'secondary';
        }
    };

    return (
        <Container fluid className="py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold mb-1">Vue d'ensemble Admin</h2>
                    <p className="text-secondary mb-0">Statistiques globales de la plateforme Smart Irrigation</p>
                </div>
            </div>

            <Row className="g-4 mb-4">
                {kpiCards.map((kpi, idx) => (
                    <Col key={idx} xs={12} sm={6} lg={3}>
                        <Card className="border-0 shadow-sm h-100 rounded-4">
                            <Card.Body className="d-flex align-items-center g-3">
                                <div 
                                    className="d-flex align-items-center justify-content-center rounded-3 me-3" 
                                    style={{ width: '56px', height: '56px', backgroundColor: `${kpi.color}20`, color: kpi.color, fontSize: '1.5rem' }}
                                >
                                    {kpi.icon}
                                </div>
                                <div>
                                    <h6 className="text-uppercase text-secondary mb-1" style={{ fontSize: '0.75rem', letterSpacing: '0.05em', fontWeight: '600' }}>{kpi.title}</h6>
                                    <h3 className="fw-bold mb-0 text-dark">{kpi.value}</h3>
                                    <small className="text-secondary">{kpi.sub}</small>
                                </div>
                            </Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>

            <Row className="g-4">
                <Col lg={6}>
                    <Card className="border-0 shadow-sm rounded-4 h-100">
                        <Card.Header className="bg-white border-0 pt-4 pb-2 px-4">
                            <h5 className="fw-bold mb-0">Statuts des prédictions</h5>
                        </Card.Header>
                        <Card.Body className="px-4">
                            <div className="d-flex flex-column gap-3">
                                <div>
                                    <div className="d-flex justify-content-between mb-1">
                                        <span className="text-secondary fw-medium"><span className="text-success me-2">●</span>Succès</span>
                                        <span className="fw-bold">{stats.predictions_success}</span>
                                    </div>
                                    <div className="progress" style={{ height: '8px' }}>
                                        <div className="progress-bar bg-success" style={{ width: `${stats.total_predictions ? (stats.predictions_success / stats.total_predictions) * 100 : 0}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="d-flex justify-content-between mb-1">
                                        <span className="text-secondary fw-medium"><span className="text-warning me-2">●</span>En attente</span>
                                        <span className="fw-bold">{stats.predictions_pending}</span>
                                    </div>
                                    <div className="progress" style={{ height: '8px' }}>
                                        <div className="progress-bar bg-warning" style={{ width: `${stats.total_predictions ? (stats.predictions_pending / stats.total_predictions) * 100 : 0}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="d-flex justify-content-between mb-1">
                                        <span className="text-secondary fw-medium"><span className="text-danger me-2">●</span>Échouées</span>
                                        <span className="fw-bold">{stats.predictions_failed}</span>
                                    </div>
                                    <div className="progress" style={{ height: '8px' }}>
                                        <div className="progress-bar bg-danger" style={{ width: `${stats.total_predictions ? (stats.predictions_failed / stats.total_predictions) * 100 : 0}%` }}></div>
                                    </div>
                                </div>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
                <Col lg={6}>
                    <Card className="border-0 shadow-sm rounded-4 h-100">
                        <Card.Header className="bg-white border-0 pt-4 pb-2 px-4">
                            <h5 className="fw-bold mb-0">Indicateurs clés</h5>
                        </Card.Header>
                        <Card.Body className="px-4 d-flex align-items-center justify-content-center">
                           <div className="text-center">
                               <div className="mb-2" style={{ fontSize: '4rem', color: '#ef4444' }}>💧</div>
                               <h2 className="fw-bold mb-0">{stats.trigger_rate}%</h2>
                               <p className="text-secondary mb-0">Taux global de déclenchement d'irrigation</p>
                               <Badge bg="danger" className="mt-2 px-3 py-2 rounded-pill">
                                   {stats.predictions_triggered} déclenchements
                               </Badge>
                           </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default AdminDashboard;
