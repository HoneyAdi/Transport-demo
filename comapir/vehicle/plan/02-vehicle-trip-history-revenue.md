# Vehicle Trip History & Revenue Tracking

A comprehensive trip history page for each vehicle showing all completed trips with revenue details, filtering capabilities, and earnings analytics.

## Overview

This feature provides a dedicated trip history view for each vehicle, listing all trips (from DispatchTrip and TransportBill modules) with associated revenue, dates, routes, and status. It enables fleet managers to track vehicle utilization and earnings performance.

## Business Value

- Track individual vehicle performance and utilization
- Identify high/low revenue vehicles
- Calculate revenue per trip averages
- Analyze route profitability by vehicle
- Historical data for maintenance planning based on mileage

## Key Features

### 1. Trip History List View

**Columns:**
- Trip Number (e.g., TRP-00001)
- Trip Date
- Origin → Destination (route)
- Party/Customer Name
- Bilky/GR Number
- Status (Planned/Dispatched/Delivered/Closed)
- Freight Amount (₹)
- Distance (km) - if available from GPS

### 2. Filters & Search

- Date Range filter
- Status filter (multi-select)
- Party/Customer search
- Route search (Origin/Destination)
- Minimum/Maximum amount range

### 3. Summary Statistics Bar

- Total Trips (in selected period)
- Total Revenue
- Average Revenue per Trip
- Total Distance Covered
- Average Distance per Trip

### 4. Pagination

- 25/50/100 trips per page options
- Jump to specific page
- Export current page/all to Excel

### 5. Sorting

- Sort by Date, Amount, Trip Number, Status
- Ascending/Descending toggle

### 6. Trip Detail View

Clicking a trip shows:
- Complete trip details
- Associated Bilky/GR details
- Driver assigned
- POD status
- Payment status

### 7. Revenue Charts (Optional Enhancement)

- Monthly revenue trend for this vehicle
- Revenue by route (top 5)
- Revenue by party (top 5)

## Technical Implementation

### New Route Required
```
GET /vehicles/<id>/trips
GET /vehicles/<id>/trips/data (for AJAX/JSON)
```

### Database Queries
```python
# Base query
query = db.session.query(
    DispatchTrip,
    TransportBill,
    Vendor  # for party name
).join(
    TransportBill, DispatchTrip.bilty_id == TransportBill.id
).filter(
    DispatchTrip.vehicle_id == vehicle_id
)

# Apply filters
if date_from:
    query = query.filter(DispatchTrip.trip_date >= date_from)
if status_filter:
    query = query.filter(DispatchTrip.status.in_(status_filter))

# Summary stats
total_trips = query.count()
total_revenue = db.session.query(func.sum(TransportBill.rate)).filter(...)
```

### UI Components
- Filter panel (collapsible)
- Summary cards (4 metrics)
- Data table with sorting
- Pagination controls
- Export button

## Data Model Considerations

No new models required. Uses existing:
- `DispatchTrip` (trip data)
- `TransportBill` (revenue/GR data)
- `Vendor` (party information)

May need to add to `DispatchTrip`:
- `distance_km` (optional, calculated from GPS or manual entry)

## Acceptance Criteria

- [ ] Trip history accessible from vehicle dashboard
- [ ] All trips for vehicle listed chronologically
- [ ] Revenue amount shown for each trip
- [ ] Filters work: Date range, Status, Party, Amount
- [ ] Summary statistics calculated correctly
- [ ] Pagination functional
- [ ] Export to Excel available
- [ ] Sorting by columns works
- [ ] Mobile-responsive table

## Integration Points

- Links to trip detail pages
- Links to bilty/invoice print pages
- Links to driver assignment pages

## Estimated Effort

- Backend API: 4-6 hours
- Frontend UI: 6-8 hours
- Testing & Refinement: 3-4 hours
