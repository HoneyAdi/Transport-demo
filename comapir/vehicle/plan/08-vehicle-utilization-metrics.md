# Vehicle Utilization Metrics

Analytics tracking active vs idle days, utilization percentage, and operational efficiency metrics for each vehicle to optimize fleet deployment.

## Overview

This feature tracks how actively each vehicle is being used - measuring days on the road versus idle days, utilization percentage, and comparing against fleet averages to identify underutilized assets.

## Business Value

- Identify underutilized vehicles for reassignment or disposal
- Optimize fleet size based on actual usage
- Track vehicle productivity trends
- Make data-driven decisions on vehicle purchases
- Improve fleet ROI

## Key Features

### 1. Utilization Summary Card

**Key Metrics:**
- **Utilization %** - (Active Days / Total Days) × 100
- Active Days (with trips assigned)
- Idle Days (no trips)
- Total Trips Completed
- Average Trips per Active Day

### 2. Time Period Selection

- Current Month
- Last 3 Months
- Last 6 Months
- Current Year
- Custom Date Range

### 3. Active vs Idle Breakdown

**Visual Representation:**
- Calendar view showing active days (green) vs idle (gray)
- Bar chart: Active days per month
- Pie chart: Active % vs Idle %

### 4. Trend Analysis

- Utilization % trend over months
- Comparison with fleet average
- Comparison with same vehicle type (all trucks, all tempos)

### 5. Efficiency Metrics

- Revenue per Active Day
- Revenue per Idle Day (opportunity cost)
- Cost per Day (regardless of usage)
- Break-even utilization %

### 6. Underutilization Alerts

- Flag vehicles with < 50% utilization
- Flag vehicles idle for > 7 consecutive days
- Weekly utilization report

### 7. Fleet Comparison Table

Rank all vehicles by:
- Utilization %
- Active Days
- Revenue per Day
- Idle Days Count

## Technical Implementation

### Calculation Logic
```python
from datetime import date, timedelta

def calculate_vehicle_utilization(vehicle_id, start_date, end_date):
    total_days = (end_date - start_date).days + 1
    
    # Get all days with at least one trip
    active_dates = db.session.query(
        func.date(DispatchTrip.trip_date).label('trip_date')
    ).filter(
        DispatchTrip.vehicle_id == vehicle_id,
        DispatchTrip.trip_date.between(start_date, end_date)
    ).distinct().all()
    
    active_days = len(active_dates)
    idle_days = total_days - active_days
    utilization_pct = (active_days / total_days * 100) if total_days > 0 else 0
    
    # Get trip count
    total_trips = DispatchTrip.query.filter(
        DispatchTrip.vehicle_id == vehicle_id,
        DispatchTrip.trip_date.between(start_date, end_date)
    ).count()
    
    return {
        'total_days': total_days,
        'active_days': active_days,
        'idle_days': idle_days,
        'utilization_pct': round(utilization_pct, 2),
        'total_trips': total_trips,
        'avg_trips_per_active_day': round(total_trips / active_days, 2) if active_days > 0 else 0
    }

# Fleet average comparison
def get_fleet_average_utilization(start_date, end_date):
    vehicles = Vehicle.query.filter_by(status='Active').all()
    utilization_values = []
    
    for v in vehicles:
        util = calculate_vehicle_utilization(v.id, start_date, end_date)
        utilization_values.append(util['utilization_pct'])
    
    return sum(utilization_values) / len(utilization_values) if utilization_values else 0
```

### Monthly Breakdown
```python
def get_monthly_utilization(vehicle_id, months=6):
    results = []
    today = date.today()
    
    for i in range(months):
        month_date = today - timedelta(days=30*i)
        start = month_date.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        util = calculate_vehicle_utilization(vehicle_id, start, end)
        results.append({
            'month': start.strftime('%Y-%m'),
            'utilization_pct': util['utilization_pct'],
            'active_days': util['active_days'],
            'idle_days': util['idle_days']
        })
    
    return results
```

### New Routes
```
GET /vehicles/<id>/utilization
GET /vehicles/<id>/utilization/data?months=6 (JSON)
GET /fleet/utilization-report
```

### UI Components
- Large utilization % display
- Active vs Idle day counters
- Calendar heatmap (active days)
- Trend line chart
- Comparison bar (this vehicle vs fleet average)
- Underutilization alert banner

## Data Requirements

- `DispatchTrip` records with dates
- `Vehicle` status to filter active vehicles only

## Acceptance Criteria

- [ ] Utilization % calculated correctly for selected period
- [ ] Active days counted accurately (days with trips)
- [ ] Idle days calculated as remaining days
- [ ] Monthly trend chart displays
- [ ] Fleet average comparison shown
- [ ] Underutilized vehicles flagged
- [ ] Calendar view shows active/idle days
- [ ] Period selector updates all metrics
- [ ] Export utilization report to Excel

## Integration Points

- Vehicle dashboard (utilization widget)
- Fleet-wide reports
- Main dashboard (underutilization alerts)

## Estimated Effort

- Calculation logic: 4 hours
- Backend API: 3 hours
- Frontend UI: 5 hours
- Calendar heatmap: 4 hours
- Charts: 3 hours
- Testing: 3 hours
