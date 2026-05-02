import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Card, Table, Spinner, Badge, Form, InputGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';

const AdminUsers = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await axiosInstance.get('/api/auth/admin/users/');
                setUsers(response.data);
            } catch (error) {
                console.error("Erreur lors de la récupération des utilisateurs", error);
                toast.error("Erreur de chargement des utilisateurs");
            } finally {
                setLoading(false);
            }
        };

        fetchUsers();
    }, []);

    const filteredUsers = users.filter((user) =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) || 
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const formatDate = (dateString) => {
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
                    <h2 className="fw-bold mb-1">Utilisateurs</h2>
                    <p className="text-secondary mb-0">Gestion des comptes de la plateforme</p>
                </div>
            </div>

            <Card className="border-0 shadow-sm rounded-4 overflow-hidden">
                <Card.Header className="bg-white border-bottom-0 pt-4 pb-0 px-4">
                    <InputGroup className="mb-3" style={{ maxWidth: '400px' }}>
                        <InputGroup.Text className="bg-light border-end-0">🔍</InputGroup.Text>
                        <Form.Control
                            placeholder="Rechercher un utilisateur (nom, email)..."
                            className="bg-light border-start-0"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </InputGroup>
                </Card.Header>
                <Card.Body className="p-0">
                    <Table responsive hover className="mb-0">
                        <thead className="bg-light align-middle text-secondary" style={{ fontSize: '0.85rem' }}>
                            <tr>
                                <th className="px-4 py-3 fw-medium">Utilisateur</th>
                                <th className="py-3 fw-medium">Role</th>
                                <th className="py-3 fw-medium">Contact</th>
                                <th className="py-3 fw-medium text-end px-4">Inscrit le</th>
                            </tr>
                        </thead>
                        <tbody className="align-middle border-top-0">
                            {filteredUsers.length > 0 ? (
                                filteredUsers.map((user) => (
                                    <tr key={user.id}>
                                        <td className="px-4 py-3">
                                            <div className="d-flex align-items-center gap-3">
                                                <div 
                                                    className="rounded-circle d-flex align-items-center justify-content-center fw-bold text-white shadow-sm"
                                                    style={{ 
                                                        width: '40px', height: '40px', 
                                                        backgroundColor: user.role === 'admin' ? '#ef4444' : '#16a34a' 
                                                    }}
                                                >
                                                    {user.username.charAt(0).toUpperCase()}
                                                </div>
                                                <div>
                                                    <div className="fw-bold text-dark">{user.username}</div>
                                                    <div className="text-secondary small">{user.email}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-3">
                                            <Badge bg={user.role === 'admin' ? 'danger' : 'success'} className="rounded-pill px-3 py-2 fw-medium">
                                                {user.role === 'admin' ? 'Administrateur' : 'Agriculteur'}
                                            </Badge>
                                        </td>
                                        <td className="py-3 text-secondary">
                                            {user.phone || '-'}
                                        </td>
                                        <td className="py-3 text-end px-4 text-secondary small">
                                            {formatDate(user.created_at)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="text-center py-5 text-secondary">
                                        Aucun utilisateur trouvé.
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

export default AdminUsers;
