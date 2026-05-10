"""
Create vehicle service log tables directly in the database.
Run this script to create the missing tables.
"""
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db, VehicleServiceLog, VehicleServiceSchedule
from webapp import app

def create_tables():
    """Create the vehicle service log tables."""
    with app.app_context():
        try:
            # Create only the new tables
            db.create_all()
            print("SUCCESS: Vehicle service log tables created!")
            print("   - vehicle_service_logs")
            print("   - vehicle_service_schedules")
            return True
        except Exception as e:
            print("ERROR creating tables: {}".format(e))
            return False

if __name__ == "__main__":
    print("Creating vehicle service log tables...")
    success = create_tables()
    sys.exit(0 if success else 1)
