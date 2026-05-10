#!/usr/bin/env python3
"""
Quick Demo Data Setup for Transport Management System
Creates essential test data for demo checklist
"""

import os
import sys
from datetime import datetime, date, timedelta
from sqlalchemy import text

sys.path.append('.')
from models import *
from webapp import app

def create_basic_demo_data():
    """Create basic demo data for testing"""
    
    with app.app_context():
        print("Starting quick demo data setup...")
        
        # Check database connection
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful")
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
        
        # Create tables if they don't exist
        try:
            db.create_all()
            print("Database tables created/verified")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
        
        # 1. Create Tenant
        print("\nCreating Tenant...")
        existing_tenant = Tenant.query.filter_by(slug='demo-transport-company').first()
        if not existing_tenant:
            tenant = Tenant(
                name='Demo Transport Company',
                slug='demo-transport-company',
                contact_email='admin@demo.com',
                primary_phone='+91-9876543210',
                pan_number='AAAPL1234C',
                gstin='27AAAPL1234C1ZV',
                business_type='Private Limited',
                subscription_plan='Pro',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            print(f"  Created tenant: {tenant.name}")
        else:
            tenant = existing_tenant
            print(f"  Tenant exists: {tenant.name}")
        
        # 2. Create Users
        print("\nCreating Users...")
        users = [
            {
                'username': 'admin',
                'email': 'admin@transport.com',
                'password': 'admin123',
                'full_name': 'Super Admin',
                'role': 'superadmin',
                'tenant_id': None
            },
            {
                'username': 'tenant1',
                'email': 'tenant1@company.com',
                'password': 'tenant123',
                'full_name': 'Tenant Admin',
                'role': 'tenant_admin',
                'tenant_id': tenant.id
            },
            {
                'username': 'ops',
                'email': 'ops@company.com',
                'password': 'ops123',
                'full_name': 'Operations User',
                'role': 'tenant_user',
                'tenant_id': tenant.id
            },
            {
                'username': 'customer',
                'email': 'customer@company.com',
                'password': 'customer123',
                'full_name': 'Customer User',
                'role': 'tenant_user',
                'tenant_id': tenant.id
            }
        ]
        
        for user_data in users:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                password = user_data.pop('password')
                user_data['password_hash'] = generate_password_hash(password)
                user = User(**user_data)
                db.session.add(user)
                db.session.commit()
                print(f"  Created user: {user.email}")
            else:
                print(f"  User exists: {existing.email}")
        
        # 3. Create Vendors
        print("\nCreating Vendors...")
        vendors = [
            {
                'vendor_name': 'ABC Suppliers Ltd',
                'vendor_code': 'VENDOR001',
                'email': 'info@abc.com',
                'phone_primary': '+91-9876543212',
                'reg_address_line1': '789 Vendor Street',
                'reg_city': 'Chennai',
                'reg_state': 'Tamil Nadu',
                'reg_pincode': '600001',
                'status': 'active',
                'vendor_type': 'supplier',
                'tenant_id': tenant.id
            },
            {
                'vendor_name': 'XYZ Transporters',
                'vendor_code': 'VENDOR002',
                'email': 'contact@xyz.com',
                'phone_primary': '+91-9876543213',
                'reg_address_line1': '321 Transport Road',
                'reg_city': 'Bangalore',
                'reg_state': 'Karnataka',
                'reg_pincode': '560001',
                'status': 'active',
                'vendor_type': 'transporter',
                'tenant_id': tenant.id
            }
        ]
        
        created_vendors = []
        for vendor_data in vendors:
            existing = Vendor.query.filter_by(vendor_code=vendor_data['vendor_code']).first()
            if not existing:
                vendor = Vendor(**vendor_data)
                db.session.add(vendor)
                db.session.commit()
                created_vendors.append(vendor)
                print(f"  Created vendor: {vendor.vendor_name}")
            else:
                created_vendors.append(existing)
                print(f"  Vendor exists: {existing.vendor_name}")
        
        # 4. Create Vehicles
        print("\nCreating Vehicles...")
        vehicles = [
            {
                'registration_number': 'MH01AB1234',
                'vehicle_type': 'Truck',
                'make': 'Tata',
                'model': 'LPT 1613',
                'year': 2022,
                'load_capacity_kg': 10000,
                'status': 'Active',
                'tenant_id': tenant.id
            },
            {
                'registration_number': 'MH02CD5678',
                'vehicle_type': 'Trailer',
                'make': 'Ashok Leyland',
                'model': '3718',
                'year': 2023,
                'load_capacity_kg': 20000,
                'status': 'Active',
                'tenant_id': tenant.id
            }
        ]
        
        created_vehicles = []
        for vehicle_data in vehicles:
            existing = Vehicle.query.filter_by(registration_number=vehicle_data['registration_number']).first()
            if not existing:
                vehicle = Vehicle(**vehicle_data)
                db.session.add(vehicle)
                db.session.commit()
                created_vehicles.append(vehicle)
                print(f"  Created vehicle: {vehicle.registration_number}")
            else:
                created_vehicles.append(existing)
                print(f"  Vehicle exists: {existing.registration_number}")
        
        # 5. Create Drivers
        print("\nCreating Drivers...")
        drivers = [
            {
                'driver_code': 'DRV001',
                'first_name': 'Ramesh',
                'last_name': 'Kumar',
                'mobile_number': '+91-9876543214',
                'address_line1': '111 Driver Street',
                'city': 'Pune',
                'state': 'Maharashtra',
                'pincode': '411001',
                'status': 'Active',
                'tenant_id': tenant.id
            },
            {
                'driver_code': 'DRV002',
                'first_name': 'Suresh',
                'last_name': 'Sharma',
                'mobile_number': '+91-9876543215',
                'address_line1': '222 Driver Road',
                'city': 'Nagpur',
                'state': 'Maharashtra',
                'pincode': '440001',
                'status': 'Active',
                'tenant_id': tenant.id
            }
        ]
        
        created_drivers = []
        for driver_data in drivers:
            existing = Driver.query.filter_by(driver_code=driver_data['driver_code']).first()
            if not existing:
                driver = Driver(**driver_data)
                db.session.add(driver)
                db.session.commit()
                created_drivers.append(driver)
                print(f"  Created driver: {driver.first_name} {driver.last_name}")
            else:
                created_drivers.append(existing)
                print(f"  Driver exists: {existing.first_name} {existing.last_name}")
        
        print("\nQuick demo data setup completed!")
        print("\nTest Accounts:")
        print("  - Superadmin: admin@transport.com / admin123")
        print("  - Tenant Admin: tenant1@company.com / tenant123")
        print("  - Operations: ops@company.com / ops123")
        print("  - Customer: customer@company.com / customer123")
        
        print("\nData Summary:")
        print(f"  - Tenants: 1")
        print(f"  - Users: 4")
        print(f"  - Vendors: {len(created_vendors)}")
        print(f"  - Vehicles: {len(created_vehicles)}")
        print(f"  - Drivers: {len(created_drivers)}")
        
        return True

if __name__ == '__main__':
    success = create_basic_demo_data()
    if success:
        print("\nDemo data is ready for testing!")
        sys.exit(0)
    else:
        print("\nFailed to setup demo data!")
        sys.exit(1)
