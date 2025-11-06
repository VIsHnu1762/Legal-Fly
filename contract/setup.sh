#!/bin/bash

# Legal Fly Pro - Setup Script
# Version 2.0.0

echo "=========================================="
echo "Legal Fly Pro - Setup Script"
echo "Version 2.0.0"
echo "=========================================="

# Check Python version
echo -e "\n✓ Checking Python version..."
python3 --version

# Create virtual environment
echo -e "\n✓ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo -e "\n✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "\n✓ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo -e "\n✓ Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo -e "\n✓ Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n✓ Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create required directories
echo -e "\n✓ Creating directories..."
mkdir -p uploads
mkdir -p generated_reports
mkdir -p models

# Initialize database
echo -e "\n✓ Initializing database..."
python -c "from database.connection import init_db; init_db(); print('Database initialized successfully!')"

echo -e "\n=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo -e "\nTo start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run Streamlit app: streamlit run app_pro.py"
echo "  3. Or run API: python api/main.py"
echo -e "\n=========================================="
