"""
Quick test script to verify Legal Fly Pro installation
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    modules = [
        "streamlit",
        "transformers",
        "torch",
        "sentence_transformers",
        "PyPDF2",
        "pdfplumber",
        "sqlalchemy",
        "fastapi",
        "reportlab",
        "plotly",
        "deep_translator"
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - NOT FOUND")
            failed.append(module)
    
    return len(failed) == 0, failed


def test_database():
    """Test database connection"""
    print("\n🗄️  Testing database...")
    try:
        from database.connection import init_db, get_db_session
        init_db()
        db = get_db_session()
        db.close()
        print("  ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False


def test_models():
    """Test AI model initialization"""
    print("\n🤖 Testing AI models...")
    try:
        from utils.advanced_classifier import AdvancedContractClassifier
        from utils.advanced_risk_analyzer import AdvancedRiskAnalyzer
        
        classifier = AdvancedContractClassifier()
        print("  ✅ Classifier initialized")
        
        analyzer = AdvancedRiskAnalyzer()
        print("  ✅ Risk analyzer initialized")
        
        return True
    except Exception as e:
        print(f"  ❌ Model error: {e}")
        return False


def test_directories():
    """Test required directories exist"""
    print("\n📁 Testing directories...")
    
    dirs = ["uploads", "generated_reports", "models", "database", "utils", "api", "reports"]
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("="*50)
    print("Legal Fly Pro - Installation Test")
    print("Version 2.0.0")
    print("="*50)
    
    imports_ok, failed_modules = test_imports()
    db_ok = test_database()
    models_ok = test_models()
    dirs_ok = test_directories()
    
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    
    if imports_ok and db_ok and models_ok and dirs_ok:
        print("✅ All tests passed! Installation successful.")
        print("\nYou can now run:")
        print("  - streamlit run app_pro.py")
        print("  - python api/main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
        if not imports_ok:
            print(f"\nMissing modules: {', '.join(failed_modules)}")
            print("Run: pip install -r requirements.txt")
        
        if not dirs_ok:
            print("\nRun setup.sh to create required directories")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
