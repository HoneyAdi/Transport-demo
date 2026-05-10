"""
Fix database schema issues for customer portal enhancements.
Run this script to add missing columns to vendors table.
"""
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db
from webapp import app
from sqlalchemy import text

def fix_schema():
    """Add missing columns to vendors table"""
    with app.app_context():
        try:
            # Add missing customer classification columns to vendors table
            sql_statements = [
                # Customer classification fields
                text("ALTER TABLE vendors ADD COLUMN customer_type VARCHAR(50) DEFAULT 'regular'"),
                text("ALTER TABLE vendors ADD COLUMN customer_tier VARCHAR(20) DEFAULT 'bronze'"), 
                text("ALTER TABLE vendors ADD COLUMN customer_segment VARCHAR(100)"),
                text("ALTER TABLE vendors ADD COLUMN customer_lifecycle_status VARCHAR(20) DEFAULT 'active'"),
                text("ALTER TABLE vendors ADD COLUMN classification_notes TEXT"),
                text("ALTER TABLE vendors ADD COLUMN classification_date DATE DEFAULT (CURRENT_DATE)"),
                text("ALTER TABLE vendors ADD COLUMN classified_by INT")
            ]
            
            for sql in sql_statements:
                try:
                    db.session.execute(sql)
                    print(f"SUCCESS: {sql}")
                except Exception as e:
                    if "Duplicate column name" not in str(e):
                        print(f"ERROR: {sql} - {e}")
            
            db.session.commit()
            print("Schema fix completed successfully!")
            return True
            
        except Exception as e:
            print(f"ERROR fixing schema: {e}")
            return False

if __name__ == "__main__":
    print("Fixing customer portal schema...")
    success = fix_schema()
    sys.exit(0 if success else 1)
