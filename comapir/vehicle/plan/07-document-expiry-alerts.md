# Document Expiry Alert System

An automated alert system that monitors vehicle document expiry dates (insurance, fitness, permits) and provides visual warnings, email notifications, and dashboard alerts.

## Overview

The current system stores document expiry dates but has no alerting mechanism. This feature adds proactive notifications for upcoming expiries and visual indicators on the dashboard, helping avoid legal/operational issues from expired documents.

## Business Value

- Avoid fines and penalties from expired documents
- Prevent vehicle downtime due to compliance issues
- Reduce last-minute rush for renewals
- Maintain fleet compliance standards
- Lower legal and operational risks

## Key Features

### 1. Document Expiry Tracking

**Documents Monitored:**
- Insurance Certificate
- Fitness Certificate
- National Permit (1-year)
- National Permit (5-year)
- Road Tax
- PUC (Pollution Under Control)

### 2. Alert Levels & Colors

**Green:** Valid (more than 30 days)
**Yellow:** Expiring Soon (15-30 days)
**Orange:** Critical (7-14 days)
**Red:** Expired or Expiring < 7 days

### 3. Alert Types

**Visual Alerts:**
- Color-coded badges on vehicle list
- Warning icons on vehicle dashboard
- Expiry countdown badges ("5 days left")
- Expired document highlights

**Dashboard Widget:**
- "Documents Expiring This Week" list
- Count of documents by status (Green/Yellow/Red)
- Click to view details

**Email/Notification Alerts:**
- 30 days before expiry
- 15 days before expiry
- 7 days before expiry
- Day of expiry
- Daily reminder if expired

### 4. Vehicle List View Enhancement

Add columns or filters:
- Insurance Status (color badge)
- Fitness Status (color badge)
- Any Document Expiring Soon flag

### 5. Vehicle Dashboard Enhancement

Document panel showing:
- All documents with expiry dates
- Days remaining countdown
- Color status indicator
- Download/View document button
- "Mark as Renewed" action (updates date)

### 6. Master Alert Dashboard

Fleet-wide view showing:
- All vehicles with expiring documents
- Filter by expiry timeframe (7 days, 30 days, 90 days)
- Filter by document type
- Export list for action

### 7. Bulk Renewal Tracking

- Select multiple vehicles
- Mark documents as renewed with new dates
- Bulk upload new expiry dates

### 8. Renewal History (Optional)

- Track document renewal dates
- Cost of renewals
- Renewal vendor details

## Technical Implementation

### Alert Calculation Logic
```python
from datetime import date, timedelta

def get_document_status(expiry_date):
    if not expiry_date:
        return 'unknown', 'No date set'
    
    today = date.today()
    days_remaining = (expiry_date - today).days
    
    if days_remaining < 0:
        return 'expired', f'Expired {abs(days_remaining)} days ago'
    elif days_remaining <= 7:
        return 'critical', f'{days_remaining} days left'
    elif days_remaining <= 14:
        return 'warning', f'{days_remaining} days left'
    elif days_remaining <= 30:
        return 'expiring', f'{days_remaining} days left'
    else:
        return 'valid', f'{days_remaining} days left'

# For each vehicle
def get_vehicle_document_alerts(vehicle):
    alerts = []
    
    docs = [
        ('Insurance', vehicle.insurance_expiry),
        ('Fitness Certificate', vehicle.fitness_expiry),
        ('Permit 1-Year', vehicle.permit_1_year_expiry),
        ('Permit 5-Year', vehicle.permit_5_year_expiry),
        ('Road Tax', vehicle.road_tax_expiry),
        ('PUC', vehicle.puc_expiry),
    ]
    
    for doc_name, expiry in docs:
        status, message = get_document_status(expiry)
        if status in ['expired', 'critical', 'warning']:
            alerts.append({
                'document': doc_name,
                'status': status,
                'message': message,
                'expiry_date': expiry
            })
    
    return alerts
```

### Database - No Changes Required

Uses existing Vehicle model fields:
- `insurance_expiry`
- `fitness_expiry`
- `permit_1_year_expiry`
- `permit_5_year_expiry`
- `road_tax_expiry`
- `puc_expiry`

### New Routes
```
GET /vehicle-documents/alerts
GET /vehicle-documents/expiring?days=30
POST /vehicles/<id>/documents/update-expiry
```

### UI Components
- Color-coded badge component
- Countdown display
- Alert banner on vehicle dashboard
- Master alerts table
- Notification bell with badge count

### Email Template Structure
```
Subject: [URGENT] Vehicle Documents Expiring Soon - [Vehicle Number]

Documents requiring attention:
- Insurance: Expires in 5 days (2024-02-15)
- Fitness: Expires in 12 days (2024-02-22)

Vehicle: MH01AB1234
Click to view: [Link]
```

## Acceptance Criteria

- [ ] Color codes display correctly (Green/Yellow/Orange/Red)
- [ ] Days remaining shown for each document
- [ ] Expired documents clearly marked
- [ ] Vehicle list shows document status indicators
- [ ] Alert dashboard lists all expiring documents
- [ ] Can filter by expiry timeframe
- [ ] Can update expiry dates from alert view
- [ ] Email notifications sent at configured intervals
- [ ] Mobile-responsive alert badges

## Configuration Options

```python
# Alert thresholds (configurable)
ALERT_CRITICAL_DAYS = 7
ALERT_WARNING_DAYS = 15
ALERT_NOTICE_DAYS = 30

# Notification schedule
NOTIFICATION_SCHEDULE = [
    30,  # days before
    15,
    7,
    0,   # on expiry day
]
```

## Integration Points

- Vehicle list view (add status columns)
- Vehicle dashboard (document panel)
- Main dashboard (alert widget)
- Email notification system
- Optional: SMS notifications

## Estimated Effort

- Alert calculation logic: 3 hours
- Badge/indicator components: 4 hours
- Alert dashboard: 4 hours
- Email notifications: 5 hours
- Vehicle list integration: 3 hours
- Testing: 3 hours
