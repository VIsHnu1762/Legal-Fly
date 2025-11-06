"""
Database initialization script
Run this to set up the database for Legal Fly Pro
"""
from database.connection import init_db
from database.models import Base
import os

def main():
    print("="*60)
    print("Legal Fly Pro - Database Initialization")
    print("="*60)
    
    # Create uploads and reports directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated_reports", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    print("\n📁 Directories created:")
    print("  ✅ uploads/")
    print("  ✅ generated_reports/")
    print("  ✅ models/")
    
    # Initialize database
    print("\n💾 Initializing database...")
    try:
        init_db()
        print("  ✅ Database tables created successfully!")
        print("\n🎉 Setup complete!")
        print("\nYou can now run:")
        print("  streamlit run app_pro.py")
        print("  or")
        print("  python api/main.py")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print("\nTrying with SQLite fallback...")
        os.environ["DATABASE_URL"] = "sqlite:///./legal_fly.db"
        init_db()
        print("  ✅ SQLite database created!")
        print("\n⚠️  Using SQLite. For production, configure PostgreSQL in .env")

if __name__ == "__main__":
    main()
