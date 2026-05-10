# Windows Demo Deployment Guide
## Transport Management System

### Overview
This guide provides step-by-step instructions for deploying the Transport Management System on a Windows computer for client demonstration.

### Prerequisites for Client Computer

#### 1. Python Installation
- Download Python 3.9+ from https://www.python.org/downloads/windows/
- During installation, **check "Add Python to PATH"**
- Verify installation: Open Command Prompt and run `python --version`

#### 2. MySQL Database
- Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
- Install MySQL with default settings
- Set root password during installation (remember this password)
- Install MySQL Workbench for database management (optional but recommended)

#### 3. Git (Optional)
- Download from https://git-scm.com/download/win
- Required only if downloading from repository

---

## Quick Demo Setup (30 Minutes)

### Step 1: Prepare Application Files
1. Copy the entire `transport-master` folder to the client computer
2. Place it in a simple location like `C:\transport-demo\`

### Step 2: Database Setup
1. Open MySQL Command Line Client (from Start Menu)
2. Run these commands:
```sql
CREATE DATABASE transport_db;
CREATE USER 'transport_user'@'localhost' IDENTIFIED BY 'demo123';
GRANT ALL PRIVILEGES ON transport_db.* TO 'transport_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Environment Configuration
1. Navigate to the project folder: `cd C:\transport-demo`
2. Copy the environment file: `copy .env.example .env`
3. Edit `.env` file with Notepad and set:
```
SECRET_KEY=demo-secret-key-for-client-presentation
DB_HOST=localhost
DB_USER=transport_user
DB_PASSWORD=demo123
DB_NAME=transport_db
FLASK_ENV=production
SESSION_COOKIE_SECURE=false
```

### Step 4: Install Python Dependencies
1. Open Command Prompt as Administrator
2. Navigate to project: `cd C:\transport-demo`
3. Install dependencies:
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Initialize Database
1. Run database setup:
```cmd
python init_db.py
python -m flask db upgrade
```

### Step 6: Create Demo Data
1. Run demo data setup:
```cmd
python setup_demo_data.py
```

### Step 7: Launch Application
1. Start the web server:
```cmd
python webapp.py
```
2. Open browser and go to: `http://localhost:5000`
3. Default login credentials:
   - Username: `admin`
   - Password: `admin123`

---

## Portable Demo Package (Alternative)

For easier client setup, create a portable package:

### Option 1: Using Provided Scripts
Run the included setup script:
```cmd
setup_demo.bat
```

### Option 2: Manual Portable Setup
1. Install Python portable version to `C:\transport-demo\python`
2. Install dependencies locally:
```cmd
C:\transport-demo\python\python.exe -m pip install -r requirements.txt --target C:\transport-demo\lib
```

---

## Demo Checklist

### Before Demo
- [ ] Database is created and accessible
- [ ] All Python dependencies installed successfully
- [ ] Application starts without errors
- [ ] Demo data is populated
- [ ] Login credentials work
- [ ] All major features are functional

### Demo Features to Showcase
1. **Dashboard Overview**
   - Real-time statistics
   - Active trips and vehicles
   - Financial summaries

2. **Transport Management**
   - Create new transport bills
   - Vehicle and driver management
   - Trip scheduling

3. **Customer Portal**
   - Customer registration and login
   - Document management
   - Communication hub

4. **Reports & Analytics**
   - Financial reports
   - Vehicle performance
   - Customer analytics

5. **Admin Features**
   - User management
   - System configuration
   - Audit logs

---

## Troubleshooting

### Common Issues

#### 1. Python Not Found
**Error**: `'python' is not recognized`
**Solution**: 
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python39\python.exe`

#### 2. Database Connection Error
**Error**: `Can't connect to MySQL server`
**Solution**:
- Check MySQL service is running
- Verify database credentials in `.env`
- Test connection with MySQL Workbench

#### 3. Port Already in Use
**Error**: `Address already in use`
**Solution**:
- Stop other services on port 5000
- Or change port in `webapp.py`: `app.run(port=5001)`

#### 4. Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version compatibility

#### 5. Permission Issues
**Error**: `Permission denied`
**Solution**:
- Run Command Prompt as Administrator
- Check folder permissions

### Performance Tips
1. Use SSD storage for better performance
2. Ensure at least 4GB RAM available
3. Close unnecessary applications during demo
4. Pre-load all demo pages before client arrives

---

## Client Handover Package

### Files to Provide
1. `transport-master` folder (complete application)
2. This deployment guide
3. Demo user credentials document
4. Feature overview document
4. Contact information for support

### Documentation for Client
- User manual with screenshots
- Feature list and benefits
- Technical requirements
- Support contact information

---

## Post-Demo Support

### Quick Recovery Commands
```cmd
# Reset database
python init_db.py

# Restart application
taskkill /f /im python.exe
python webapp.py

# Check database connection
python check_db.py
```

### Backup and Restore
```cmd
# Backup database
mysqldump -u transport_user -p transport_db > backup.sql

# Restore database
mysql -u transport_user -p transport_db < backup.sql
```

---

## Security Notes for Demo

### Demo Environment
- Use demo-specific passwords
- Disable sensitive features in production mode
- Reset demo data after each client
- Don't use real customer data in demo

### Production Deployment
- Change all default passwords
- Enable HTTPS
- Configure firewall rules
- Set up regular backups
- Implement user authentication policies

---

## Contact Support

For technical issues during demo:
- Email: support@yourcompany.com
- Phone: +1-XXX-XXX-XXXX
- Remote support available upon request

---

**Last Updated**: May 2025
**Version**: 1.0
**Compatible**: Windows 10/11, Python 3.9+, MySQL 8.0+
