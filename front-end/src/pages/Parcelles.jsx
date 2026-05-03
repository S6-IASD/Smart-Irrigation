import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Modal, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axiosInstance from '../api/axios';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet icons issue in bundlers
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Map Interactor Component
function LocationMarker({ formData, setFormData }) {
  useMapEvents({
    async click(e) {
      const { lat, lng } = e.latlng;
      let newFormData = { ...formData, latitude: lat.toFixed(6), longitude: lng.toFixed(6) };
      
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        if (response.ok) {
          const data = await response.json();
          const ville = data.address.city || data.address.town || data.address.village || data.address.county || data.address.state || 'Inconnue';
          newFormData.ville = ville;
        }
      } catch (err) {
        console.error("Geocoding error", err);
      }
      setFormData(newFormData);
    },
  });

  return formData.latitude && formData.longitude ? (
    <Marker position={[parseFloat(formData.latitude), parseFloat(formData.longitude)]} />
  ) : null;
}

const Parcelles = () => {
  const [parcelles, setParcelles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    nom: '',
    superficie_ha: '',
    type_plante: 'Blé',
    stade: 'jeune',
    latitude: '',
    longitude: '',
    ville: ''
  });

  const plantesDict = [
    'Blé', 'Maïs', 'Orge', 'Soja', 'Riz', 'Sorgo', 'Millet', 
    'Avoine', 'Seigle', 'Tournesol', 'Colza', 'Arachide', 
    'Coton', 'Betterave', 'Canne', 'Pomme de terre', 'Manioc', 
    'Tomate', 'Oignon', 'Ail', 'Carotte', 'Chou', 'Laitue', 
    'Vigne', 'Pommier', 'Oranger', 'Manguier', 'Bananier', 
    'Café', 'Cacao'
  ];

  const fetchParcelles = async () => {
    try {
      const response = await axiosInstance.get('/api/parcelles/');
      setParcelles(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des parcelles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchParcelles();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Center map dynamically on France or user's rough geo if possible (defaulting to North Africa / France)
  const defaultMapCenter = [33.5731, -7.5898]; // Casablanca Default
  const mapZoom = 6;

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await axiosInstance.post('/api/parcelles/', {
        ...formData,
        superficie_ha: parseFloat(formData.superficie_ha),
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude)
        // ville is already a string
      });
      toast.success('Parcelle créée avec succès !');
      setShowModal(false);
      setFormData({ nom: '', superficie_ha: '', type_plante: 'Blé', stade: 'jeune', latitude: '', longitude: '', ville: '' });
      fetchParcelles();
    } catch (error) {
      toast.error('Erreur lors de la création de la parcelle');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, nom) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer la parcelle "${nom}" ?`)) {
      try {
        await axiosInstance.delete(`/api/parcelles/${id}/`);
        toast.success(`Parcelle "${nom}" supprimée`);
        setParcelles(parcelles.filter(p => p.id !== id));
      } catch (error) {
        toast.error('Erreur lors de la suppression');
      }
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-5">
        <div>
          <h2 className="fw-bold mb-0" style={{ color: 'var(--color-sidebar)' }}>Mes Parcelles</h2>
          <p className="text-muted mb-0">Gérez vos zones de culture et capteurs.</p>
        </div>
        <Button variant="success" onClick={() => setShowModal(true)} className="rounded-pill px-4 shadow-sm fw-medium">
          + Nouvelle Parcelle
        </Button>
      </div>

      <Row>
        {parcelles.map((parcelle) => (
          <Col md={6} lg={4} key={parcelle.id} className="mb-4">
            <Card className="border-0 p-2 hover-card h-100">
              <Card.Body className="d-flex flex-column">
                <div className="d-flex justify-content-between align-items-start mb-4">
                  <div>
                    <Card.Title className="fw-bold mb-1" style={{ color: 'var(--color-sidebar)', fontSize: '1.2rem' }}>{parcelle.nom}</Card.Title>
                    <Badge bg="" className="bg-success bg-opacity-10 text-success fw-medium rounded-pill px-2 py-1 border-0 me-2">{parcelle.superficie_ha} ha</Badge>
                    {parcelle.ville && (
                        <small className="text-secondary">📍 {parcelle.ville}</small>
                    )}
                  </div>
                  <div className="bg-light rounded-circle d-flex align-items-center justify-content-center border" style={{ width: '40px', height: '40px', fontSize: '1.2rem' }}>🌿</div>
                </div>
                
                <div className="mb-4">
                  <div className="d-flex justify-content-between border-bottom py-2">
                    <span className="text-muted small">Plante</span>
                    <span className="fw-medium">{parcelle.type_plante}</span>
                  </div>
                  <div className="d-flex justify-content-between py-2">
                    <span className="text-muted small">Stade végétatif</span>
                    <span className="fw-medium text-capitalize">{parcelle.stade}</span>
                  </div>
                </div>
                
                <div className="d-flex justify-content-between mt-auto gap-2">
                  <Button as={Link} to={`/parcelles/${parcelle.id}`} variant="outline-success" size="sm" className="rounded-pill px-3 flex-grow-1 fw-medium">
                    Analyser
                  </Button>
                  <Button variant="outline-danger" size="sm" onClick={() => handleDelete(parcelle.id, parcelle.nom)} className="rounded-pill px-3">
                    Supprimer
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
        {parcelles.length === 0 && (
          <Col>
            <div className="text-center py-5 bg-white border border-light rounded-4 shadow-sm" style={{ backgroundColor: 'var(--color-surface)' }}>
              <div className="fs-1 mb-3">🌱</div>
              <h4 className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>Aucune parcelle</h4>
              <p className="text-muted mb-4">Commencez par délimiter vos zones de culture.</p>
              <Button variant="success" onClick={() => setShowModal(true)} className="rounded-pill px-4 shadow-sm fw-medium">
                Créer la première
              </Button>
            </div>
          </Col>
        )}
      </Row>

      {/* Modal Création */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered size="lg" contentClassName="border-0 rounded-4 shadow-lg">
        <Modal.Header closeButton className="border-bottom-0 pb-0 px-4 pt-4">
          <Modal.Title className="fw-bold" style={{ color: 'var(--color-sidebar)' }}>Nouvelle Parcelle</Modal.Title>
        </Modal.Header>
        <Modal.Body className="px-4 pb-4">
          <Form onSubmit={handleCreate}>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium text-muted">Nom de la parcelle</Form.Label>
              <Form.Control type="text" name="nom" required value={formData.nom} onChange={handleChange} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }} />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label className="small fw-medium text-muted">Superficie (ha)</Form.Label>
                  <Form.Control type="number" step="0.01" name="superficie_ha" required value={formData.superficie_ha} onChange={handleChange} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }} />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label className="small fw-medium text-muted">Stade</Form.Label>
                  <Form.Select name="stade" value={formData.stade} onChange={handleChange} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}>
                    <option value="jeune">Jeune</option>
                    <option value="mature">Mature</option>
                    <option value="fin">Fin</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium text-muted">Type de plante</Form.Label>
              <Form.Select name="type_plante" value={formData.type_plante} onChange={handleChange} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }}>
                {plantesDict.map(plante => (
                  <option key={plante} value={plante}>{plante}</option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <div className="mb-4 rounded overflow-hidden shadow-sm border border-light" style={{ height: '250px', position: 'relative' }}>
              <div className="position-absolute top-0 start-0 w-100 p-2 z-1 bg-white bg-opacity-75" style={{ zIndex: 1000}}>
                <small className="fw-bold text-success text-center d-block">🗺️ Cliquez sur la carte pour définir la géolocalisation et la ville</small>
              </div>
              <MapContainer center={defaultMapCenter} zoom={mapZoom} style={{ height: '100%', width: '100%', zIndex: 1 }}>
                <TileLayer
                  attribution='&copy; <a href="http://osm.org/copyright">OSM</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationMarker formData={formData} setFormData={setFormData} />
              </MapContainer>
            </div>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label className="small fw-medium text-muted">Latitude</Form.Label>
                  <Form.Control type="text" readOnly name="latitude" required value={formData.latitude} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }} />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-4">
                  <Form.Label className="small fw-medium text-muted">Longitude</Form.Label>
                  <Form.Control type="text" readOnly name="longitude" required value={formData.longitude} className="bg-light border-0 py-2" style={{ borderRadius: '8px' }} />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-4">
                  <Form.Label className="small fw-medium text-muted">Ville</Form.Label>
                  <Form.Control type="text" name="ville" required value={formData.ville} onChange={handleChange} placeholder="-" className="bg-light border-0 py-2" style={{ borderRadius: '8px' }} />
                </Form.Group>
              </Col>
            </Row>
            <Button variant="success" type="submit" className="w-100 rounded-pill py-2 fw-medium" disabled={submitting}>
              {submitting ? 'Création...' : 'Créer la parcelle'}
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default Parcelles;
