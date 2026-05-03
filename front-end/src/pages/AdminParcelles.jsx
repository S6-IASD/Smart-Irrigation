import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Card, Table, Spinner, Badge, Form, InputGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';

const AdminParcelles = () => {
    const [parcelles, setParcelles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [typeFilter, setTypeFilter] = useState('');

    useEffect(() => {
        const fetchParcelles = async () => {
            try {
                const response = await axiosInstance.get('/api/parcelles/');
                // Assuming DRF returns the array directly or in response.data.results
                const data = response.data.results ? response.data.results : response.data;
                setParcelles(data);
            } catch (error) {
                console.error("Erreur lors de la récupération des parcelles", error);
                toast.error("Erreur de chargement des parcelles");
            } finally {
                setLoading(false);
            }
        };

        fetchParcelles();
    }, []);

    // Extract unique plant types for the filter dropdown
    const typesPlante = [...new Set(parcelles.map(p => p.type_plante))].filter(Boolean);

    const filteredParcelles = parcelles.filter((p) => {
        const matchesSearch = p.nom.toLowerCase().includes(searchTerm.toLowerCase()) || 
                              (p.coordonnees && p.coordonnees.toLowerCase().includes(searchTerm.toLowerCase()));
        const matchesType = typeFilter === '' || p.type_plante === typeFilter;
        return matchesSearch && matchesType;
    });

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit', month: 'short', year: 'numeric'
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
                    <h2 className="fw-bold mb-1">Parcelles</h2>
                    <p className="text-secondary mb-0">Vue globale de toutes les parcelles de la plateforme</p>
                </div>
            </div>

            <Card className="border-0 shadow-sm rounded-4 overflow-hidden">
                <Card.Header className="bg-white border-bottom-0 pt-4 pb-0 px-4 d-flex gap-3 flex-wrap">
                    <InputGroup style={{ maxWidth: '350px' }}>
                        <InputGroup.Text className="bg-light border-end-0">🔍</InputGroup.Text>
                        <Form.Control
                            placeholder="Rechercher par nom..."
                            className="bg-light border-start-0"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </InputGroup>
                    
                    <Form.Select 
                        style={{ maxWidth: '200px' }} 
                        className="bg-light"
                        value={typeFilter}
                        onChange={(e) => setTypeFilter(e.target.value)}
                    >
                        <option value="">Tous les types</option>
                        {typesPlante.map(type => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </Form.Select>
                </Card.Header>
                <Card.Body className="p-0 mt-3">
                    <Table responsive hover className="mb-0">
                        <thead className="bg-light align-middle text-secondary" style={{ fontSize: '0.85rem' }}>
                            <tr>
                                <th className="px-4 py-3 fw-medium">Nom de la parcelle</th>
                                <th className="py-3 fw-medium">Surface</th>
                                <th className="py-3 fw-medium">Culture</th>
                                <th className="py-3 fw-medium">Stade</th>
                                <th className="py-3 fw-medium">Propriétaire</th>
                                <th className="py-3 fw-medium text-end px-4">Créée le</th>
                            </tr>
                        </thead>
                        <tbody className="align-middle border-top-0">
                            {filteredParcelles.length > 0 ? (
                                filteredParcelles.map((p) => (
                                    <tr key={p.id}>
                                        <td className="px-4 py-3">
                                            <div className="fw-bold text-dark">{p.nom}</div>
                                        </td>
                                        <td className="py-3 text-secondary">
                                            {p.surface} ha
                                        </td>
                                        <td className="py-3">
                                            <Badge bg="success" bg-opacity="10" className="text-success bg-success bg-opacity-10 rounded-pill px-3 py-1 fw-medium border border-success border-opacity-25" style={{backgroundColor: '#dcfce7', color: '#166534'}}>
                                                {p.type_plante}
                                            </Badge>
                                        </td>
                                        <td className="py-3 text-secondary small text-capitalize">
                                            {p.stade_croissance}
                                        </td>
                                        <td className="py-3 text-dark fw-medium text-capitalize">
                                            {p.user_nom || '-'}
                                        </td>
                                        <td className="py-3 text-end px-4 text-secondary small">
                                            {formatDate(p.created_at)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center py-5 text-secondary">
                                        Aucune parcelle ne correspond à vos filtres.
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

export default AdminParcelles;
