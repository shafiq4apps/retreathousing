from datetime import datetime
from app import db

class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.Enum('apartment', 'house', 'commercial', name='property_types'), nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    square_footage = db.Column(db.Integer)
    rent_amount = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leases = db.relationship('Lease', backref='property', lazy=True)
    messages = db.relationship('Message', backref='property', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='property', lazy=True)
    
    @property
    def current_tenant(self):
        from app.models.lease import Lease
        active_lease = Lease.query.filter_by(property_id=self.id, status='active').first()
        return active_lease.tenant if active_lease else None
    
    def __repr__(self):
        return f'<Property {self.address}>'