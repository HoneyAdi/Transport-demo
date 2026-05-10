# Vehicle Dashboard/Profile View

A comprehensive vehicle profile page that consolidates all vehicle information, performance metrics, and operational status into a single dashboard view.

## Overview

The current system only provides a list view and edit form for vehicles. This feature adds a detailed dashboard page accessible by clicking a vehicle's registration number, displaying all vehicle data including documents status, assigned driver, recent trips, and quick action buttons.

## Business Value

- Single-page visibility into complete vehicle status
- Quick identification of document expiries and compliance issues
- Faster decision-making for fleet operations
- Reduced time searching for vehicle information across modules

## Key Features

### 1. Vehicle Header Card
- Large registration number display
- Status badge (Active/Inactive/Maintenance/Sold)
- Vehicle type icon + Make/Model/Year
- Quick actions: Edit, Print, View Trips

### 2. Information Sections (Tabs or Cards)

**Basic Details:**
- Registration Number, Type, Make, Model, Year, Color
- Fuel Type, Engine/Chassis Number
- Purchase Date, Age of Vehicle

**Capacity & Specifications:**
- Seating Capacity, Load Capacity (kg)
- Truck Size category

**Owner Information:**
- Owner Name, Contact
- Ownership type (Company/Owner/Leased)

**Assigned Driver:**
- Current driver name and photo (if available)
- Driver contact, license details
- Assignment date

### 3. Document Status Panel

Visual indicator for each document:
- Insurance (color-coded: Green=Valid, Yellow=Expiring<30days, Red=Expired)
- Fitness Certificate
- Permits (1-year, 5-year)
- Road Tax
- PUC
- Days remaining until expiry

### 4. Financial Summary Card

- Total trips completed (lifetime)
- Total revenue generated
- Total expenses (fuel + maintenance)
- Net profit/loss for this vehicle
- Average revenue per trip

### 5. Recent Activity

- Last 5 trips with dates, destinations, revenue
- Last maintenance/fuel entry
- Last expense recorded

### 6. Attachments Gallery

- Quick view of uploaded documents
- Insurance certificate, Fitness certificate
- Download links

## Technical Implementation

### New Route Required
```
GET /vehicles/<id>/dashboard
```

### Database Queries Needed
```python
# Vehicle basic info
vehicle = Vehicle.query.get(id)

# Assigned driver
driver = Driver.query.get(vehicle.driver_id)

# Trip statistics
trip_count = DispatchTrip.query.filter_by(vehicle_id=id).count()
total_revenue = db.session.query(func.sum(TransportBill.rate)).filter(...)

# Recent trips
recent_trips = DispatchTrip.query.filter_by(vehicle_id=id).order_by(desc(created_at)).limit(5)

# Expenses
vehicle_expenses = Expense.query.filter_by(vehicle_id=id).all()

# Document expiry calculations
expiry_status = calculate_expiry_status(vehicle.insurance_expiry, ...)
```

### UI Components
- Vehicle header with action buttons
- Tab navigation: Overview | Documents | Trips | Expenses | History
- Progress bars for document validity
- Statistics cards (4-card grid)
- Data tables for recent trips/expenses

## Acceptance Criteria

- [ ] Clicking vehicle registration number opens dashboard
- [ ] All vehicle details visible on single page
- [ ] Document expiry status color-coded (green/yellow/red)
- [ ] Driver information displayed if assigned
- [ ] Trip count and financial summary visible
- [ ] Recent activity (last 5 trips) listed
- [ ] Mobile-responsive layout
- [ ] Print-friendly view available

## Dependencies

- Existing Vehicle model
- Existing Driver model
- Existing DispatchTrip model
- Existing Expense model

## Estimated Effort

- Backend: 4-6 hours
- Frontend: 6-8 hours
- Testing: 2-3 hours
