# Vehicle Expense Tracking

A centralized expense view for each vehicle aggregating all fuel, maintenance, repair, and other expenses with categorization and cost analysis.

## Overview

While the system has an Expense module, expenses are not easily viewable in a vehicle-centric manner. This feature creates a dedicated expense history page for each vehicle, categorizing expenses and providing cost analytics to understand the true cost of operating each vehicle.

## Business Value

- Understand total cost of ownership per vehicle
- Identify vehicles with high maintenance costs
- Track fuel consumption patterns
- Budget planning for vehicle operations
- Compare expenses across vehicles
- Detect anomalies (unusual fuel costs, frequent repairs)

## Key Features

### 1. Expense List View

**Columns:**
- Date
- Category (Fuel/Maintenance/Repairs/Insurance/Tax/Other)
- Description
- Vendor/Garage Name
- Amount (₹)
- Payment Method
- Bill/Receipt Number
- Actions (View/Edit/Delete)

### 2. Expense Categories

**Predefined Categories:**
- **Fuel** - All fuel purchases
- **Maintenance** - Regular servicing, oil changes
- **Repairs** - Breakdown repairs, part replacements
- **Tires** - Tire purchases and repairs
- **Insurance** - Premium payments
- **Tax** - Road tax, permits
- **Accessories** - Add-ons, modifications
- **Other** - Miscellaneous

### 3. Filters

- Date Range
- Category (multi-select dropdown)
- Expense above/below amount
- Vendor name search

### 4. Summary Statistics

- Total Expenses (selected period)
- Expense by Category (breakdown chart)
- Average Expense per Month
- Highest Expense Category
- Recent 30 days expense total

### 5. Expense Entry Enhancement

When adding expense with vehicle selected:
- Auto-calculate fuel efficiency (if fuel expense + odometer provided)
- Show last expense of same category
- Suggest vendors from history

### 6. Recurring Expense Reminders

- Flag vehicles with upcoming insurance renewal
- Flag vehicles due for scheduled maintenance

### 7. Comparison View (Optional)

- Compare this vehicle's expenses with fleet average
- Month-over-month expense trend

## Technical Implementation

### New Route Required
```
GET /vehicles/<id>/expenses
GET /vehicles/<id>/expenses/add
```

### Expense Model Enhancement
```python
# Add to Expense model if not present:
category = db.Column(db.String(50), default='Other')  # fuel, maintenance, repairs, etc.
odometer_reading = db.Column(db.Integer)  # for fuel efficiency
fuel_liters = db.Column(db.Numeric(10, 2))  # for fuel entries
vendor_name = db.Column(db.String(200))  # garage/fuel station name

# Existing fields already support:
# - amount
# - expense_date
# - description
# - receipt_path
```

### Database Queries
```python
# All vehicle expenses
expenses = Expense.query.filter_by(vehicle_id=vehicle_id).order_by(desc(expense_date))

# Category breakdown
category_totals = db.session.query(
    Expense.category,
    func.sum(Expense.amount).label('total')
).filter_by(vehicle_id=vehicle_id).group_by(Expense.category)

# Monthly totals for trend
monthly_expenses = db.session.query(
    func.date_format(Expense.expense_date, '%Y-%m').label('month'),
    func.sum(Expense.amount).label('total')
).filter_by(vehicle_id=vehicle_id).group_by('month').order_by('month')
```

### UI Components
- Category filter pills/buttons
- Expense table with category badges
- Pie/bar chart for category breakdown
- Summary cards (Total, Monthly Avg, Top Category)
- Add Expense button (quick modal form)

## Acceptance Criteria

- [ ] All expenses for vehicle listed chronologically
- [ ] Expenses categorized with visual badges
- [ ] Filter by category and date range works
- [ ] Total expenses calculated correctly
- [ ] Category breakdown shows percentages
- [ ] Can add new expense directly from vehicle page
- [ ] Fuel efficiency auto-calculated when odometer provided
- [ ] Edit/Delete expense functionality
- [ ] Export to Excel available

## Dependencies

- Existing Expense model (may need category field)
- Vehicle model
- Driver model (for fueling records)

## Migration Required
```python
# Add category field to existing expenses
def migrate_expense_categories():
    # Set default category based on description keywords
    for expense in Expense.query.all():
        desc = expense.description.lower()
        if 'fuel' in desc or 'diesel' in desc or 'petrol' in desc:
            expense.category = 'fuel'
        elif 'maint' in desc or 'service' in desc or 'oil' in desc:
            expense.category = 'maintenance'
        # ... etc
```

## Estimated Effort

- Model updates: 2 hours
- Migration: 2 hours
- Backend API: 4 hours
- Frontend UI: 6 hours
- Charts/Visualizations: 3 hours
- Testing: 3 hours
