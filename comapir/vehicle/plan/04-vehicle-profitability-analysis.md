# Vehicle Profitability Analysis

A financial performance dashboard for each vehicle calculating revenue from trips minus all expenses to show true profitability with trend analysis.

## Overview

This feature combines trip revenue data with expense data to calculate the net profitability of each vehicle. It provides P&L (Profit & Loss) statements per vehicle, enabling fleet managers to identify their most and least profitable assets.

## Business Value

- Identify most profitable vehicles in fleet
- Identify loss-making vehicles needing attention
- Make data-driven decisions on vehicle retention/disposal
- Compare profitability across vehicle types/sizes
- Track profitability trends over time
- Optimize vehicle deployment based on earnings

## Key Features

### 1. Profitability Summary Card

**Key Metrics:**
- Total Revenue (all trips)
- Total Expenses (all categories)
- **Net Profit/Loss** (highlighted prominently)
- Profit Margin % (Profit ÷ Revenue × 100)
- Revenue per Day (active days)
- Cost per Kilometer (if distance tracked)

### 2. Revenue Breakdown

- Trip Revenue (Freight charges)
- Additional charges (loading, unloading, etc.)
- Total Revenue

### 3. Expense Breakdown

- Fuel Costs
- Maintenance & Repairs
- Insurance
- Taxes & Permits
- Other Expenses
- Total Expenses

### 4. Monthly P&L Statement

Table showing month-by-month:
- Month/Year
- Revenue
- Expenses
- Net Profit/Loss
- Profit Margin %
- Comparison to previous month

### 5. Trend Charts

- Revenue vs Expenses trend (line chart, 12 months)
- Net profit trend (bar chart)
- Profit margin % trend

### 6. Fleet Comparison (Optional)

- This vehicle's profit margin vs fleet average
- Ranking among similar vehicle types
- Efficiency score

### 7. Period Selection

- Current Month
- Last 3 Months
- Last 6 Months
- Current Year
- Custom Date Range
- Lifetime (All time)

### 8. Alert Indicators

- Red alert if consistently unprofitable (3+ months)
- Yellow warning if margin below fleet average
- Green badge if top 10% performer

## Technical Implementation

### New Route Required
```
GET /vehicles/<id>/profitability
GET /vehicles/<id>/profitability/data?period=3m (JSON for charts)
```

### Calculation Logic
```python
def calculate_vehicle_profitability(vehicle_id, start_date, end_date):
    # Revenue calculation
    revenue = db.session.query(func.sum(TransportBill.rate)).join(
        DispatchTrip, DispatchTrip.bilty_id == TransportBill.id
    ).filter(
        DispatchTrip.vehicle_id == vehicle_id,
        DispatchTrip.trip_date.between(start_date, end_date)
    ).scalar() or 0
    
    # Expense calculation
    expenses = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.vehicle_id == vehicle_id,
        Expense.expense_date.between(start_date, end_date)
    ).group_by(Expense.category).all()
    
    total_expenses = sum(e.total for e in expenses)
    net_profit = revenue - total_expenses
    profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
    
    return {
        'revenue': revenue,
        'expenses': {e.category: e.total for e in expenses},
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'profit_margin': profit_margin
    }

# Monthly breakdown
for month in date_range_months:
    monthly_data[month] = calculate_vehicle_profitability(vehicle_id, month_start, month_end)
```

### UI Components
- Large profit/loss display (green/red color-coded)
- Revenue vs Expenses comparison bars
- Two-column breakdown (Revenue left, Expenses right)
- Monthly P&L table
- Trend charts (Chart.js)
- Period selector dropdown

## Data Requirements

- Trip data from `DispatchTrip` + `TransportBill`
- Expense data from `Expense` model
- Both filtered by vehicle_id and date range

## Acceptance Criteria

- [ ] Net profit/loss calculated accurately for selected period
- [ ] Revenue from trips correctly aggregated
- [ ] All expense categories summed correctly
- [ ] Monthly P&L table generated
- [ ] Profit margin percentage calculated
- [ ] Charts render revenue vs expenses trend
- [ ] Period selector changes all calculations
- [ ] Unprofitable vehicles clearly flagged
- [ ] Mobile-responsive layout

## Dependencies

- Features #2 (Trip History) and #3 (Expense Tracking)
- Chart.js or similar for visualizations

## Report Integration

This data can feed into:
- Fleet-wide profitability report
- Vehicle disposal/replacement recommendations
- Annual financial reporting

## Estimated Effort

- Calculation logic: 4 hours
- Backend API: 3 hours
- Frontend UI: 6 hours
- Charts implementation: 4 hours
- Testing with real data: 3 hours
