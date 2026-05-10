from datetime import datetime, date, timedelta
import json
import os
import re
import secrets
from urllib.parse import quote_plus

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
from sqlalchemy import UniqueConstraint, text
from werkzeug.security import check_password_hash, generate_password_hash


MODULE_DEFINITIONS = [
    ("dispatch", "Dispatch / Trips"),
    ("transport_bills", "Bilty Generation"),
    ("accounting", "Accounting Integration"),
    ("gps", "GPS Integration"),
    ("vendors", "Vendors"),
    ("vehicles", "Vehicles"),
    ("drivers", "Drivers"),
    ("expenses", "Expenses"),
    ("loans", "Loans"),
    ("ratelists", "Rate List"),
    ("locations", "Locations"),
    ("delivery_types", "Delivery Types"),
    ("reports", "Reports"),
]


def load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key, value)


def ensure_mysql_database(host, user, password, database_name):
    if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
        raise ValueError(f"Invalid MySQL database name: {database_name}")

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


load_env()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "transport-management-secret-key"
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=int(os.environ.get("SESSION_LIFETIME_MINUTES", "480"))
)
app.config["PREFERRED_URL_SCHEME"] = "https" if app.config["SESSION_COOKIE_SECURE"] else "http"

# Add custom Jinja2 filter for JSON parsing
import json as json_module
@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json_module.loads(s)
    except (ValueError, TypeError):
        return None

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///transport.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def run_auto_migration():
    """Auto-run migrations on application startup when models change"""
    with app.app_context():
        from flask_migrate import init, migrate as migrate_cmd, upgrade
        import os

        migrations_dir = "migrations"

        # Initialize migrations if not exists
        if not os.path.exists(migrations_dir):
            print("[Alembic] Initializing migration environment...")
            init(directory=migrations_dir)
            migrate_cmd(directory=migrations_dir, message="Initial migration")
            upgrade(directory=migrations_dir)
            print("[Alembic] Initial migration complete.")
        else:
            # Check if there are pending changes and create migration
            try:
                migrate_cmd(directory=migrations_dir, message="Auto migration")
                upgrade(directory=migrations_dir)
                print("[Alembic] Auto-migration applied successfully.")
            except Exception as e:
                # No changes detected or already up to date
                upgrade(directory=migrations_dir)
                print("[Alembic] Database is up to date.")


# Run auto-migration on startup (optional - can be disabled for production)
if os.environ.get("AUTO_MIGRATE", "false").lower() == "true":
    run_auto_migration()


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    contact_email = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Company Information
    cin_number = db.Column(db.String(25))  # Company Identification Number (optional)
    pan_number = db.Column(db.String(10), nullable=False)  # PAN (required)
    gstin = db.Column(db.String(15), nullable=False)  # GSTIN (required)
    business_type = db.Column(db.String(50), nullable=False)  # Sole Proprietorship, Partnership, LLP, Private Limited, Public Limited, One Person Company
    establishment_date = db.Column(db.Date)
    website_url = db.Column(db.String(200))

    # Contact Information
    primary_phone = db.Column(db.String(20), nullable=False)
    secondary_contact_person = db.Column(db.String(100))
    secondary_contact_phone = db.Column(db.String(20))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))

    # Financial Details
    credit_limit = db.Column(db.Numeric(12, 2), default=0)
    payment_terms = db.Column(db.String(200))
    bank_name = db.Column(db.String(100))
    bank_branch = db.Column(db.String(100))
    account_number = db.Column(db.String(30))
    account_type = db.Column(db.String(20), default='Current')
    ifsc_code = db.Column(db.String(11))
    micr_code = db.Column(db.String(9))
    upi_id = db.Column(db.String(50))

    # Document Uploads
    gst_certificate_path = db.Column(db.String(500))
    pan_card_path = db.Column(db.String(500))
    cin_certificate_path = db.Column(db.String(500))
    cancelled_cheque_path = db.Column(db.String(500))

    # Subscription Details
    subscription_plan = db.Column(db.String(50), nullable=False, default='Basic')  # Basic, Pro, Enterprise
    plan_expiry_date = db.Column(db.Date)
    max_users = db.Column(db.Integer, default=5)

    # Registered Address
    reg_address_line1 = db.Column(db.String(255))
    reg_address_line2 = db.Column(db.String(255))
    reg_city = db.Column(db.String(100))
    reg_state = db.Column(db.String(100))
    reg_pincode = db.Column(db.String(20))
    reg_country = db.Column(db.String(100), default='India')

    # Billing Address
    billing_address_line1 = db.Column(db.String(255))
    billing_address_line2 = db.Column(db.String(255))
    billing_city = db.Column(db.String(100))
    billing_state = db.Column(db.String(100))
    billing_pincode = db.Column(db.String(20))
    billing_country = db.Column(db.String(100), default='India')
    same_as_registered = db.Column(db.Boolean, default=False)


class TenantPermission(db.Model):
    __tablename__ = "tenant_permissions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "module_name", name="uq_tenant_module_permission"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )
    module_name = db.Column(db.String(50), nullable=False)
    can_view = db.Column(db.Boolean, default=True)
    can_create = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=True)
    can_delete = db.Column(db.Boolean, default=True)
    can_export = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tenant = db.relationship("Tenant", backref="permissions")


class TenantAddress(db.Model):
    __tablename__ = "tenant_addresses"
    __table_args__ = (
        UniqueConstraint("tenant_id", "address_type", name="uq_tenant_address_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)

    # Address Details
    address_type = db.Column(db.String(50), nullable=False)  # Registered, Billing, Office, Warehouse
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')

    # Contact at this address
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))

    # Status
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship("Tenant", backref="addresses")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="tenant_user")  # superadmin, tenant_admin, tenant_user, vendor
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant", backref="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserAmendmentRequest(db.Model):
    __tablename__ = "user_amendment_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    
    # Field changes stored as JSON
    field_changes = db.Column(db.Text, nullable=False)  # JSON: {"field_name": {"old": "value", "new": "value"}}
    
    # Classification
    change_type = db.Column(db.String(20), nullable=False, default="basic")  # basic or major
    
    # Reason for amendment
    reason = db.Column(db.Text, nullable=False)
    
    # Approval workflow
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending, approved, rejected, auto_approved
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="amendment_requests")
    requester = db.relationship("User", foreign_keys=[requested_by])
    approver = db.relationship("User", foreign_keys=[approved_by])
    tenant = db.relationship("Tenant")


class VendorUser(db.Model):
    """Link between Vendor and User for vendor login access"""
    __tablename__ = "vendor_users"
    __table_args__ = (
        UniqueConstraint("vendor_id", "user_id", name="uq_vendor_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    is_primary = db.Column(db.Boolean, default=False)  # Primary contact for the vendor
    can_view_own_data = db.Column(db.Boolean, default=True)
    can_edit_own_data = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    vendor = db.relationship("Vendor", backref="vendor_users")
    user = db.relationship("User", foreign_keys=[user_id], backref="vendor_associations")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User", foreign_keys=[created_by])


class VendorFieldPermission(db.Model):
    """Field-level permissions for vendor users - controls what fields they can see/edit"""
    __tablename__ = "vendor_field_permissions"
    __table_args__ = (
        UniqueConstraint("vendor_user_id", "field_name", name="uq_vendor_user_field"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vendor_user_id = db.Column(db.Integer, db.ForeignKey("vendor_users.id"), nullable=False, index=True)
    field_name = db.Column(db.String(100), nullable=False)  # e.g., "vendor_name", "contact_person", "phone_primary"
    field_category = db.Column(db.String(50), nullable=False)  # e.g., "basic", "contact", "address", "financial"
    can_view = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=False)
    is_required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor_user = db.relationship("VendorUser", backref="field_permissions")


class DeliveryType(db.Model):
    __tablename__ = "delivery_types"
    __table_args__ = (
        UniqueConstraint("tenant_id", "delivery_type", name="uq_delivery_type_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    delivery_type = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant")


class Location(db.Model):
    __tablename__ = "locations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "location", name="uq_location_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    location = db.Column(db.String(200), nullable=False)
    rate = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant")


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "registration_number",
            name="uq_vehicle_registration_tenant",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    registration_number = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(50))
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    color = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    engine_number = db.Column(db.String(100))
    chassis_number = db.Column(db.String(100))
    seating_capacity = db.Column(db.Integer)
    load_capacity_kg = db.Column(db.Integer)
    truck_size = db.Column(db.String(50))  # e.g., 10 Ft, 14 Ft, 17 Ft, 19 Ft, 20 Ft, 22 Ft, 24 Ft, 32 Ft
    owner_name = db.Column(db.String(200))
    owner_contact = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)

    # Insurance & Certificate Expiry Dates
    insurance_expiry = db.Column(db.Date)
    fitness_expiry = db.Column(db.Date)
    permit_1_year_expiry = db.Column(db.Date)
    permit_5_year_expiry = db.Column(db.Date)
    road_tax_expiry = db.Column(db.Date)
    puc_expiry = db.Column(db.Date)

    # Certificate Attachments
    insurance_attachment_path = db.Column(db.String(500))
    fitness_certificate_path = db.Column(db.String(500))
    permit_1_year_attachment_path = db.Column(db.String(500))
    permit_5_year_attachment_path = db.Column(db.String(500))
    road_tax_attachment_path = db.Column(db.String(500))
    puc_attachment_path = db.Column(db.String(500))

    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))

    tenant = db.relationship("Tenant")
    driver = db.relationship("Driver", backref="vehicles")


# Simplified TransportBill model to work within MySQL row size limit
# TODO: Move extended fields to a separate related table
class TransportBill(db.Model):
    __tablename__ = "transport_bills"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    name = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Versioning fields
    parent_id = db.Column(db.Integer, db.ForeignKey("transport_bills.id"), nullable=True, index=True)
    version_number = db.Column(db.Integer, default=1)
    is_original = db.Column(db.Boolean, default=True)
    modification_reason = db.Column(db.Text, nullable=True)

    # Essential fields used by the application
    gr_number = db.Column(db.String(50))
    gr_date = db.Column(db.Date)
    date = db.Column(db.Date, default=datetime.utcnow)
    challan_number = db.Column(db.String(50))
    party_information = db.Column(db.String(100))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    rate = db.Column(db.Integer, default=0)
    delivery_type_id = db.Column(db.Integer, db.ForeignKey("delivery_types.id"))
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    status = db.Column(db.String(30), default='booked')

    # Extended data stored as JSON to avoid row size limit
    extended_data = db.Column(db.Text)  # JSON field for additional attributes

    def __init__(self, **kwargs):
        # Define essential columns that exist as direct database columns
        essential_cols = {
            'id', 'tenant_id', 'name', 'created_at', 'updated_at',
            'parent_id', 'version_number', 'is_original', 'modification_reason',
            'gr_number', 'gr_date', 'date', 'challan_number', 'party_information',
            'location_id', 'rate', 'delivery_type_id', 'vehicle_id', 'status',
            'extended_data'
        }

        # Separate essential fields from extended fields
        essential_data = {}
        extended_fields = {}

        for key, value in kwargs.items():
            if key in essential_cols:
                essential_data[key] = value
            else:
                extended_fields[key] = value

        # Set essential fields
        super().__init__(**essential_data)

        # Store extended fields in JSON (convert dates to strings)
        if extended_fields:
            serializable_fields = {}
            for key, value in extended_fields.items():
                if isinstance(value, (datetime, date)):
                    serializable_fields[key] = value.isoformat()
                else:
                    serializable_fields[key] = value
            self.extended_data = json.dumps(serializable_fields)

    def get_extended_field(self, field_name, default=None):
        """Get a value from extended_data JSON"""
        if self.extended_data:
            data = json.loads(self.extended_data)
            return data.get(field_name, default)
        return default

    def set_extended_field(self, field_name, value):
        """Set a value in extended_data JSON"""
        data = {}
        if self.extended_data:
            data = json.loads(self.extended_data)
        # Convert dates to strings for JSON serialization
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        data[field_name] = value
        self.extended_data = json.dumps(data)

    tenant = db.relationship("Tenant")
    vehicle = db.relationship("Vehicle", backref="bills")
    location = db.relationship("Location", backref="bills")
    delivery_type = db.relationship("DeliveryType", backref="bills")
    parent = db.relationship("TransportBill", remote_side=[id], backref="versions")


class DispatchTrip(db.Model):
    __tablename__ = "dispatch_trips"
    __table_args__ = (
        UniqueConstraint("tenant_id", "trip_number", name="uq_dispatch_trip_number_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    trip_number = db.Column(db.String(50), nullable=False)
    trip_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(30), default="planned", index=True)

    bilty_id = db.Column(db.Integer, db.ForeignKey("transport_bills.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), index=True)

    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    planned_dispatch_at = db.Column(db.DateTime)
    actual_dispatch_at = db.Column(db.DateTime)
    expected_delivery_at = db.Column(db.DateTime)
    actual_delivery_at = db.Column(db.DateTime)

    current_location = db.Column(db.String(200))
    last_latitude = db.Column(db.Numeric(10, 7))
    last_longitude = db.Column(db.Numeric(10, 7))
    last_tracking_update_at = db.Column(db.DateTime)
    delay_reason = db.Column(db.Text)
    dispatch_notes = db.Column(db.Text)

    pod_number = db.Column(db.String(100))
    pod_attachment_path = db.Column(db.String(500))
    received_by_name = db.Column(db.String(200))
    delivered_by = db.Column(db.String(200))
    delivery_remarks = db.Column(db.Text)
    customer_tracking_token = db.Column(db.String(64), unique=True, index=True)
    driver_access_token = db.Column(db.String(64), unique=True, index=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship("Tenant")
    bilty = db.relationship("TransportBill", backref="dispatch_trips")
    vehicle = db.relationship("Vehicle", backref="dispatch_trips")
    driver = db.relationship("Driver", backref="dispatch_trips")
    creator = db.relationship("User", foreign_keys=[created_by])


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(100), nullable=False, index=True)
    entity_id = db.Column(db.Integer, index=True)
    summary = db.Column(db.String(500))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    tenant = db.relationship("Tenant")
    user = db.relationship("User")


class CustomerPortalAccount(db.Model):
    """Customer portal accounts for self-service access"""
    __tablename__ = "customer_portal_accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_customer_portal_email_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), index=True)
    email = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # Portal enhancement fields
    last_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    notification_preferences = db.Column(db.Text)  # JSON for notification settings
    language_preference = db.Column(db.String(10), default='en')
    timezone_preference = db.Column(db.String(50), default='UTC')
    portal_theme = db.Column(db.String(20), default='light')

    tenant = db.relationship("Tenant")
    vendor = db.relationship("Vendor")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class AccountingIntegration(db.Model):
    __tablename__ = "accounting_integrations"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    provider = db.Column(db.String(50), default="tally")
    export_format = db.Column(db.String(20), default="csv")
    api_base_url = db.Column(db.String(255))
    api_key = db.Column(db.String(255))
    ledger_sales = db.Column(db.String(150), default="Freight Sales")
    ledger_receivable = db.Column(db.String(150), default="Sundry Debtors")
    ledger_tax = db.Column(db.String(150), default="GST Output")
    ledger_cash_bank = db.Column(db.String(150), default="Bank")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship("Tenant")


class AccountingExport(db.Model):
    __tablename__ = "accounting_exports"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    integration_id = db.Column(db.Integer, db.ForeignKey("accounting_integrations.id"), index=True)
    export_type = db.Column(db.String(30), nullable=False)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="generated")
    records_count = db.Column(db.Integer, default=0)
    file_name = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant")
    integration = db.relationship("AccountingIntegration")
    creator = db.relationship("User")


class GPSDevice(db.Model):
    __tablename__ = "gps_devices"
    __table_args__ = (
        UniqueConstraint("tenant_id", "device_imei", name="uq_gps_device_imei_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), index=True)
    device_imei = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50), default="generic")
    api_key = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant")
    vehicle = db.relationship("Vehicle")


class GPSPing(db.Model):
    __tablename__ = "gps_pings"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    device_id = db.Column(db.Integer, db.ForeignKey("gps_devices.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), index=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("dispatch_trips.id"), index=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    speed_kmph = db.Column(db.Numeric(8, 2))
    heading = db.Column(db.Numeric(8, 2))
    address = db.Column(db.String(255))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    raw_payload = db.Column(db.Text)

    tenant = db.relationship("Tenant")
    device = db.relationship("GPSDevice")
    vehicle = db.relationship("Vehicle")
    trip = db.relationship("DispatchTrip", backref="gps_pings")


def generate_access_token():
    return secrets.token_urlsafe(32)


def generate_trip_number():
    last_trip = DispatchTrip.query.order_by(DispatchTrip.id.desc()).first()
    if last_trip and last_trip.trip_number:
        try:
            last_num = int(last_trip.trip_number.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"TRP-{new_num:05d}"


class Vendor(db.Model):
    __tablename__ = "vendors"
    __table_args__ = (
        UniqueConstraint("tenant_id", "vendor_code", name="uq_vendor_code_tenant"),
        # Removed GSTIN unique constraint - same GSTIN can have multiple addresses
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 1. Basic Information
    vendor_code = db.Column(db.String(20), nullable=False)
    vendor_name = db.Column(db.String(200), nullable=False)
    vendor_type = db.Column(db.String(50), default='supplier')
    status = db.Column(db.String(50), default='active')
    business_nature = db.Column(db.String(100))
    establishment_date = db.Column(db.Date)
    website = db.Column(db.String(200))
    referral_source = db.Column(db.String(100))

    # 2. Contact Information
    contact_person = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    phone_primary = db.Column(db.String(20))
    phone_secondary = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(150))
    alternate_email = db.Column(db.String(150))
    fax_number = db.Column(db.String(20))

    # 3. Registered Address
    reg_address_line1 = db.Column(db.String(200))
    reg_address_line2 = db.Column(db.String(200))
    reg_city = db.Column(db.String(100))
    reg_state = db.Column(db.String(100))
    reg_pincode = db.Column(db.String(10))
    reg_country = db.Column(db.String(100), default='India')

    # 4. Office/Communication Address
    office_address_line1 = db.Column(db.String(200))
    office_address_line2 = db.Column(db.String(200))
    office_city = db.Column(db.String(100))
    office_state = db.Column(db.String(100))
    office_pincode = db.Column(db.String(10))
    office_country = db.Column(db.String(100), default='India')
    same_as_registered = db.Column(db.Boolean, default=False)

    # 5. GST & Tax Details
    gstin = db.Column(db.String(20))
    gst_registration_date = db.Column(db.Date)
    gst_state_code = db.Column(db.String(2))
    pan_number = db.Column(db.String(10))
    tan_number = db.Column(db.String(10))
    tin_number = db.Column(db.String(20))
    cin_number = db.Column(db.String(25))
    msme_number = db.Column(db.String(25))
    tax_regime = db.Column(db.String(50), default='regular')
    is_composition_dealer = db.Column(db.Boolean, default=False)
    is_tds_applicable = db.Column(db.Boolean, default=False)
    tds_rate = db.Column(db.Numeric(5, 2), default=0)

    # 6. Bank Account Details
    bank_name = db.Column(db.String(100))
    bank_branch = db.Column(db.String(100))
    account_number = db.Column(db.String(30))
    account_type = db.Column(db.String(20), default='current')
    ifsc_code = db.Column(db.String(11))
    micr_code = db.Column(db.String(9))
    swift_code = db.Column(db.String(11))
    bank_address = db.Column(db.Text)
    upi_id = db.Column(db.String(50))

    # 7. Primary Contact Person
    primary_contact_name = db.Column(db.String(100))
    primary_contact_designation = db.Column(db.String(100))
    primary_contact_phone = db.Column(db.String(20))
    primary_contact_mobile = db.Column(db.String(20))
    primary_contact_email = db.Column(db.String(150))
    
    # 8. Customer Classification Fields
    customer_type = db.Column(db.String(50), default='regular')  # regular, premium, vip, one_time
    customer_tier = db.Column(db.String(20), default='bronze')   # bronze, silver, gold, platinum
    customer_segment = db.Column(db.String(100))  # manufacturing, logistics, retail, etc.
    customer_lifecycle_status = db.Column(db.String(20), default='active')  # active, inactive, blacklisted, dormant
    classification_notes = db.Column(db.Text)
    classification_date = db.Column(db.Date, default=date.today)
    classified_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    # 8. Secondary Contact Person
    secondary_contact_name = db.Column(db.String(100))
    secondary_contact_designation = db.Column(db.String(100))
    secondary_contact_phone = db.Column(db.String(20))
    secondary_contact_mobile = db.Column(db.String(20))
    secondary_contact_email = db.Column(db.String(150))

    # 9. Document Uploads
    pan_card_path = db.Column(db.String(500))
    gst_certificate_path = db.Column(db.String(500))
    bank_proof_path = db.Column(db.String(500))
    address_proof_path = db.Column(db.String(500))
    msme_certificate_path = db.Column(db.String(500))
    incorporation_certificate_path = db.Column(db.String(500))
    cancelled_cheque_path = db.Column(db.String(500))

    # 10. Compliance & Verification
    kyc_status = db.Column(db.String(50), default='pending')
    verification_date = db.Column(db.Date)
    verified_by = db.Column(db.String(100))
    compliance_rating = db.Column(db.String(20), default='unrated')
    background_check_done = db.Column(db.Boolean, default=False)
    background_check_date = db.Column(db.Date)

    # 11. Trade References
    trade_reference_1_name = db.Column(db.String(200))
    trade_reference_1_contact = db.Column(db.String(20))
    trade_reference_1_address = db.Column(db.Text)
    trade_reference_2_name = db.Column(db.String(200))
    trade_reference_2_contact = db.Column(db.String(20))
    trade_reference_2_address = db.Column(db.Text)

    # 12. Financial Information
    credit_limit = db.Column(db.Numeric(12, 2), default=0)
    credit_period_days = db.Column(db.Integer, default=0)
    opening_balance = db.Column(db.Numeric(12, 2), default=0)
    balance_type = db.Column(db.String(10), default='dr')
    currency = db.Column(db.String(3), default='INR')
    payment_terms = db.Column(db.String(200))

    # 13. Supply Details
    supply_type = db.Column(db.String(50))
    product_categories = db.Column(db.Text)
    lead_time_days = db.Column(db.Integer, default=0)
    min_order_value = db.Column(db.Numeric(12, 2), default=0)
    max_order_value = db.Column(db.Numeric(12, 2), default=0)
    delivery_mode = db.Column(db.String(50))

    # 14. System Fields
    created_by = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    approved_on = db.Column(db.DateTime)
    remarks = db.Column(db.Text)

    tenant = db.relationship("Tenant", backref="vendors")
    addresses = db.relationship("VendorAddress", backref="vendor", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def primary_address(self):
        """Get the primary address for this vendor"""
        return self.addresses.filter_by(is_primary=True, is_active=True).first() or self.addresses.filter_by(is_active=True).first()


class VendorAddress(db.Model):
    __tablename__ = "vendor_addresses"
    __table_args__ = (
        UniqueConstraint("vendor_id", "address_type", name="uq_vendor_address_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    vendor_address_id = db.Column(db.Integer, db.ForeignKey("vendor_addresses.id"), index=True)  # Selected vendor address
    
    # Address Details
    address_type = db.Column(db.String(50), nullable=False)  # Registered, Billing, Shipping, Warehouse, etc.
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')
    
    # Contact at this address
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    
    # Status
    is_primary = db.Column(db.Boolean, default=False)  # Default address for this vendor
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship("Tenant")


def generate_vendor_code():
    last_vendor = Vendor.query.order_by(Vendor.id.desc()).first()
    if last_vendor and last_vendor.vendor_code:
        try:
            last_num = int(last_vendor.vendor_code.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"VDR-{new_num:05d}"


def generate_bill_name():
    last_bill = TransportBill.query.order_by(TransportBill.id.desc()).first()
    if last_bill and last_bill.name:
        try:
            last_num = int(last_bill.name.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"TBG-{new_num:05d}"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    name = db.Column(db.String(20), unique=True)
    expense_date = db.Column(db.Date, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    amount = db.Column(db.Numeric(10, 2), default=0)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    payment_method = db.Column(db.String(50), default="Cash")
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), index=True)
    vendor_address_id = db.Column(db.Integer, db.ForeignKey("vendor_addresses.id"), index=True)
    vendor_name = db.Column(db.String(200))  # Kept for backward compatibility
    vendor_contact = db.Column(db.String(100))  # Kept for backward compatibility
    bill_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    receipt_path = db.Column(db.String(500))
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant")
    vehicle = db.relationship("Vehicle", backref="expenses")
    location = db.relationship("Location", backref="expenses")


def generate_expense_name():
    last_expense = Expense.query.order_by(Expense.id.desc()).first()
    if last_expense and last_expense.name:
        try:
            last_num = int(last_expense.name.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"EXP-{new_num:05d}"


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    name = db.Column(db.String(20), unique=True)
    loan_type = db.Column(db.String(50), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    principal_amount = db.Column(db.Numeric(12, 2), default=0)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)
    tenure_months = db.Column(db.Integer, default=0)
    emi_amount = db.Column(db.Numeric(10, 2), default=0)
    total_payable = db.Column(db.Numeric(12, 2), default=0)
    total_interest = db.Column(db.Numeric(12, 2), default=0)
    lender_name = db.Column(db.String(200))
    lender_type = db.Column(db.String(50))
    lender_contact = db.Column(db.String(50))
    lender_address = db.Column(db.String(500))
    agent_name = db.Column(db.String(200))
    agent_contact = db.Column(db.String(50))
    loan_date = db.Column(db.Date, default=datetime.utcnow)
    disbursement_date = db.Column(db.Date)
    first_emi_date = db.Column(db.Date)
    last_emi_date = db.Column(db.Date)
    down_payment = db.Column(db.Numeric(10, 2), default=0)
    amount_paid = db.Column(db.Numeric(12, 2), default=0)
    balance_amount = db.Column(db.Numeric(12, 2), default=0)
    emis_paid = db.Column(db.Integer, default=0)
    emis_remaining = db.Column(db.Integer, default=0)
    next_emi_due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Active")
    loan_account_number = db.Column(db.String(100))
    document_path = db.Column(db.String(500))
    purpose = db.Column(db.Text)
    collateral = db.Column(db.String(500))
    insurance_details = db.Column(db.String(500))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tenant = db.relationship("Tenant")
    vehicle = db.relationship("Vehicle", backref="loans")


class Driver(db.Model):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "driver_code", name="uq_driver_code_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    driver_code = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    father_name = db.Column(db.String(200))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    nationality = db.Column(db.String(50), default="Indian")
    marital_status = db.Column(db.String(20))

    # Contact Information
    mobile_number = db.Column(db.String(20))
    alternate_mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_number = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(50))

    # Address Information
    address_line1 = db.Column(db.String(300))
    address_line2 = db.Column(db.String(300))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    country = db.Column(db.String(50), default="India")

    # Employment Details
    employee_code = db.Column(db.String(50))
    date_of_joining = db.Column(db.Date)
    designation = db.Column(db.String(100), default="Driver")
    department = db.Column(db.String(100))
    employment_type = db.Column(db.String(50), default="Full-time")
    status = db.Column(db.String(50), default="Active")
    monthly_salary = db.Column(db.Numeric(10, 2))
    daily_wage = db.Column(db.Numeric(8, 2))

    # Experience & Qualifications
    total_experience_years = db.Column(db.Integer)
    license_type = db.Column(db.String(50))
    license_number = db.Column(db.String(50))
    license_issue_date = db.Column(db.Date)
    license_expiry_date = db.Column(db.Date)
    license_issuing_authority = db.Column(db.String(200))
    license_state = db.Column(db.String(100))

    # Bank Details
    bank_name = db.Column(db.String(200))
    bank_branch = db.Column(db.String(200))
    account_holder_name = db.Column(db.String(200))
    account_number = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(20))
    account_type = db.Column(db.String(50), default="Savings")
    upi_id = db.Column(db.String(100))

    # Documents & Attachments
    photo_path = db.Column(db.String(500))
    aadhaar_number = db.Column(db.String(20))
    aadhaar_attachment_path = db.Column(db.String(500))
    pan_number = db.Column(db.String(20))
    pan_attachment_path = db.Column(db.String(500))
    driving_license_attachment_path = db.Column(db.String(500))
    bank_attachment_path = db.Column(db.String(500))
    police_verification_path = db.Column(db.String(500))
    medical_certificate_path = db.Column(db.String(500))

    # References
    reference1_name = db.Column(db.String(200))
    reference1_contact = db.Column(db.String(20))
    reference1_address = db.Column(db.String(500))
    reference2_name = db.Column(db.String(200))
    reference2_contact = db.Column(db.String(20))
    reference2_address = db.Column(db.String(500))

    # Remarks
    remarks = db.Column(db.Text)

    tenant = db.relationship("Tenant")


class RateList(db.Model):
    __tablename__ = "ratelists"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_ratelist_name_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    party_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), index=True)  # Vendor/Party
    name = db.Column(db.String(200), nullable=False)  # Rate list name (e.g., "Mumbai-Delhi Truck Rates")
    description = db.Column(db.Text)
    origin = db.Column(db.String(100))  # Origin location
    destination = db.Column(db.String(100))  # Destination location
    vehicle_type = db.Column(db.String(50))  # Truck, Tempo, Trailer, etc.
    
    # Vehicle-specific rates
    rate_14ft = db.Column(db.Numeric(10, 2))
    rate_17ft = db.Column(db.Numeric(10, 2))
    rate_t5_1109 = db.Column(db.Numeric(10, 2))
    rate_19ft = db.Column(db.Numeric(10, 2))
    rate_22ft = db.Column(db.Numeric(10, 2))
    rate_32ft = db.Column(db.Numeric(10, 2))
    
    # Freight Charges
    basic_freight = db.Column(db.Numeric(10, 2))
    loading_charge = db.Column(db.Numeric(10, 2))
    unloading_charge = db.Column(db.Numeric(10, 2))
    door_pickup_charge = db.Column(db.Numeric(10, 2))
    door_delivery_charge = db.Column(db.Numeric(10, 2))
    hamali_charge = db.Column(db.Numeric(10, 2))
    detention_charge = db.Column(db.Numeric(10, 2))
    waiting_charge = db.Column(db.Numeric(10, 2))
    halting_charge = db.Column(db.Numeric(10, 2))
    toll_charge = db.Column(db.Numeric(10, 2))
    border_charge = db.Column(db.Numeric(10, 2))
    fuel_surcharge = db.Column(db.Numeric(10, 2))
    packing_charge = db.Column(db.Numeric(10, 2))
    weighment_charge = db.Column(db.Numeric(10, 2))
    permit_charge = db.Column(db.Numeric(10, 2))
    driver_allowance = db.Column(db.Numeric(10, 2))
    insurance_charge = db.Column(db.Numeric(10, 2))
    other_charges = db.Column(db.Numeric(10, 2))
    
    # GST
    igst_rate = db.Column(db.Numeric(5, 2))
    cgst_rate = db.Column(db.Numeric(5, 2))
    sgst_rate = db.Column(db.Numeric(5, 2))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    effective_from = db.Column(db.Date)
    effective_to = db.Column(db.Date)
    effective_date = db.Column(db.Date, default=date.today)  # Date when rate was last updated
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship("Tenant")
    party = db.relationship("Vendor", backref="ratelists")


class PaymentReceipt(db.Model):
    __tablename__ = "payment_receipts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "receipt_number", name="uq_payment_receipt_number_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    bilty_id = db.Column(db.Integer, db.ForeignKey("transport_bills.id"), index=True, nullable=False)
    receipt_number = db.Column(db.String(50), nullable=False)  # Auto-generated receipt number
    receipt_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Payment details
    amount_received = db.Column(db.Numeric(12, 2), nullable=False)  # Amount actually received
    tds_amount = db.Column(db.Numeric(12, 2), default=0)  # TDS deducted (editable)
    optional_amount = db.Column(db.Numeric(12, 2), default=0)  # Optional amount for pending payments
    optional_amount_reason = db.Column(db.Text)  # Reason for optional amount
    
    # Balance tracking
    balance_before = db.Column(db.Numeric(12, 2), nullable=False)  # Balance before this payment
    balance_after = db.Column(db.Numeric(12, 2), nullable=False)  # Balance after this payment
    
    # Status
    is_complete = db.Column(db.Boolean, default=False)  # Marked as complete when balance is zero
    remarks = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    # Relationships
    bilty = db.relationship("TransportBill", backref="payment_receipts")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User", foreign_keys=[created_by])


def generate_driver_code():
    last_driver = Driver.query.order_by(Driver.id.desc()).first()
    if last_driver and last_driver.driver_code:
        try:
            last_num = int(last_driver.driver_code.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"DRV-{new_num:05d}"


def generate_loan_name():
    last_loan = Loan.query.order_by(Loan.id.desc()).first()
    if last_loan and last_loan.name:
        try:
            last_num = int(last_loan.name.split("-")[1])
            new_num = last_num + 1
        except Exception:
            new_num = 1
    else:
        new_num = 1
    return f"LON-{new_num:05d}"


def _column_exists(connection, table_name, column_name):
    result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return bool(result.scalar())


def _index_exists(connection, table_name, index_name):
    result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND index_name = :index_name
            """
        ),
        {"table_name": table_name, "index_name": index_name},
    )
    return bool(result.scalar())


def _add_column_if_missing(connection, table_name, column_name, ddl):
    if not _column_exists(connection, table_name, column_name):
        connection.execute(text(f"ALTER TABLE `{table_name}` ADD COLUMN {ddl}"))


def _drop_index_if_exists(connection, table_name, index_name):
    if index_name != "PRIMARY" and _index_exists(connection, table_name, index_name):
        connection.execute(text(f"ALTER TABLE `{table_name}` DROP INDEX `{index_name}`"))


def _create_index_if_missing(connection, table_name, index_name, sql):
    if not _index_exists(connection, table_name, index_name):
        connection.execute(text(sql))


def ensure_default_tenant():
    default_tenant = Tenant.query.filter_by(slug="default-tenant").first()
    if not default_tenant:
        default_tenant = Tenant(
            name="Default Tenant",
            slug="default-tenant",
            contact_email="tenant@transport.local",
            is_active=True,
        )
        db.session.add(default_tenant)
        db.session.commit()
    elif not default_tenant.is_active:
        default_tenant.is_active = True
        db.session.commit()
    return default_tenant


def ensure_tenant_permission_rows():
    changed = False
    for tenant in Tenant.query.all():
        existing = {
            permission.module_name: permission
            for permission in TenantPermission.query.filter_by(tenant_id=tenant.id).all()
        }
        for module_name, _label in MODULE_DEFINITIONS:
            if module_name not in existing:
                db.session.add(
                    TenantPermission(
                        tenant_id=tenant.id,
                        module_name=module_name,
                        can_view=True,
                        can_create=True,
                        can_edit=True,
                        can_delete=True,
                        can_export=True,
                    )
                )
                changed = True
    if changed:
        db.session.commit()


def initialize_database():
    with app.app_context():
        db.create_all()

        with db.engine.begin() as connection:
            tenant_tables = [
                "delivery_types",
                "locations",
                "vehicles",
                "drivers",
                "dispatch_trips",
                "transport_bills",
                "vendors",
                "expenses",
                "loans",
            ]

            for table_name in tenant_tables:
                _add_column_if_missing(
                    connection,
                    table_name,
                    "tenant_id",
                    "tenant_id INT NULL",
                )
                _create_index_if_missing(
                    connection,
                    table_name,
                    f"ix_{table_name}_tenant_id",
                    f"CREATE INDEX `ix_{table_name}_tenant_id` ON `{table_name}` (`tenant_id`)",
                )

            _drop_index_if_exists(connection, "delivery_types", "delivery_type")
            _drop_index_if_exists(connection, "locations", "location")
            _drop_index_if_exists(connection, "vehicles", "registration_number")

            _create_index_if_missing(
                connection,
                "delivery_types",
                "uq_delivery_type_tenant",
                "CREATE UNIQUE INDEX `uq_delivery_type_tenant` "
                "ON `delivery_types` (`tenant_id`, `delivery_type`)",
            )
            _create_index_if_missing(
                connection,
                "locations",
                "uq_location_tenant",
                "CREATE UNIQUE INDEX `uq_location_tenant` "
                "ON `locations` (`tenant_id`, `location`)",
            )
            _create_index_if_missing(
                connection,
                "vehicles",
                "uq_vehicle_registration_tenant",
                "CREATE UNIQUE INDEX `uq_vehicle_registration_tenant` "
                "ON `vehicles` (`tenant_id`, `registration_number`)",
            )
            _add_column_if_missing(
                connection,
                "dispatch_trips",
                "customer_tracking_token",
                "customer_tracking_token VARCHAR(64) NULL",
            )
            _add_column_if_missing(
                connection,
                "dispatch_trips",
                "driver_access_token",
                "driver_access_token VARCHAR(64) NULL",
            )
            _create_index_if_missing(
                connection,
                "dispatch_trips",
                "ix_dispatch_trips_customer_tracking_token",
                "CREATE INDEX `ix_dispatch_trips_customer_tracking_token` "
                "ON `dispatch_trips` (`customer_tracking_token`)",
            )
            _create_index_if_missing(
                connection,
                "dispatch_trips",
                "ix_dispatch_trips_driver_access_token",
                "CREATE INDEX `ix_dispatch_trips_driver_access_token` "
                "ON `dispatch_trips` (`driver_access_token`)",
            )
            _add_column_if_missing(
                connection,
                "dispatch_trips",
                "last_latitude",
                "last_latitude DECIMAL(10,7) NULL",
            )
            _add_column_if_missing(
                connection,
                "dispatch_trips",
                "last_longitude",
                "last_longitude DECIMAL(10,7) NULL",
            )

        default_tenant = ensure_default_tenant()

        with db.engine.begin() as connection:
            for table_name in [
                "delivery_types",
                "locations",
                "vehicles",
                "drivers",
                "dispatch_trips",
                "transport_bills",
                "expenses",
                "loans",
            ]:
                connection.execute(
                    text(
                        f"UPDATE `{table_name}` "
                        "SET tenant_id = :tenant_id "
                        "WHERE tenant_id IS NULL"
                    ),
                    {"tenant_id": default_tenant.id},
                )

            connection.execute(
                text(
                    "UPDATE users "
                    "SET role = 'tenant_user' "
                    "WHERE role NOT IN ('superadmin', 'tenant_admin', 'tenant_user')"
                )
            )
            connection.execute(
                text(
                    "UPDATE users "
                    "SET role = 'tenant_admin' "
                    "WHERE username = 'tenant' AND role <> 'superadmin'"
                )
            )
            connection.execute(
                text(
                    "UPDATE users "
                    "SET tenant_id = :tenant_id "
                    "WHERE role <> 'superadmin' AND tenant_id IS NULL"
                ),
                {"tenant_id": default_tenant.id},
            )

        ensure_tenant_permission_rows()


# initialize_database()  # Commented out for SQLite compatibility
class SubscriptionPlan(db.Model):
    __tablename__ = "subscription_plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    monthly_price = db.Column(db.Numeric(10, 2), nullable=False)
    annual_price = db.Column(db.Numeric(10, 2), nullable=False)
    max_vehicles = db.Column(db.Integer, nullable=False)
    max_drivers = db.Column(db.Integer, nullable=False)
    max_users = db.Column(db.Integer, nullable=False)
    max_storage_gb = db.Column(db.Integer, nullable=False)
    features = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TenantSubscription(db.Model):
    __tablename__ = "tenant_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plans.id"))
    
    custom_monthly_price = db.Column(db.Numeric(10, 2))
    custom_annual_price = db.Column(db.Numeric(10, 2))
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    billing_cycle = db.Column(db.String(20), default="monthly")
    start_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    
    current_vehicles = db.Column(db.Integer, default=0)
    current_drivers = db.Column(db.Integer, default=0)
    current_users = db.Column(db.Integer, default=0)
    current_storage_mb = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(20), default="active")
    auto_renew = db.Column(db.Boolean, default=True)
    
    payment_method = db.Column(db.String(50), default="manual")
    last_payment_date = db.Column(db.Date)
    next_payment_date = db.Column(db.Date)
    payment_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = db.relationship("Tenant", backref="subscriptions")
    plan = db.relationship("SubscriptionPlan")


class SubscriptionPayment(db.Model):
    __tablename__ = "subscription_payments"

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey("tenant_subscriptions.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default="success")
    notes = db.Column(db.Text)
    invoice_url = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscription = db.relationship("TenantSubscription", backref="payments")


class VehicleServiceLog(db.Model):
    """Service and maintenance history log for vehicles"""
    __tablename__ = "vehicle_service_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)

    # Service Details
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # oil_change, filter_replacement, tire_service, etc.
    service_description = db.Column(db.Text)

    # Odometer Reading
    odometer_reading = db.Column(db.Integer)

    # Garage/Service Center Information
    garage_name = db.Column(db.String(200))
    garage_contact = db.Column(db.String(20))
    garage_address = db.Column(db.Text)

    # Parts Replaced (stored as JSON string)
    parts_replaced = db.Column(db.Text)  # JSON: [{"part": "Oil Filter", "cost": 500}]

    # Costs
    labor_cost = db.Column(db.Numeric(10, 2), default=0)
    parts_cost = db.Column(db.Numeric(10, 2), default=0)
    total_cost = db.Column(db.Numeric(10, 2), default=0)

    # Invoice/Receipt
    invoice_number = db.Column(db.String(100))
    invoice_path = db.Column(db.String(500))  # File attachment path

    # Next Service Due
    next_service_date = db.Column(db.Date)
    next_service_km = db.Column(db.Integer)

    # Additional Notes
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    vehicle = db.relationship("Vehicle", backref="service_logs")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User")


class VehicleServiceSchedule(db.Model):
    """Predefined service schedules for vehicle types"""
    __tablename__ = "vehicle_service_schedules"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_type = db.Column(db.String(50))  # Truck, Container, etc.
    service_type = db.Column(db.String(50))
    interval_months = db.Column(db.Integer)
    interval_km = db.Column(db.Integer)
    description = db.Column(db.Text)

    tenant = db.relationship("Tenant")


class VehicleFuelLog(db.Model):
    """Vehicle fuel consumption tracking with efficiency calculations."""
    __tablename__ = "vehicle_fuel_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)

    fueling_date = db.Column(db.Date, nullable=False)
    odometer_reading = db.Column(db.Integer, nullable=False)
    fuel_liters = db.Column(db.Numeric(10, 2), nullable=False)
    fuel_price_per_liter = db.Column(db.Numeric(8, 2))
    total_cost = db.Column(db.Numeric(10, 2))

    fuel_station = db.Column(db.String(200))
    fuel_type = db.Column(db.String(20))  # Diesel, Petrol, CNG

    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    payment_method = db.Column(db.String(50))
    receipt_number = db.Column(db.String(100))
    receipt_path = db.Column(db.String(500))

    # Calculated fields
    distance_since_last = db.Column(db.Integer)
    efficiency_km_per_liter = db.Column(db.Numeric(5, 2))
    cost_per_km = db.Column(db.Numeric(8, 2))

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    vehicle = db.relationship("Vehicle", backref="fuel_logs")
    driver = db.relationship("Driver")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User")


class VehicleDriverAssignment(db.Model):
    """Historical tracking of driver assignments to vehicles."""
    __tablename__ = "vehicle_driver_assignments"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False, index=True)

    # Assignment Details
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    assignment_date = db.Column(db.Date, default=date.today)

    # End Assignment Details
    ended_at = db.Column(db.DateTime)
    ended_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    end_date = db.Column(db.Date)
    end_reason = db.Column(db.Text)

    # Notes
    assignment_notes = db.Column(db.Text)
    handover_notes = db.Column(db.Text)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    vehicle = db.relationship("Vehicle", backref="driver_assignments")
    driver = db.relationship("Driver", backref="vehicle_assignments")
    assigner = db.relationship("User", foreign_keys=[assigned_by])
    ender = db.relationship("User", foreign_keys=[ended_by])

    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.assignment_date).days
        return (date.today() - self.assignment_date).days


class CustomerCategory(db.Model):
    """Customer category definitions for classification"""
    __tablename__ = "customer_categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category_code", name="uq_customer_category_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    
    # Credit Settings
    min_credit_limit = db.Column(db.Numeric(12, 2), default=0)
    max_credit_limit = db.Column(db.Numeric(12, 2), default=0)
    default_payment_terms = db.Column(db.String(50), default='Net 30')
    
    # Service Level Settings
    service_priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    sla_hours = db.Column(db.Integer, default=48)  # Service Level Agreement hours
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship("Tenant")


class CustomerCredit(db.Model):
    """Customer credit management for transport business"""
    __tablename__ = "customer_credits"
    __table_args__ = (
        UniqueConstraint("vendor_id", name="uq_customer_credit_vendor"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Credit Limits
    credit_limit = db.Column(db.Numeric(12, 2), default=0)
    available_credit = db.Column(db.Numeric(12, 2), default=0)
    current_outstanding = db.Column(db.Numeric(12, 2), default=0)
    
    # Credit Terms
    credit_period_days = db.Column(db.Integer, default=30)  # Net 15, 30, 60 days
    payment_terms = db.Column(db.String(50), default='Net 30')
    
    # Status
    is_credit_hold = db.Column(db.Boolean, default=False)
    hold_reason = db.Column(db.Text)
    credit_status = db.Column(db.String(20), default='active')  # active, hold, suspended
    
    # Monitoring
    last_payment_date = db.Column(db.Date)
    last_invoice_date = db.Column(db.Date)
    dso_days = db.Column(db.Integer, default=0)  # Days Sales Outstanding
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    # Relationships
    vendor = db.relationship("Vendor", backref="credit_info")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User", foreign_keys=[created_by])
    
    @property
    def credit_utilization_pct(self):
        if self.credit_limit and self.credit_limit > 0:
            return (self.current_outstanding / self.credit_limit) * 100
        return 0


class CustomerNotification(db.Model):
    """Customer notifications and preferences"""
    __tablename__ = "customer_notifications"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Notification Details
    notification_type = db.Column(db.String(50))  # payment_reminder, delivery_update, document_upload, general
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_email_sent = db.Column(db.Boolean, default=False)
    is_sms_sent = db.Column(db.Boolean, default=False)
    is_push_sent = db.Column(db.Boolean, default=True)
    
    # Preferences
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="notifications")
    tenant = db.relationship("Tenant")


class CustomerDocument(db.Model):
    """Customer uploaded documents"""
    __tablename__ = "customer_documents"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Document Details
    document_type = db.Column(db.String(50))  # invoice, receipt, contract, identity_proof, other
    document_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="documents")
    uploader = db.relationship("User", foreign_keys=[uploaded_by])
    approver = db.relationship("User", foreign_keys=[approved_by])
    tenant = db.relationship("Tenant")


class CustomerAnalytics(db.Model):
    """Customer performance analytics cache and calculation results"""
    __tablename__ = "customer_analytics"
    __table_args__ = (
        UniqueConstraint("vendor_id", "period_start", "period_end", name="uq_customer_analytics_period"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Period Definition
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='monthly')  # daily, weekly, monthly, quarterly, yearly
    
    # Performance Metrics
    total_revenue = db.Column(db.Numeric(15, 2), default=0)
    total_bills = db.Column(db.Integer, default=0)
    total_deliveries = db.Column(db.Integer, default=0)
    on_time_deliveries = db.Column(db.Integer, default=0)
    delayed_deliveries = db.Column(db.Integer, default=0)
    
    # Financial Metrics
    avg_order_value = db.Column(db.Numeric(12, 2), default=0)
    total_payments = db.Column(db.Numeric(15, 2), default=0)
    outstanding_balance = db.Column(db.Numeric(15, 2), default=0)
    
    # Satisfaction Metrics
    customer_satisfaction_score = db.Column(db.Numeric(5, 2), default=0)
    total_feedback_entries = db.Column(db.Integer, default=0)
    positive_feedback_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    # Calculated Fields
    on_time_delivery_rate = db.Column(db.Numeric(5, 2), default=0)  # percentage
    customer_lifetime_value = db.Column(db.Numeric(15, 2), default=0)
    churn_probability = db.Column(db.Numeric(5, 2), default=0)  # percentage
    growth_rate = db.Column(db.Numeric(5, 2), default=0)  # percentage
    
    # Timestamps
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="analytics")
    tenant = db.relationship("Tenant")


class CustomerCommunication(db.Model):
    """Customer communication history"""
    __tablename__ = "customer_communications"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Communication Details
    communication_type = db.Column(db.String(50))  # email, phone, meeting, complaint
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    direction = db.Column(db.String(20))  # inbound, outbound
    
    # Status & Priority
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Metadata
    communicated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    communication_date = db.Column(db.DateTime, default=datetime.utcnow)
    next_followup = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="communications")
    communicator = db.relationship("User", foreign_keys=[communicated_by])


class CustomerFeedback(db.Model):
    """Customer feedback collection"""
    __tablename__ = "customer_feedback"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Feedback Details
    feedback_type = db.Column(db.String(50))  # service, delivery, billing, general
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback_text = db.Column(db.Text)
    resolution_status = db.Column(db.String(20))  # pending, resolved, escalated
    
    # Metadata
    feedback_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    resolved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="feedback")
    resolver = db.relationship("User", foreign_keys=[resolved_by])


class CustomerTransaction(db.Model):
    """Customer transaction history for credit management"""
    __tablename__ = "customer_transactions"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    transport_bill_id = db.Column(db.Integer, db.ForeignKey("transport_bills.id"), index=True)
    
    # Transaction Details
    transaction_type = db.Column(db.String(20), nullable=False)  # invoice, payment, credit_adjustment
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    balance_after = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Payment Details (for payment transactions)
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    bank_reference = db.Column(db.String(100))
    
    # Dates
    transaction_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    
    # Notes
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    # Relationships
    vendor = db.relationship("Vendor", backref="transactions")
    transport_bill = db.relationship("TransportBill", backref="credit_transactions")
    tenant = db.relationship("Tenant")
    creator = db.relationship("User", foreign_keys=[created_by])


class PodStatus(db.Model):
    """POD status master table"""
    __tablename__ = "pod_status"
    
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(20), unique=True, nullable=False)
    status_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    color_code = db.Column(db.String(10))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Relationships
    tenant = db.relationship("Tenant", backref="pod_statuses")
    tracking_entries = db.relationship("PodTracking", backref="status")


class PodTracking(db.Model):
    """POD tracking table for status history"""
    __tablename__ = "pod_tracking"
    
    id = db.Column(db.Integer, primary_key=True)
    transport_bill_id = db.Column(db.Integer, db.ForeignKey('transport_bills.id'), nullable=False)
    status_code = db.Column(db.String(20), db.ForeignKey('pod_status.status_code'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    remarks = db.Column(db.Text)
    location = db.Column(db.String(200))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Relationships
    transport_bill = db.relationship('TransportBill', backref='pod_tracking')
    updated_by_user = db.relationship('User', backref='pod_updates')
    tenant = db.relationship("Tenant", backref="pod_tracking")
