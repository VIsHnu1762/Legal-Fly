#!/usr/bin/env python3
"""
Quick Start Script for Legal Fly Pro
Runs the application with minimal setup
"""
import os
import sys
import subprocess

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_venv():
    """Check if virtual environment exists"""
    return os.path.exists("venv")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "streamlit", "transformers", 
                   "torch", "PyPDF2", "pdfplumber", "deep-translator", "plotly", 
                   "sqlalchemy", "sentence-transformers"], check=True)
    print("✅ Core dependencies installed")

def init_database():
    """Initialize database"""
    print("\n💾 Initializing database...")
    try:
        from database.connection import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database init warning: {e}")

def main():
    """Main entry point"""
    print("="*60)
    print("🚀 Legal Fly Pro - Quick Start")
    print("="*60)
    
    # Check Python
    check_python()
    
    # Check if first run
    if not os.path.exists("database") or not os.path.exists("utils"):
        print("\n❌ Application files not found!")
        print("Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Check venv
    if not check_venv():
        print("\n⚠️  No virtual environment found")
        print("Installing dependencies globally...")
        try:
            install_dependencies()
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            print("\nTry running: pip install -r requirements.txt")
            sys.exit(1)
    
    # Initialize database
    try:
        init_database()
    except:
        pass
    
    # Run Streamlit
    print("\n" + "="*60)
    print("🎉 Starting Legal Fly Pro...")
    print("="*60)
    print("\n📍 The app will open in your browser")
    print("   URL: http://localhost:8501")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_pro.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTry running manually: streamlit run app_pro.py")

if __name__ == "__main__":
    main()
