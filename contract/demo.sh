#!/bin/bash
# Legal Fly Pro - Demo Script
# Shows all the new capabilities

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              🚀 LEGAL FLY PRO v2.0 - DEMO 🚀                  ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Function to show progress
show_step() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Check if we're in the right directory
if [ ! -f "app_pro.py" ]; then
    echo "❌ Error: Please run this script from the contract directory"
    exit 1
fi

show_step "STEP 1: Testing Installation"
python3 test_installation.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some tests failed. Do you want to run setup? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        show_step "Running Setup..."
        ./setup.sh
    fi
fi

show_step "STEP 2: Available Options"
echo "Choose how you want to run Legal Fly Pro:"
echo ""
echo "  1) 🎨 Streamlit Web App (Recommended for end users)"
echo "  2) 🔌 FastAPI Server (For developers/integration)"
echo "  3) 💻 Command Line (For quick analysis)"
echo "  4) 📚 View Documentation"
echo "  5) 🧪 Run Demo Analysis"
echo "  6) ❌ Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        show_step "Starting Streamlit App..."
        echo "📍 The app will open at: http://localhost:8501"
        echo "⌨️  Press Ctrl+C to stop the server"
        echo ""
        streamlit run app_pro.py
        ;;
    2)
        show_step "Starting FastAPI Server..."
        echo "📍 API will be available at: http://localhost:8000"
        echo "📚 Documentation at: http://localhost:8000/docs"
        echo "⌨️  Press Ctrl+C to stop the server"
        echo ""
        python api/main.py
        ;;
    3)
        show_step "Command Line Mode"
        if [ -f "sample.pdf" ]; then
            echo "Running analysis on sample.pdf..."
            python main.py sample.pdf
        else
            echo "❌ sample.pdf not found"
            echo "Usage: python main.py <path-to-contract.pdf>"
        fi
        ;;
    4)
        show_step "Documentation"
        echo "📚 Available Documentation:"
        echo ""
        echo "  • START_HERE.md         ← Quick overview (RECOMMENDED)"
        echo "  • SUMMARY.md            ← Complete summary"
        echo "  • README_V2.md          ← Detailed documentation"
        echo "  • WHATS_NEW.md          ← V1 vs V2 comparison"
        echo "  • UPGRADE_GUIDE.md      ← Migration guide"
        echo "  • FEATURES.md           ← Feature list"
        echo ""
        read -p "Which file would you like to view? (or press Enter to skip): " doc_file
        if [ ! -z "$doc_file" ]; then
            if [ -f "$doc_file" ]; then
                less "$doc_file"
            else
                echo "❌ File not found: $doc_file"
            fi
        fi
        ;;
    5)
        show_step "Running Demo Analysis"
        echo "This will demonstrate all capabilities..."
        echo ""
        
        if [ -f "sample.pdf" ]; then
            echo "✅ Found sample.pdf"
            echo ""
            echo "📊 Classification:"
            python -c "from reader import read_pdf; from utils.advanced_classifier import AdvancedContractClassifier; classifier = AdvancedContractClassifier(); text = read_pdf('sample.pdf'); result = classifier.classify(text); print(f\"  Type: {result['contract_type']}\"); print(f\"  Confidence: {result['confidence']*100:.1f}%\")"
            echo ""
            echo "⚠️  Risk Analysis:"
            python -c "from reader import read_pdf; from utils.advanced_risk_analyzer import AdvancedRiskAnalyzer; analyzer = AdvancedRiskAnalyzer(); text = read_pdf('sample.pdf'); analysis = analyzer.analyze(text); print(f\"  Risk Score: {analysis['risk_score']}/10\"); print(f\"  Risk Level: {analysis['risk_level']}\"); print(f\"  Findings: {analysis['total_findings']}\")"
            echo ""
            echo "✅ Demo complete! Run Streamlit for full experience."
        else
            echo "❌ sample.pdf not found. Please upload a contract PDF."
        fi
        ;;
    6)
        echo ""
        echo "👋 Goodbye! To start again, run: ./demo.sh"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              🎉 Thanks for using Legal Fly Pro! 🎉            ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
