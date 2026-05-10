"""
Initialize sample data for Transport Management System
Run: python init_db.py
"""
from models import app, db
from models import (
    DeliveryType,
    Location,
    Tenant,
    User,
    Vehicle,
    ensure_tenant_permission_rows,
)

SUPERADMIN_USERNAME = 'superadmin'
SUPERADMIN_EMAIL = 'superadmin@transport.local'
SUPERADMIN_PASSWORD = 'SuperAdmin@123'

TENANT_NAME = 'Default Tenant'
TENANT_SLUG = 'default-tenant'
TENANT_EMAIL = 'tenant@transport.local'
TENANT_USERNAME = 'tenant'
TENANT_PASSWORD = 'Tenant@123'

with app.app_context():
    # Create tables
    db.create_all()

    default_tenant = Tenant.query.filter_by(slug=TENANT_SLUG).first()
    if not default_tenant:
        default_tenant = Tenant(
            name=TENANT_NAME,
            slug=TENANT_SLUG,
            contact_email=TENANT_EMAIL,
            is_active=True
        )
        db.session.add(default_tenant)
        db.session.flush()
    else:
        default_tenant.name = TENANT_NAME
        default_tenant.contact_email = TENANT_EMAIL
        default_tenant.is_active = True
    db.session.flush()

    superadmin = User.query.filter_by(username=SUPERADMIN_USERNAME).first()
    if not superadmin:
        superadmin = User(
            username=SUPERADMIN_USERNAME,
            email=SUPERADMIN_EMAIL,
            full_name='System Superadmin',
            role='superadmin',
            is_active=True
        )
        db.session.add(superadmin)
    else:
        superadmin.email = SUPERADMIN_EMAIL
        superadmin.full_name = 'System Superadmin'
        superadmin.role = 'superadmin'
        superadmin.is_active = True
    superadmin.tenant_id = None
    superadmin.set_password(SUPERADMIN_PASSWORD)

    tenant_user = User.query.filter_by(username=TENANT_USERNAME).first()
    if not tenant_user:
        tenant_user = User(
            username=TENANT_USERNAME,
            email=TENANT_EMAIL,
            full_name='Default Tenant Admin',
            role='tenant_admin',
            tenant_id=default_tenant.id,
            is_active=True
        )
        db.session.add(tenant_user)
    else:
        tenant_user.email = TENANT_EMAIL
        tenant_user.full_name = 'Default Tenant Admin'
        tenant_user.role = 'tenant_admin'
        tenant_user.tenant_id = default_tenant.id
        tenant_user.is_active = True
    tenant_user.set_password(TENANT_PASSWORD)
    
    # Sample Delivery Types
    delivery_types = ['Express', 'Standard', 'Overnight', 'Same Day']
    for dt in delivery_types:
        if not DeliveryType.query.filter_by(tenant_id=default_tenant.id, delivery_type=dt).first():
            db.session.add(DeliveryType(tenant_id=default_tenant.id, delivery_type=dt))
    
    # Sample Locations
    locations = [
        ('Mumbai-Delhi', 5000),
        ('Mumbai-Pune', 1500),
        ('Delhi-Jaipur', 2000),
        ('Bangalore-Chennai', 3000),
        ('Hyderabad-Bangalore', 3500),
    ]
    for loc, rate in locations:
        if not Location.query.filter_by(tenant_id=default_tenant.id, location=loc).first():
            db.session.add(Location(tenant_id=default_tenant.id, location=loc, rate=rate))
    
    # Sample Vehicles
    vehicles = [
        ('MH01AB1234', 'Truck', 'Tata 407'),
        ('MH02CD5678', 'Truck', 'Ashok Leyland'),
        ('DL03EF9012', 'Van', 'Mahindra Bolero'),
        ('KA04GH3456', 'Container', 'Eicher 1109'),
    ]
    for reg, vtype, model in vehicles:
        if not Vehicle.query.filter_by(tenant_id=default_tenant.id, registration_number=reg).first():
            db.session.add(
                Vehicle(
                    tenant_id=default_tenant.id,
                    registration_number=reg,
                    vehicle_type=vtype,
                    model=model,
                )
            )
    
    db.session.commit()
    ensure_tenant_permission_rows()
    print("Sample data initialized successfully!")
    print(f"   - Tenants: {Tenant.query.count()}")
    print(f"   - Users: {User.query.count()}")
    print(f"   - Tenant Permissions: {default_tenant.permissions.__len__()}")
    print(f"   - Delivery Types: {DeliveryType.query.count()}")
    print(f"   - Locations: {Location.query.count()}")
    print(f"   - Vehicles: {Vehicle.query.count()}")
    print("   - Superadmin login: superadmin / SuperAdmin@123")
    print("   - Tenant login: tenant / Tenant@123")
