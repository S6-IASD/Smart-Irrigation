import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Card, Table, Spinner, Badge, Form, InputGroup, Button, Modal, Alert } from 'react-bootstrap';
import { toast } from 'react-toastify';


const AdminCapteurs = () => {
    const [capteurs, setCapteurs] = useState([]);
    const [parcelles, setParcelles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('');

    // Modal state
    const [showModal, setShowModal] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [newApiKey, setNewApiKey] = useState(null);
    const [formData, setFormData] = useState({
        type: 'multiparameter',
        mode: 'IoT',
        device_id: '',
        parcelle: ''
    });

    useEffect(() => {  
        const fetchData = async () => {
            try {
                const [capteursRes, parcellesRes] = await Promise.all([
                    axiosInstance.get('/api/capteurs/'),
                    axiosInstance.get('/api/parcelles/')
                ]);
                const cData = capteursRes.data.results ? capteursRes.data.results : capteursRes.data;
                setCapteurs(cData);

                const pData = parcellesRes.data.results ? parcellesRes.data.results : parcellesRes.data;
                setParcelles(pData);
            } catch (error) {
                console.error("Erreur lors de la récupération des données", error);
                toast.error("Erreur de chargement des données");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleCreateCapteur = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setNewApiKey(null);
        try {
            const response = await axiosInstance.post('/api/capteurs/', formData);
            toast.success("Capteur créé avec succès !");
            
            // Re-fetch to update list
            const capteursRes = await axiosInstance.get('/api/capteurs/');
            const cData = capteursRes.data.results ? capteursRes.data.results : capteursRes.data;
            setCapteurs(cData);

            // Show API Key to admin
            if(response.data.api_key) {
                setNewApiKey(response.data.api_key);
            } else {
                setShowModal(false);
                setFormData({ type: 'multiparameter', mode: 'IoT', device_id: '', parcelle: '' });
            }
        } catch (error) {
            console.error(error);
            toast.error("Erreur lors de la création du capteur");
        } finally {
            setSubmitting(false);
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setNewApiKey(null);
        setFormData({ type: 'multiparameter', mode: 'IoT', device_id: '', parcelle: '' });
    };

    // Unique modes
    const typesStatus = [...new Set(capteurs.map(c => c.mode))].filter(Boolean);

    const filteredCapteurs = capteurs.filter((c) => {
        const searchMatches = (c.type && c.type.toLowerCase().includes(searchTerm.toLowerCase())) ||
                              (c.parcelle_nom && c.parcelle_nom.toLowerCase().includes(searchTerm.toLowerCase()));
        
        const statusMatches = statusFilter === '' || c.mode === statusFilter;
        return searchMatches && statusMatches;
    });

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
                <Spinner animation="border" variant="success" />
            </Container>
        );
    }

    return (
        <Container fluid className="py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold mb-1">Capteurs</h2>
                    <p className="text-secondary mb-0">Vue globale des capteurs IoT et manuels</p>
                </div>
                <Button variant="success" onClick={() => setShowModal(true)} className="rounded-pill px-4 shadow-sm fw-medium">
                    + Ajouter un Capteur
                </Button>
            </div>

            <Card className="border-0 shadow-sm rounded-4 overflow-hidden">
                <Card.Header className="bg-white border-bottom-0 pt-4 pb-0 px-4 d-flex gap-3 flex-wrap">
                    <InputGroup style={{ maxWidth: '350px' }}>
                        <InputGroup.Text className="bg-light border-end-0">🔍</InputGroup.Text>
                        <Form.Control
                            placeholder="Rechercher par type ou parcelle..."
                            className="bg-light border-start-0"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </InputGroup>
                    
                    <Form.Select 
                        style={{ maxWidth: '200px' }} 
                        className="bg-light"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">Tous les statuts</option>
                        {typesStatus.map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </Form.Select>
                </Card.Header>
                <Card.Body className="p-0 mt-3">
                    <Table responsive hover className="mb-0">
                        <thead className="bg-light align-middle text-secondary" style={{ fontSize: '0.85rem' }}>
                            <tr>
                                <th className="px-4 py-3 fw-medium">Type</th>
                                <th className="py-3 fw-medium">Parcelle</th>
                                <th className="py-3 fw-medium">Propriétaire</th>
                                <th className="py-3 fw-medium">Mode</th>
                                <th className="py-3 fw-medium text-end px-4">Créé le</th>
                            </tr>
                        </thead>
                        <tbody className="align-middle border-top-0">
                            {filteredCapteurs.length > 0 ? (
                                filteredCapteurs.map((c) => (
                                    <tr key={c.id}>
                                        <td className="px-4 py-3">
                                            <div className="fw-bold text-dark text-capitalize">{c.type}</div>
                                        </td>
                                        <td className="py-3">
                                            {c.parcelle_nom ? (
                                                <Badge bg="secondary" className="fw-medium px-2 py-1">
                                                    {c.parcelle_nom}
                                                </Badge>
                                            ) : (
                                                <span className="text-secondary small">Non assigné</span>
                                            )}
                                        </td>
                                        <td className="py-3 text-dark fw-medium text-capitalize">
                                            {c.user_nom || '-'}
                                        </td>
                                        <td className="py-3">
                                            <Badge 
                                                bg={c.mode === 'automatique' || c.mode === 'actif' ? 'success' : 'warning'} 
                                                className="rounded-pill px-3 py-1 fw-medium text-capitalize"
                                            >
                                                {c.mode}
                                            </Badge>
                                        </td>
                                        <td className="py-3 text-end px-4 text-secondary small">
                                            {formatDate(c.created_at)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center py-5 text-secondary">
                                        Aucun capteur ne correspond à vos filtres.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            {/* Modal de création de capteur */}
            <Modal show={showModal} onHide={handleCloseModal} centered contentClassName="border-0 rounded-4 shadow-lg">
                <Modal.Header closeButton className="border-bottom-0 pb-0 px-4 pt-4">
                    <Modal.Title className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>
                        Nouveau Capteur
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body className="px-4 pb-4">
                    {newApiKey ? (
                        <Alert variant="success" className="rounded-3 border-0 bg-success bg-opacity-10 text-success">
                            <h5 className="alert-heading fw-bold mb-2">🎉 Capteur enregistré !</h5>
                            <p className="mb-2">Voici la clé API unique générée de manière sécurisée pour ce microcontrôleur. <strong>Sauvegardez-la</strong>, elle ne sera plus affichée !</p>
                            <hr />
                            <div className="d-flex align-items-center justify-content-between gap-2 p-2 bg-white rounded border">
                                <code className="fs-6 text-dark flex-grow-1 user-select-all">{newApiKey}</code>
                                <Button size="sm" variant="outline-secondary" onClick={() => navigator.clipboard.writeText(newApiKey)}>
                                    Copier
                                </Button>
                            </div>
                            <Button variant="success" onClick={handleCloseModal} className="w-100 mt-3 rounded-pill fw-medium">
                                J'ai copié ma clé
                            </Button>
                        </Alert>
                    ) : (
                        <Form onSubmit={handleCreateCapteur}>
                            <Form.Group className="mb-3">
                                <Form.Label className="small fw-medium text-muted">Parcelle de destination</Form.Label>
                                <Form.Select 
                                    required
                                    value={formData.parcelle}
                                    onChange={(e) => setFormData({...formData, parcelle: e.target.value})}
                                    className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                                >
                                    <option value="">Sélectionnez une parcelle</option>
                                    {parcelles.map(p => (
                                        <option key={p.id} value={p.id}>{p.nom} (Propriétaire: {p.user_nom})</option>
                                    ))}
                                </Form.Select>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label className="small fw-medium text-muted">Device ID (Hardware MAC ou Custom)</Form.Label>
                                <Form.Control 
                                    type="text" 
                                    required 
                                    placeholder="ex: ESP32_PARCELLE_A"
                                    value={formData.device_id}
                                    onChange={(e) => setFormData({...formData, device_id: e.target.value})}
                                    className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                                />
                                <Form.Text className="text-muted" style={{ fontSize: '0.75rem' }}>
                                    Ce Device ID servira à identifier la source durant l'ingestion IoT `/api/iot/ingest/`.
                                </Form.Text>
                            </Form.Group>

                            <div className="d-flex gap-3 mb-4">
                                <Form.Group className="flex-grow-1">
                                    <Form.Label className="small fw-medium text-muted">Mode</Form.Label>
                                    <Form.Select 
                                        value={formData.mode}
                                        onChange={(e) => setFormData({...formData, mode: e.target.value})}
                                        className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                                    >
                                        <option value="IoT">IoT (Automatique)</option>
                                        <option value="manuel">Manuel</option>
                                    </Form.Select>
                                </Form.Group>

                                <Form.Group className="flex-grow-1">
                                    <Form.Label className="small fw-medium text-muted">Type de capteur</Form.Label>
                                    <Form.Control 
                                        type="text"
                                        value={formData.type}
                                        onChange={(e) => setFormData({...formData, type: e.target.value})}
                                        className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}
                                        placeholder="Multiparamètre"
                                    />
                                </Form.Group>
                            </div>

                            <Button variant="success" type="submit" className="w-100 rounded-pill py-2 fw-medium" disabled={submitting}>
                                {submitting ? 'Enregistrement...' : 'Enregistrer et générer la clé'}
                            </Button>
                        </Form>
                    )}
                </Modal.Body>
            </Modal>
        </Container>
    );
};

export default AdminCapteurs;
