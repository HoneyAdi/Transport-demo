# Vehicle Service/Maintenance Log

A detailed maintenance history tracking system for each vehicle recording all service activities, scheduled maintenance, garage details, and maintenance costs.

## Overview

The current system tracks document expiry dates but lacks a proper service history log. This feature creates a maintenance log showing all past services, upcoming scheduled maintenance, service costs, and garage information for proactive vehicle maintenance management.

## Business Value

- Maintain complete service history for each vehicle
- Track maintenance costs over vehicle lifetime
- Schedule preventive maintenance to avoid breakdowns
- Identify vehicles with high maintenance costs
- Track service warranties
- Compliance with manufacturer service schedules
- Resale value documentation

## Key Features

### 1. Service History List

**Columns:**
- Service Date
- Service Type (dropdown)
- Garage/Service Center Name
- Odometer Reading (at service)
- Description of work done
- Parts replaced (list)
- Total Cost
- Next Service Due (date/km)
- Invoice/Receipt Number
- Actions (View Receipt, Edit, Delete)

### 2. Service Types (Predefined)

- **Oil Change** - Engine oil replacement
- **Filter Replacement** - Oil/air/fuel filters
- **Tire Service** - Rotation, alignment, replacement
- **Brake Service** - Pad replacement, fluid change
- **Battery Service** - Replacement, charging
- **AC Service** - Gas refill, cleaning
- **General Service** - Routine checkup
- **Repair** - Breakdown repairs
- **Inspection** - Safety/inspection check

### 3. Scheduled Maintenance

**Upcoming Service Reminders:**
- Based on date (e.g., every 3 months)
- Based on odometer (e.g., every 5000 km)
- Overdue alerts
- Email/notification triggers

### 4. Maintenance Summary

- Total services completed
- Total maintenance cost (lifetime)
- Average cost per service
- Last service date
- Next service due
- Services this year

### 5. Garage/Vendor Management

- Track preferred service centers
- Compare costs across garages
- Garage contact details
- Service quality notes

### 6. Parts Inventory Tracking (Optional)

- Parts replaced history
- Part warranty tracking
- Common replacement parts per vehicle

### 7. Service Due Alerts

- Dashboard widget showing vehicles needing service
- Alerts 7 days before due date
- Alerts at 1000 km before due odometer

## Technical Implementation

### New Model Required
```python
class VehicleServiceLog(db.Model):
    __tablename__ = "vehicle_service_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # Service Details
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # oil_change, repair, etc.
    service_description = db.Column(db.Text)
    
    # Odometer
    odometer_reading = db.Column(db.Integer)
    
    # Garage Information
    garage_name = db.Column(db.String(200))
    garage_contact = db.Column(db.String(20))
    garage_address = db.Column(db.Text)
    
    # Parts Replaced (JSON array)
    parts_replaced = db.Column(db.Text)  # JSON: [{"part": "Oil Filter", "cost": 500}]
    
    # Costs
    labor_cost = db.Column(db.Numeric(10, 2), default=0)
    parts_cost = db.Column(db.Numeric(10, 2), default=0)
    total_cost = db.Column(db.Numeric(10, 2), default=0)
    
    # Invoice
    invoice_number = db.Column(db.String(100))
    invoice_path = db.Column(db.String(500))  # File attachment
    
    # Next Service Due
    next_service_date = db.Column(db.Date)
    next_service_km = db.Column(db.Integer)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

class VehicleServiceSchedule(db.Model):
    """Predefined service schedules for vehicle types"""
    __tablename__ = "vehicle_service_schedules"
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50))  # Truck, Container, etc.
    service_type = db.Column(db.String(50))
    interval_months = db.Column(db.Integer)
    interval_km = db.Column(db.Integer)
    description = db.Column(db.Text)
```

### New Routes
```
GET /vehicles/<id>/services
POST /vehicles/<id>/services/create
GET /vehicles/<id>/services/<log_id>/edit
POST /vehicles/<id>/services/<log_id>/delete
```

### UI Components
- Service history table with expandable details
- "Add Service" modal form
- Service type filter buttons
- Upcoming service alert banner
- Summary cards (Total services, Total cost, Last service, Next due)
- Garage autocomplete dropdown

## Acceptance Criteria

- [ ] Can record new service entry with all details
- [ ] Service history listed chronologically
- [ ] Odometer reading tracked at each service
- [ ] Parts replaced can be listed
- [ ] Invoice/Receipt can be attached
- [ ] Next service date/km can be set
- [ ] Service due alerts appear when approaching
- [ ] Total maintenance cost calculated
- [ ] Filter by service type works
- [ ] Edit/Delete service entries

## Integration Points

- Links to Expense module (service costs auto-sync)
- Vehicle dashboard shows next service due
- Alerts feed into notification system

## Migration Strategy

- Start with empty logs for existing vehicles
- Optionally migrate past expenses categorized as "maintenance" or "repairs"
- Set next service dates based on last service date + interval

## Estimated Effort

- Database models: 3 hours
- Backend API: 5 hours
- Frontend forms: 6 hours
- Alert system: 4 hours
- Testing: 3 hours
