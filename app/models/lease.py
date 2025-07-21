from datetime import datetime
from app import db

class Lease(db.Model):
    __tablename__ = 'leases'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    security_deposit = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum('active', 'expired', 'terminated', name='lease_statuses'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='lease', lazy=True)
    
    @property
    def is_active(self):
        return self.status == 'active' and self.start_date <= datetime.now().date() <= self.end_date
    
    def __repr__(self):
        return f'<Lease {self.tenant.full_name} - {self.property.address}>'