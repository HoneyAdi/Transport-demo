# Vehicle Fuel Log

A detailed fuel consumption tracking system recording every fueling event with odometer readings, fuel quantity, costs, and efficiency calculations for each vehicle.

## Overview

This feature tracks all fuel purchases for each vehicle, calculating fuel efficiency (km per liter) and monitoring fuel costs. It helps identify fuel consumption patterns, detect fuel theft or inefficiencies, and manage fuel budgets.

## Business Value

- Track fuel consumption patterns per vehicle
- Calculate fuel efficiency (km/liter)
- Identify vehicles with poor fuel economy
- Detect fuel theft or anomalies
- Budget fuel costs accurately
- Compare fuel efficiency across similar vehicles
- Optimize route planning based on fuel consumption

## Key Features

### 1. Fuel Log Entry Form

**Fields:**
- Fueling Date
- Odometer Reading (km)
- Fuel Quantity (liters)
- Fuel Price per Liter (₹)
- Total Cost (auto-calculated)
- Fuel Station/Vendor Name
- Fuel Type (Diesel/Petrol/CNG)
- Payment Method
- Bill/Receipt Number
- Driver Name (who fueled)
- Notes

### 2. Fuel Log List View

**Columns:**
- Date
- Odometer (km)
- Quantity (L)
- Total Cost (₹)
- Price/Liter (₹)
- Fuel Station
- **Efficiency (km/L)** - calculated from previous entry
- Driver

### 3. Efficiency Calculations

**Auto-calculated fields:**
- Distance since last fueling (km)
- Fuel efficiency (km per liter)
- Cost per kilometer (₹/km)
- Running average efficiency

```
Efficiency = (Current Odometer - Previous Odometer) / Quantity
```

### 4. Fuel Summary Statistics

- Total fuel consumed (lifetime)
- Total fuel cost (lifetime)
- Average efficiency (km/L)
- Best/Worst efficiency recorded
- Fuel cost this month
- Fuel consumption trend (chart)

### 5. Efficiency Alerts

- Alert if efficiency drops below threshold
- Alert if fuel quantity doesn't match expected consumption
- Flag suspicious fuel entries (efficiency too low/high)

### 6. Fuel Price Tracking

- Track fuel price changes over time
- Compare prices across fuel stations
- Budget variance analysis

### 7. Charts & Visualizations

- Fuel consumption trend (liters per month)
- Efficiency trend (km/L over time)
- Fuel cost trend (₹ per month)
- Top fuel stations by volume

### 8. Bulk Entry (Optional)

- Import fuel log from Excel
- Bulk update from fuel card statements

## Technical Implementation

### Model Enhancement or New Model

Option A: Enhance Expense Model
```python
# Add to Expense model
category = "fuel"  # Use expense category
fuel_liters = db.Column(db.Numeric(10, 2))
odometer_reading = db.Column(db.Integer)
fuel_station = db.Column(db.String(200))
fuel_price_per_liter = db.Column(db.Numeric(8, 2))
```

Option B: New Dedicated Model (Recommended)
```python
class VehicleFuelLog(db.Model):
    __tablename__ = "vehicle_fuel_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    
    fueling_date = db.Column(db.Date, nullable=False)
    odometer_reading = db.Column(db.Integer, nullable=False)  # km
    fuel_liters = db.Column(db.Numeric(10, 2), nullable=False)
    fuel_price_per_liter = db.Column(db.Numeric(8, 2))
    total_cost = db.Column(db.Numeric(10, 2))  # liters × price
    
    fuel_station = db.Column(db.String(200))
    fuel_type = db.Column(db.String(20))  # Diesel, Petrol, CNG
    
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    payment_method = db.Column(db.String(50))
    receipt_number = db.Column(db.String(100))
    receipt_path = db.Column(db.String(500))
    
    # Calculated fields (can be stored or calculated on-the-fly)
    distance_since_last = db.Column(db.Integer)  # km
    efficiency_km_per_liter = db.Column(db.Numeric(5, 2))  # km/L
    cost_per_km = db.Column(db.Numeric(8, 2))  # ₹/km
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicle = db.relationship("Vehicle", backref="fuel_logs")
    driver = db.relationship("Driver")
```

### Calculation Logic
```python
def calculate_efficiency(fuel_log):
    # Get previous fuel log
    previous = VehicleFuelLog.query.filter(
        VehicleFuelLog.vehicle_id == fuel_log.vehicle_id,
        VehicleFuelLog.fueling_date < fuel_log.fueling_date,
        VehicleFuelLog.id != fuel_log.id
    ).order_by(VehicleFuelLog.fueling_date.desc()).first()
    
    if previous:
        distance = fuel_log.odometer_reading - previous.odometer_reading
        fuel_log.distance_since_last = distance
        
        if fuel_log.fuel_liters > 0:
            fuel_log.efficiency_km_per_liter = distance / fuel_log.fuel_liters
            fuel_log.cost_per_km = fuel_log.total_cost / distance if distance > 0 else 0
    
    return fuel_log
```

### New Routes
```
GET /vehicles/<id>/fuel-log
POST /vehicles/<id>/fuel-log/create
GET /vehicles/<id>/fuel-log/<log_id>/edit
POST /vehicles/<id>/fuel-log/<log_id>/delete
```

## Acceptance Criteria

- [ ] Can record fuel entry with odometer, liters, cost
- [ ] Fuel efficiency auto-calculated from previous entry
- [ ] Fuel log listed chronologically with efficiency column
- [ ] Summary stats show average efficiency
- [ ] Alerts for low efficiency or suspicious entries
- [ ] Fuel cost trend chart displayed
- [ ] Can attach fuel receipt
- [ ] Edit/Delete fuel entries
- [ ] Filter by date range

## Integration Points

- Links to Vehicle Expense Tracking (fuel costs)
- Links to Profitability Analysis (fuel as expense category)
- Driver can be linked to fuel entry

## Estimated Effort

- Database model: 2 hours
- Calculation logic: 3 hours
- Backend API: 4 hours
- Frontend forms: 5 hours
- Charts: 3 hours
- Testing: 3 hours
