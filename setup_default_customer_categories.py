"""
Setup default customer categories for classification system.
Run this script to create default categories.
"""
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db, CustomerCategory
from webapp import app

def setup_default_categories():
    """Create default customer categories"""
    default_categories = [
        {
            'category_name': 'Regular Customers',
            'category_code': 'regular',
            'description': 'Standard transport customers with regular service requirements',
            'min_credit_limit': 50000,
            'max_credit_limit': 200000,
            'default_payment_terms': 'Net 30',
            'service_priority': 'medium',
            'sort_order': 1
        },
        {
            'category_name': 'Premium Customers',
            'category_code': 'premium',
            'description': 'High-value customers requiring priority service',
            'min_credit_limit': 100000,
            'max_credit_limit': 1000000,
            'default_payment_terms': 'Net 15',
            'service_priority': 'high',
            'sort_order': 2
        },
        {
            'category_name': 'VIP Customers',
            'category_code': 'vip',
            'description': 'Top-tier customers with white-glove service',
            'min_credit_limit': 500000,
            'max_credit_limit': 5000000,
            'default_payment_terms': 'Net 15',
            'service_priority': 'urgent',
            'sort_order': 3
        }
    ]
    
    with app.app_context():
        try:
            # Check if categories already exist
            existing_count = CustomerCategory.query.count()
            if existing_count == 0:
                for cat_data in default_categories:
                    category = CustomerCategory(
                        tenant_id=1,  # Default tenant
                        **cat_data
                    )
                    db.session.add(category)
                
                db.session.commit()
                print("SUCCESS: Default customer categories created!")
                for cat in default_categories:
                    print(f"   - {cat['category_name']} ({cat['category_code']})")
            else:
                print(f"INFO: {existing_count} categories already exist. Skipping setup.")
            return True
        except Exception as e:
            print(f"ERROR setting up categories: {e}")
            return False

if __name__ == "__main__":
    print("Setting up default customer categories...")
    success = setup_default_categories()
    sys.exit(0 if success else 1)
