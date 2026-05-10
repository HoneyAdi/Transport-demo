#!/usr/bin/env python3
"""
Setup Demo Data for Transport Management System
Creates all necessary test data for the demo checklist
"""

import os
import sys
from datetime import datetime, date, timedelta
import random
from sqlalchemy import text

sys.path.append('.')
from models import *
from webapp import app

def create_demo_data():
    """Create all necessary demo data"""
    
    with app.app_context():
        print("Starting demo data setup...")
        
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
        
        # 1. Create Tenants
        print("\nCreating Tenants...")
        tenants_data = [
            {
                'name': 'Demo Transport Company',
                'slug': 'demo-transport-company',
                'contact_email': 'admin@demo.com',
                'primary_phone': '+91-9876543210',
                'pan_number': 'AAAPL1234C',
                'gstin': '27AAAPL1234C1ZV',
                'business_type': 'Private Limited',
                'subscription_plan': 'Pro',
                'is_active': True
            },
            {
                'name': 'Test Logistics Ltd',
                'slug': 'test-logistics-ltd',
                'contact_email': 'admin@test.com',
                'primary_phone': '+91-9876543211',
                'pan_number': 'AAAXYZ5678',
                'gstin': '07AAAXYZ5678B1Z',
                'business_type': 'Private Limited',
                'subscription_plan': 'Standard',
                'is_active': True
            }
        ]
        
        created_tenants = []
        for tenant_data in tenants_data:
            existing = Tenant.query.filter_by(slug=tenant_data['slug']).first()
            if not existing:
                tenant = Tenant(**tenant_data)
                db.session.add(tenant)
                db.session.commit()
                created_tenants.append(tenant)
                print(f"  Created tenant: {tenant.name}")
            else:
                created_tenants.append(existing)
                print(f"  Tenant exists: {existing.name}")
        
        # 2. Create Users
        print("\nCreating Users...")
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@transport.com',
                'password': 'admin123',
                'full_name': 'Super Admin',
                'role': 'superadmin',
                'is_active': True,
                'tenant_id': None  # Superadmin has no tenant
            },
            {
                'username': 'tenant1',
                'email': 'tenant1@company.com',
                'password': 'tenant123',
                'full_name': 'Tenant Admin',
                'role': 'tenant_admin',
                'is_active': True,
                'tenant_id': created_tenants[0].id
            },
            {
                'username': 'ops',
                'email': 'ops@company.com',
                'password': 'ops123',
                'full_name': 'Operations User',
                'role': 'tenant_user',
                'is_active': True,
                'tenant_id': created_tenants[0].id
            },
            {
                'username': 'customer',
                'email': 'customer@company.com',
                'password': 'customer123',
                'full_name': 'Customer User',
                'role': 'tenant_user',
                'is_active': True,
                'tenant_id': created_tenants[0].id
            }
        ]
        
        for user_data in users_data:
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
        vendors_data = [
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
                'tenant_id': created_tenants[0].id
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
                'tenant_id': created_tenants[0].id
            }
        ]
        
        created_vendors = []
        for vendor_data in vendors_data:
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
        vehicles_data = [
            {
                'vehicle_number': 'MH01AB1234',
                'vehicle_type': 'Truck',
                'capacity': '10 tons',
                'make': 'Tata',
                'model': 'LPT 1613',
                'year': '2022',
                'insurance_expiry': date.today() + timedelta(days=365),
                'fitness_expiry': date.today() + timedelta(days=180),
                'status': 'available',
                'tenant_id': created_tenants[0].id
            },
            {
                'vehicle_number': 'MH02CD5678',
                'vehicle_type': 'Trailer',
                'capacity': '20 tons',
                'make': 'Ashok Leyland',
                'model': '3718',
                'year': '2023',
                'insurance_expiry': date.today() + timedelta(days=400),
                'fitness_expiry': date.today() + timedelta(days=200),
                'status': 'available',
                'tenant_id': created_tenants[0].id
            }
        ]
        
        created_vehicles = []
        for vehicle_data in vehicles_data:
            existing = Vehicle.query.filter_by(vehicle_number=vehicle_data['vehicle_number']).first()
            if not existing:
                vehicle = Vehicle(**vehicle_data)
                db.session.add(vehicle)
                db.session.commit()
                created_vehicles.append(vehicle)
                print(f"  Created vehicle: {vehicle.vehicle_number}")
            else:
                created_vehicles.append(existing)
                print(f"  Vehicle exists: {existing.vehicle_number}")
        
        # 5. Create Drivers
        print("\nCreating Drivers...")
        drivers_data = [
            {
                'name': 'Ramesh Kumar',
                'license_number': 'DL-1234567890123',
                'phone': '+91-9876543214',
                'address': '111 Driver Street, Pune, Maharashtra 411001',
                'license_expiry': date.today() + timedelta(days=730),
                'status': 'available',
                'tenant_id': created_tenants[0].id
            },
            {
                'name': 'Suresh Sharma',
                'license_number': 'DL-9876543210987',
                'phone': '+91-9876543215',
                'address': '222 Driver Road, Nagpur, Maharashtra 440001',
                'license_expiry': date.today() + timedelta(days(800)),
                'status': 'available',
                'tenant_id': created_tenants[0].id
            }
        ]
        
        created_drivers = []
        for driver_data in drivers_data:
            existing = Driver.query.filter_by(license_number=driver_data['license_number']).first()
            if not existing:
                driver = Driver(**driver_data)
                db.session.add(driver)
                db.session.commit()
                created_drivers.append(driver)
                print(f"  Created driver: {driver.name}")
            else:
                created_drivers.append(existing)
                print(f"  Driver exists: {existing.name}")
        
        # 6. Create Goods Receipts
        print("\nCreating Goods Receipts...")
        gr_data = [
            {
                'gr_number': 'GR-2024-001',
                'vendor_id': created_vendors[0].id,
                'date': date.today() - timedelta(days=5),
                'vehicle_number': created_vehicles[0].vehicle_number,
                'driver_name': created_drivers[0].name,
                'from_location': 'Mumbai',
                'to_location': 'Delhi',
                'description': 'Electronics Goods',
                'quantity': 100,
                'weight': '500 kg',
                'status': 'confirmed',
                'tenant_id': created_tenants[0].id
            },
            {
                'gr_number': 'GR-2024-002',
                'vendor_id': created_vendors[1].id,
                'date': date.today() - timedelta(days=3),
                'vehicle_number': created_vehicles[1].vehicle_number,
                'driver_name': created_drivers[1].name,
                'from_location': 'Bangalore',
                'to_location': 'Chennai',
                'description': 'Textile Materials',
                'quantity': 50,
                'weight': '300 kg',
                'status': 'confirmed',
                'tenant_id': created_tenants[0].id
            }
        ]
        
        created_grs = []
        for gr_info in gr_data:
            existing = GoodsReceipt.query.filter_by(gr_number=gr_info['gr_number']).first()
            if not existing:
                gr = GoodsReceipt(**gr_info)
                db.session.add(gr)
                db.session.commit()
                created_grs.append(gr)
                print(f"  Created GR: {gr.gr_number}")
            else:
                created_grs.append(existing)
                print(f"  GR exists: {existing.gr_number}")
        
        # 7. Create Transport Bills
        print("\nCreating Transport Bills...")
        bill_data = [
            {
                'bill_number': 'TB-2024-001',
                'gr_id': created_grs[0].id,
                'vendor_id': created_vendors[0].id,
                'date': date.today() - timedelta(days=4),
                'from_location': 'Mumbai',
                'to_location': 'Delhi',
                'amount': 15000.00,
                'gst_amount': 2700.00,
                'total_amount': 17700.00,
                'status': 'confirmed',
                'tenant_id': created_tenants[0].id
            },
            {
                'bill_number': 'TB-2024-002',
                'gr_id': created_grs[1].id,
                'vendor_id': created_vendors[1].id,
                'date': date.today() - timedelta(days=2),
                'from_location': 'Bangalore',
                'to_location': 'Chennai',
                'amount': 12000.00,
                'gst_amount': 2160.00,
                'total_amount': 14160.00,
                'status': 'sent',
                'tenant_id': created_tenants[0].id
            }
        ]
        
        for bill_info in bill_data:
            existing = TransportBill.query.filter_by(bill_number=bill_info['bill_number']).first()
            if not existing:
                bill = TransportBill(**bill_info)
                db.session.add(bill)
                db.session.commit()
                print(f"  Created Bill: {bill.bill_number}")
            else:
                print(f"  Bill exists: {existing.bill_number}")
        
        # 8. Create Customer Portal Accounts
        print("\nCreating Customer Portal Accounts...")
        customer_data = [
            {
                'email': 'customer@company.com',
                'password_hash': generate_password_hash('customer123'),
                'company_name': 'Demo Customer Pvt Ltd',
                'contact_person': 'John Doe',
                'phone': '+91-9876543216',
                'address': '999 Customer Street, Hyderabad, Telangana 500001',
                'gst_number': '36AAACUS1234D1ZV',
                'credit_limit': 100000.00,
                'is_active': True,
                'tenant_id': created_tenants[0].id
            }
        ]
        
        for cust_info in customer_data:
            existing = CustomerPortalAccount.query.filter_by(email=cust_info['email']).first()
            if not existing:
                customer = CustomerPortalAccount(**cust_info)
                db.session.add(customer)
                db.session.commit()
                print(f"  Created Customer: {customer.email}")
            else:
                print(f"  Customer exists: {existing.email}")
        
        # 9. Create Rate Lists
        print("\nCreating Rate Lists...")
        rate_data = [
            {
                'name': 'Standard Rates 2024',
                'from_location': 'Mumbai',
                'to_location': 'Delhi',
                'vehicle_type': 'Truck',
                'rate_per_ton': 150.00,
                'minimum_charge': 5000.00,
                'effective_from': date.today() - timedelta(days=30),
                'status': 'active',
                'tenant_id': created_tenants[0].id
            },
            {
                'name': 'Standard Rates 2024',
                'from_location': 'Bangalore',
                'to_location': 'Chennai',
                'vehicle_type': 'Trailer',
                'rate_per_ton': 120.00,
                'minimum_charge': 4000.00,
                'effective_from': date.today() - timedelta(days=30),
                'status': 'active',
                'tenant_id': created_tenants[0].id
            }
        ]
        
        for rate_info in rate_data:
            existing = RateList.query.filter_by(
                from_location=rate_info['from_location'],
                to_location=rate_info['to_location'],
                vehicle_type=rate_info['vehicle_type']
            ).first()
            if not existing:
                rate = RateList(**rate_info)
                db.session.add(rate)
                db.session.commit()
                print(f"  Created Rate List: {rate.from_location} to {rate.to_location}")
            else:
                print(f"  Rate List exists: {existing.from_location} to {existing.to_location}")
        
        print("\nDemo data setup completed successfully!")
        print("\nSummary:")
        print(f"  - Tenants: {len(created_tenants)}")
        print(f"  - Users: 4 (Superadmin, Tenant Admin, Operations, Customer)")
        print(f"  - Vendors: {len(created_vendors)}")
        print(f"  - Vehicles: {len(created_vehicles)}")
        print(f"  - Drivers: {len(created_drivers)}")
        print(f"  - Goods Receipts: {len(created_grs)}")
        print(f"  - Transport Bills: 2")
        print(f"  - Customer Portal Accounts: 1")
        print(f"  - Rate Lists: 2")
        
        print("\nTest Accounts:")
        print("  - Superadmin: admin@transport.com / admin123")
        print("  - Tenant Admin: tenant1@company.com / tenant123")
        print("  - Operations: ops@company.com / ops123")
        print("  - Customer: customer@company.com / customer123")
        
        return True

if __name__ == '__main__':
    success = create_demo_data()
    if success:
        print("\nDemo data is ready for testing!")
        sys.exit(0)
    else:
        print("\nFailed to setup demo data!")
        sys.exit(1)
