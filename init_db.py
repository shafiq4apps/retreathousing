#!/usr/bin/env python3
"""
Database initialization script for Retreat Housing Property Management Portal
Creates database tables and seeds with sample data
"""

import os
from datetime import datetime, date
from app import create_app, db
from app.models.user import User
from app.models.property import Property
from app.models.lease import Lease
from app.models.document import Document
from app.models.message import Message
from app.models.maintenance_request import MaintenanceRequest

def create_sample_data():
    """Create sample data for development and testing"""
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@retreathousing.com',
        first_name='Admin',
        last_name='User',
        phone='(555) 123-4567',
        role='admin'
    )
    admin.set_password('password')
    db.session.add(admin)
    
    # Create sample tenants
    tenant1 = User(
        username='tenant1',
        email='john.doe@example.com',
        first_name='John',
        last_name='Doe',
        phone='(555) 234-5678',
        role='tenant'
    )
    tenant1.set_password('password')
    db.session.add(tenant1)
    
    tenant2 = User(
        username='tenant2',
        email='jane.smith@example.com',
        first_name='Jane',
        last_name='Smith',
        phone='(555) 345-6789',
        role='tenant'
    )
    tenant2.set_password('password')
    db.session.add(tenant2)
    
    # Commit users first to get IDs
    db.session.commit()
    
    # Create sample properties
    property1 = Property(
        owner_id=admin.id,
        address='123 Main Street, Apt 2A\nDowntown, CA 90210',
        property_type='apartment',
        bedrooms=2,
        bathrooms=1,
        square_footage=850,
        rent_amount=1200.00,
        description='Modern 2-bedroom apartment in downtown area with updated kitchen and hardwood floors.'
    )
    db.session.add(property1)
    
    property2 = Property(
        owner_id=admin.id,
        address='456 Oak Avenue\nSuburbia, CA 90211',
        property_type='house',
        bedrooms=3,
        bathrooms=2,
        square_footage=1450,
        rent_amount=1800.00,
        description='Single-family home with private yard, garage, and updated appliances.'
    )
    db.session.add(property2)
    
    property3 = Property(
        owner_id=admin.id,
        address='789 Pine Street, Unit 5B\nUptown, CA 90212',
        property_type='apartment',
        bedrooms=1,
        bathrooms=1,
        square_footage=600,
        rent_amount=900.00,
        description='Cozy 1-bedroom apartment with city views and in-unit laundry.'
    )
    db.session.add(property3)
    
    # Commit properties to get IDs
    db.session.commit()
    
    # Create sample leases
    lease1 = Lease(
        tenant_id=tenant1.id,
        property_id=property1.id,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        monthly_rent=1200.00,
        security_deposit=1200.00,
        status='active'
    )
    db.session.add(lease1)
    
    lease2 = Lease(
        tenant_id=tenant2.id,
        property_id=property2.id,
        start_date=date(2024, 3, 1),
        end_date=date(2025, 2, 28),
        monthly_rent=1800.00,
        security_deposit=1800.00,
        status='active'
    )
    db.session.add(lease2)
    
    # Commit leases to get IDs
    db.session.commit()
    
    # Create sample messages
    message1 = Message(
        sender_id=tenant1.id,
        recipient_id=admin.id,
        property_id=property1.id,
        message_text='Hi! I wanted to report that the kitchen faucet is dripping. Could someone take a look at it?',
        sent_at=datetime(2024, 6, 15, 10, 30)
    )
    db.session.add(message1)
    
    message2 = Message(
        sender_id=admin.id,
        recipient_id=tenant1.id,
        property_id=property1.id,
        message_text='Thank you for reporting the issue. I\'ll send a maintenance technician over this week to fix the faucet.',
        sent_at=datetime(2024, 6, 15, 14, 45),
        is_read=True
    )
    db.session.add(message2)
    
    message3 = Message(
        sender_id=tenant2.id,
        recipient_id=admin.id,
        property_id=property2.id,
        message_text='The rent payment for this month has been submitted. Please confirm receipt.',
        sent_at=datetime(2024, 6, 1, 9, 0)
    )
    db.session.add(message3)
    
    # Create sample maintenance requests
    maintenance1 = MaintenanceRequest(
        tenant_id=tenant1.id,
        property_id=property1.id,
        title='Kitchen Faucet Dripping',
        description='The kitchen faucet has been dripping constantly for the past few days. The drip is quite loud and wasting water.',
        priority='medium',
        status='pending'
    )
    db.session.add(maintenance1)
    
    maintenance2 = MaintenanceRequest(
        tenant_id=tenant2.id,
        property_id=property2.id,
        title='Garage Door Remote Not Working',
        description='The garage door remote stopped working yesterday. I checked the batteries and they seem fine.',
        priority='low',
        status='in_progress'
    )
    db.session.add(maintenance2)
    
    maintenance3 = MaintenanceRequest(
        tenant_id=tenant1.id,
        property_id=property1.id,
        title='Air Conditioning Not Cooling',
        description='The AC unit is running but not cooling the apartment properly. It\'s getting quite warm inside.',
        priority='high',
        status='pending'
    )
    db.session.add(maintenance3)
    
    # Commit all sample data
    db.session.commit()
    
    print("✓ Sample data created successfully!")
    print(f"✓ Admin user: username='admin', password='password'")
    print(f"✓ Tenant users: username='tenant1'/'tenant2', password='password'")
    print(f"✓ Created {Property.query.count()} properties")
    print(f"✓ Created {Lease.query.count()} leases")
    print(f"✓ Created {Message.query.count()} messages")
    print(f"✓ Created {MaintenanceRequest.query.count()} maintenance requests")

def init_database():
    """Initialize the database"""
    app = create_app('development')
    
    with app.app_context():
        print("Initializing Retreat Housing Property Management Database...")
        
        # Drop all tables if they exist
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        
        print("\n🎉 Database initialization complete!")
        print("\nYou can now run the application with:")
        print("python app.py")
        print("\nLogin credentials:")
        print("Admin: admin / password")
        print("Tenant: tenant1 / password")

if __name__ == '__main__':
    init_database()