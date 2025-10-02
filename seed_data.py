"""
Data seeding script for Streamlit Cloud deployment
This ensures the demo database is created when the app starts
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def seed_demo_data():
    """Create demo database if it doesn't exist"""
    try:
        from db.seed_demo import main as seed_main
        seed_main()
        print("✅ Demo database seeded successfully")
    except Exception as e:
        print(f"⚠️ Could not seed demo database: {e}")
        print("App will still work, but with limited demo data")

if __name__ == "__main__":
    seed_demo_data()
