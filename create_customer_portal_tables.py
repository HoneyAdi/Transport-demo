"""
Create customer portal enhancement tables directly in the database.
Run this script to create the missing tables.
"""
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db, CustomerNotification, CustomerDocument
from webapp import app

def create_tables():
    """Create customer portal enhancement tables."""
    with app.app_context():
        try:
            # Create only the new tables
            db.create_all()
            print("SUCCESS: Customer portal enhancement tables created!")
            print("   - customer_notifications")
            print("   - customer_documents")
            return True
        except Exception as e:
            print("ERROR creating tables: {}".format(e))
            return False

if __name__ == "__main__":
    print("Creating customer portal enhancement tables...")
    success = create_tables()
    sys.exit(0 if success else 1)
