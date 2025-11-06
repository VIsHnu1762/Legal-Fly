# Legal Fly Pro - Next Generation AI Contract Analysis Platform

## 🚀 Version 2.0.0 - Major Upgrade

Welcome to **Legal Fly Pro**, a cutting-edge AI-powered contract analysis platform that brings professional-grade legal intelligence to everyone.

## ✨ What's New in Version 2.0

### 🎯 Core Enhancements

#### 1. **Advanced AI Classification**
- Multi-model ensemble approach
- Semantic similarity analysis
- 11 contract types (expanded from 5)
- Confidence scoring
- Party name extraction

#### 2. **Deep Risk Analysis**
- 15+ risk pattern detection (expanded from 6)
- Severity-based prioritization
- Context-aware clause extraction
- Risk distribution visualization
- Comparative risk analysis

#### 3. **Clause Intelligence**
- Automated clause extraction
- 16 clause type classifications
- Importance scoring
- Key term identification
- Obligation extraction

#### 4. **Professional Reporting**
- PDF report generation
- Executive summaries
- Visual risk dashboards
- Downloadable reports
- Custom branding

#### 5. **Data Persistence**
- SQLAlchemy database integration
- Analysis history tracking
- User management
- Audit logging

#### 6. **REST API**
- FastAPI-powered endpoints
- RESTful architecture
- Contract comparison API
- Report generation API
- Swagger documentation

#### 7. **Enhanced UI/UX**
- 6 dedicated tabs
- Interactive visualizations (Plotly)
- Risk gauge meters
- Responsive design
- Professional styling

#### 8. **Multi-language Support**
- Extended language options
- Real-time translation
- 5+ languages supported

## 🏗️ Project Structure

```
contract/
├── app_pro.py                    # Enhanced Streamlit app
├── createapp.py                  # Legacy app (V1)
├── main.py                       # CLI interface
├── requirements.txt              # All dependencies
├── .env.example                  # Environment template
│
├── api/
│   └── main.py                   # FastAPI REST API
│
├── database/
│   ├── models.py                 # SQLAlchemy models
│   └── connection.py             # Database connection
│
├── utils/
│   ├── advanced_classifier.py    # Contract classification
│   ├── advanced_risk_analyzer.py # Risk analysis engine
│   └── clause_extractor.py       # Clause extraction
│
├── reports/
│   └── pdf_generator.py          # PDF report generation
│
├── models/                       # Trained ML models
├── uploads/                      # Uploaded contracts
└── generated_reports/            # Generated PDF reports
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Tesseract OCR (for scanned PDFs)
- PostgreSQL (optional, SQLite works too)

### Step 1: Clone Repository
```bash
cd /Users/vichu/Documents/GitHub/Ai_Legal_fly/contract
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### Step 5: Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 6: Initialize Database
```bash
python -c "from database.connection import init_db; init_db()"
```

## 🚀 Usage

### Option 1: Streamlit Web App (Recommended)
```bash
streamlit run app_pro.py
```
Access at: http://localhost:8501

### Option 2: REST API
```bash
python api/main.py
```
API docs at: http://localhost:8000/docs

### Option 3: Command Line
```bash
python main.py path/to/contract.pdf
```

## 🎯 Key Features

### 1. Upload & Analyze
- Drag-and-drop PDF upload
- Automatic text extraction
- OCR for scanned documents
- Instant classification
- Quick summary metrics

### 2. Detailed Analysis
- Comprehensive risk breakdown
- Severity-based categorization
- Actionable recommendations
- Context extraction
- Risk gauge visualization

### 3. Clause Extraction
- Automatic clause identification
- Type classification
- Importance scoring
- Key term extraction
- Obligation mapping

### 4. Contract Comparison
- Side-by-side analysis
- Risk differential
- Unique risk identification
- Recommendation engine

### 5. Analysis History
- Persistent storage
- Quick access
- Search and filter
- Export capabilities

### 6. Multi-language
- 5+ language support
- Real-time translation
- Localized reports

## 🔌 API Endpoints

### POST `/api/v1/contracts/analyze`
Upload and analyze contract
```bash
curl -X POST "http://localhost:8000/api/v1/contracts/analyze" \
  -F "file=@contract.pdf"
```

### GET `/api/v1/contracts/{id}`
Get contract details

### GET `/api/v1/contracts/{id}/report`
Generate PDF report

### POST `/api/v1/contracts/compare`
Compare multiple contracts

### GET `/api/v1/contracts`
List all contracts

## 🎨 Risk Categories

| Severity | Color | Score Range | Action Required |
|----------|-------|-------------|-----------------|
| Critical | 🔴 Red | 8-10 | Legal review mandatory |
| High | 🟠 Orange | 6-8 | Careful review needed |
| Medium | 🟡 Yellow | 4-6 | Standard review |
| Low | 🟢 Green | 0-4 | Acceptable |

## 🛡️ Risk Patterns Detected

1. Unlimited Liability
2. Penalty Clauses
3. Auto-renewal Terms
4. Non-compete Restrictions
5. Termination Limitations
6. Jurisdiction Issues
7. Arbitration Clauses
8. Broad Indemnification
9. IP Assignment
10. Perpetual Confidentiality
11. Unilateral Modifications
12. Warranty Disclaimers
13. Data Rights
14. Force Majeure
15. Entire Agreement

## 📊 Supported Contract Types

1. 🏠 Lease/Rental Agreement
2. 👨‍💼 Employment Agreement
3. 📦 Vendor/Supplier Contract
4. 🔒 Non-Disclosure Agreement (NDA)
5. 🤝 Partnership Agreement
6. 💼 Service Agreement
7. 🏢 Licensing Agreement
8. ⚖️ Settlement Agreement
9. 📋 Consulting Agreement
10. 🛡️ Terms of Service
11. 📄 General Contract

## 🔒 Security Features

- File hash verification
- SQL injection protection
- Input sanitization
- Secure file storage
- Audit logging
- User authentication (API)

## 📈 Performance Optimizations

- Model caching
- Lazy loading
- Batch processing
- Database indexing
- Query optimization
- Connection pooling

## 🐛 Troubleshooting

### Issue: OCR not working
```bash
# Install Tesseract
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu
```

### Issue: spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Issue: Database connection error
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Try SQLite for development: `sqlite:///./legal_fly.db`

## 🤝 Contributing

This is a major upgrade designed to showcase professional-grade AI capabilities. Future enhancements could include:

- User authentication & authorization
- Team collaboration features
- Version control for contracts
- Integration with DocuSign
- Mobile app
- Blockchain verification

## 📜 License

This project is for educational and demonstration purposes.

## ⚖️ Disclaimer

**IMPORTANT:** This tool provides AI-powered analysis for informational purposes only. It does NOT constitute legal advice. Always consult with a qualified attorney before making legal decisions.

## 🙏 Acknowledgments

- Hugging Face Transformers
- Streamlit
- FastAPI
- ReportLab
- Sentence Transformers

## 📞 Support

For questions or issues, please refer to the documentation or create an issue in the repository.

---

**Built with ❤️ using Advanced AI Technology**

Version 2.0.0 | © 2025 Legal Fly Pro
