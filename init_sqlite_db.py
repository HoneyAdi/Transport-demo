#!/usr/bin/env python3
"""
Initialize SQLite database for the transport management system
"""

import os
from webapp import app, db

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if database file exists
        db_path = "transport.db"
        if os.path.exists(db_path):
            print(f"Database file created: {os.path.abspath(db_path)}")
        else:
            print("Warning: Database file not found after creation")

if __name__ == "__main__":
    init_database()
