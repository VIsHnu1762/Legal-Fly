"""
Legal Fly Pro - Next Generation Contract Analysis Platform
Version 2.0.0
"""
import streamlit as st
import PyPDF2
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import hashlib
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.advanced_classifier import AdvancedContractClassifier
from utils.advanced_risk_analyzer import AdvancedRiskAnalyzer
from utils.clause_extractor import ClauseExtractor
from reports.pdf_generator import ReportGenerator
from database.connection import get_db_session, init_db
from database.models import Contract, ContractAnalysis
from deep_translator import GoogleTranslator

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Legal Fly Pro - AI Contract Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark Mode
st.markdown("""
<style>
    /* Main app background - Dark */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    
    /* Content area */
    .main .block-container {
        background: rgba(26, 32, 44, 0.95);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Override all text colors to white/light */
    .main * {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Risk cards - Dark theme */
    .risk-critical {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        padding: 1rem;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.3);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .risk-high {
        background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%);
        padding: 1rem;
        border-left: 4px solid #f97316;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(249, 115, 22, 0.3);
        border: 1px solid rgba(249, 115, 22, 0.3);
    }
    .risk-medium {
        background: linear-gradient(135deg, #713f12 0%, #854d0e 100%);
        padding: 1rem;
        border-left: 4px solid #facc15;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(250, 204, 21, 0.3);
        border: 1px solid rgba(250, 204, 21, 0.3);
    }
    .risk-low {
        background: linear-gradient(135deg, #14532d 0%, #166534 100%);
        padding: 1rem;
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(34, 197, 94, 0.3);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    /* Metric cards - Dark */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Clause cards - Dark */
    .clause-card {
        background: linear-gradient(135deg, #1e293b 0%, #2d3748 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .clause-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Buttons - Dark */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tabs - Dark */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 41, 59, 0.8);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        background: transparent;
        font-weight: 600;
        color: #94a3b8 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Input fields - Dark */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* File uploader - Dark */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 12px;
        padding: 2rem;
    }
    
    /* Metrics - Dark */
    [data-testid="stMetricValue"] {
        color: #667eea !important;
        font-weight: bold;
    }
    
    /* Expanders - Dark */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #e2e8f0 !important;
    }
    
    /* Info/Success/Warning boxes - Dark */
    .stAlert {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'contract_text' not in st.session_state:
    st.session_state.contract_text = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'contract_history' not in st.session_state:
    st.session_state.contract_history = []

# Initialize AI models
@st.cache_resource
def load_models():
    """Load AI models (cached)"""
    classifier = AdvancedContractClassifier()
    risk_analyzer = AdvancedRiskAnalyzer()
    clause_extractor = ClauseExtractor()
    return classifier, risk_analyzer, clause_extractor

classifier, risk_analyzer, clause_extractor = load_models()

# Helper functions
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF with OCR fallback"""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.warning(f"PyPDF2 extraction failed: {e}")
    
    if not text.strip():
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            st.warning(f"pdfplumber extraction failed: {e}")
    
    if not text.strip():
        try:
            images = convert_from_bytes(uploaded_file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except Exception as e:
            st.error(f"OCR extraction failed: {e}")
    
    return text

def translate_text(text, target_lang="hi"):
    """Translate text to target language"""
    try:
        translator = GoogleTranslator(source="en", target=target_lang)
        # Split into chunks for translation
        max_length = 5000
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        translated = ""
        for chunk in chunks[:3]:  # Limit to avoid quota
            translated += translator.translate(chunk) + " "
        return translated
    except Exception as e:
        return f"Translation error: {e}"

def create_risk_gauge(risk_score):
    """Create risk score gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score"},
        delta={'reference': 5},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "#4caf50"},
                {'range': [3, 6], 'color': "#fbc02d"},
                {'range': [6, 8], 'color': "#f57c00"},
                {'range': [8, 10], 'color': "#d32f2f"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_risk_distribution_chart(distribution):
    """Create risk distribution pie chart"""
    labels = list(distribution.keys())
    values = list(distribution.values())
    colors = {
        "Critical": "#d32f2f",
        "High": "#f57c00",
        "Medium": "#fbc02d",
        "Low": "#388e3c"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=[colors[l] for l in labels]),
        hole=0.4
    )])
    fig.update_layout(title="Risk Distribution", height=300)
    return fig

# Main App
st.markdown('<div class="main-header">⚖️ Legal Fly Pro</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Next-Generation AI-Powered Contract Analysis Platform</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/2c5aa0/ffffff?text=Legal+Fly+Pro", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Advanced AI Classification
    - 🔍 Deep Risk Analysis
    - 📊 Clause Extraction
    - 📈 Visual Analytics
    - 🌍 Multi-language Support
    - 📄 Professional Reports
    - 🔄 Contract Comparison
    - 💾 Analysis History
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("Version 2.0.0")
    st.markdown("Powered by Advanced AI Models")

# Main content
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📤 Upload & Analyze",
    "📊 Detailed Analysis", 
    "📋 Clause Extraction",
    "🔄 Compare Contracts",
    "📜 History",
    "🌍 Multi-language"
])

# Tab 1: Upload & Analyze
with tab1:
    st.header("Upload Contract for Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a contract (PDF)",
            type=["pdf"],
            help="Upload your contract in PDF format for AI-powered analysis"
        )
    
    with col2:
        st.info("📝 **Supported Formats**\n\n✓ PDF Documents\n✓ Scanned PDFs (OCR)\n✓ Multi-page contracts")
    
    if uploaded_file:
        with st.spinner("🔍 Extracting and analyzing contract..."):
            # Extract text
            contract_text = extract_text_from_pdf(uploaded_file)
            st.session_state.contract_text = contract_text
            
            if contract_text.strip():
                # Calculate file hash
                file_hash = hashlib.md5(contract_text.encode()).hexdigest()
                
                # Classification
                classification = classifier.classify(contract_text)
                
                # Risk Analysis
                risk_analysis = risk_analyzer.analyze(contract_text)
                
                # Store results
                st.session_state.classification = classification
                st.session_state.risk_analysis = risk_analysis
                st.session_state.analysis_complete = True
                
                # Save to history
                st.session_state.contract_history.append({
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now(),
                    'contract_type': classification['contract_type'],
                    'risk_score': risk_analysis['risk_score'],
                    'file_hash': file_hash
                })
                
                st.success("✅ Analysis complete!")
                
                # Display summary
                st.markdown("---")
                st.subheader("📊 Quick Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Contract Type",
                        classification['contract_type'],
                        f"{classification['confidence']*100:.1f}% confidence"
                    )
                
                with col2:
                    st.metric(
                        "Risk Score",
                        f"{risk_analysis['risk_score']}/10",
                        risk_analysis['risk_level']
                    )
                
                with col3:
                    st.metric(
                        "Risk Factors",
                        risk_analysis['total_findings'],
                        "identified"
                    )
                
                with col4:
                    word_count = len(contract_text.split())
                    st.metric(
                        "Document Size",
                        f"{word_count:,}",
                        "words"
                    )
                
                # Risk gauge
                st.plotly_chart(create_risk_gauge(risk_analysis['risk_score']), use_container_width=True)
                
            else:
                st.error("❌ Could not extract text from PDF. Please try a different file.")

# Tab 2: Detailed Analysis
with tab2:
    if st.session_state.analysis_complete:
        st.header("📊 Comprehensive Risk Analysis")
        
        risk_analysis = st.session_state.risk_analysis
        classification = st.session_state.classification
        
        # Risk Overview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="risk-{risk_analysis['risk_level'].lower()}">
                <h3>Overall Risk: {risk_analysis['risk_level']}</h3>
                <p><strong>Score:</strong> {risk_analysis['risk_score']}/10</p>
                <p><strong>Total Findings:</strong> {risk_analysis['total_findings']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.plotly_chart(
                create_risk_distribution_chart(risk_analysis['risk_distribution']),
                use_container_width=True
            )
        
        # Detailed Findings
        st.markdown("---")
        st.subheader("🔍 Detailed Risk Findings")
        
        if risk_analysis['findings']:
            for i, finding in enumerate(risk_analysis['findings'], 1):
                with st.expander(
                    f"{'🔴' if finding['severity'] == 'Critical' else '🟠' if finding['severity'] == 'High' else '🟡' if finding['severity'] == 'Medium' else '🟢'} "
                    f"{i}. {finding['risk_type']} ({finding['severity']} Risk)",
                    expanded=(i <= 3)
                ):
                    st.markdown(f"**Issue:** {finding['explanation']}")
                    st.markdown(f"**Recommendation:** ✓ {finding['recommendation']}")
                    
                    if finding.get('context'):
                        st.markdown("**Context:**")
                        st.info(finding['context'][:300] + "...")
                    
                    st.markdown(f"**Occurrences:** {finding['occurrences']}")
        else:
            st.success("✅ No significant risk factors identified!")
        
        # Generate report button
        st.markdown("---")
        if st.button("📄 Generate Professional PDF Report", type="primary"):
            with st.spinner("Generating report..."):
                try:
                    report_dir = "generated_reports"
                    os.makedirs(report_dir, exist_ok=True)
                    
                    report_path = os.path.join(
                        report_dir,
                        f"contract_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    )
                    
                    generator = ReportGenerator(report_path)
                    generator.add_cover_page(
                        uploaded_file.name if uploaded_file else "Contract Analysis",
                        classification['contract_type']
                    )
                    generator.add_executive_summary(
                        risk_analysis['risk_score'],
                        risk_analysis['risk_level'],
                        risk_analysis['total_findings'],
                        classification['confidence']
                    )
                    generator.add_risk_findings(risk_analysis['findings'])
                    generator.add_footer_note()
                    generator.generate()
                    
                    with open(report_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Report",
                            f,
                            file_name=f"contract_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    st.success("✅ Report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating report: {e}")
    else:
        st.info("📤 Please upload a contract in the 'Upload & Analyze' tab first.")

# Tab 3: Clause Extraction
with tab3:
    if st.session_state.analysis_complete and st.session_state.contract_text:
        st.header("📋 Clause Analysis")
        
        with st.spinner("Extracting clauses..."):
            clauses = clause_extractor.extract_clauses(st.session_state.contract_text)
            clause_summary = clause_extractor.summarize_clauses(clauses)
            key_terms = clause_extractor.extract_key_terms(st.session_state.contract_text)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clauses", clause_summary['total_clauses'])
        with col2:
            st.metric("High Importance", len(clause_summary['high_importance']))
        with col3:
            st.metric("Total Words", f"{clause_summary['word_count']:,}")
        
        # Clause type distribution
        if clause_summary['clause_types']:
            st.subheader("📊 Clause Type Distribution")
            fig = px.bar(
                x=list(clause_summary['clause_types'].keys()),
                y=list(clause_summary['clause_types'].values()),
                labels={'x': 'Clause Type', 'y': 'Count'},
                color=list(clause_summary['clause_types'].values()),
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Key clauses
        st.subheader("🔑 Important Clauses")
        for clause in clause_summary['high_importance'][:10]:
            with st.expander(f"⭐ {clause['title']} (Importance: {clause['importance']*100:.0f}%)"):
                st.markdown(f"**Types:** {', '.join(clause['types'])}")
        
        # Key terms
        if key_terms:
            st.subheader("📖 Defined Terms")
            for term, definition in list(key_terms.items())[:10]:
                st.markdown(f"**{term}:** {definition}")
    else:
        st.info("📤 Please upload a contract in the 'Upload & Analyze' tab first.")

# Tab 4: Compare Contracts
with tab4:
    st.header("🔄 Contract Comparison")
    st.info("Upload multiple contracts to compare their risk profiles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file1 = st.file_uploader("Contract 1", type=["pdf"], key="compare1")
    
    with col2:
        file2 = st.file_uploader("Contract 2", type=["pdf"], key="compare2")
    
    if file1 and file2:
        if st.button("🔍 Compare Contracts"):
            with st.spinner("Analyzing contracts..."):
                text1 = extract_text_from_pdf(file1)
                text2 = extract_text_from_pdf(file2)
                
                comparison = risk_analyzer.compare_contracts(text1, text2)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"📄 {file1.name}")
                    st.metric("Risk Score", f"{comparison['contract1']['risk_score']}/10")
                    st.metric("Risk Level", comparison['contract1']['risk_level'])
                    st.metric("Findings", comparison['contract1']['total_findings'])
                
                with col2:
                    st.subheader(f"📄 {file2.name}")
                    st.metric("Risk Score", f"{comparison['contract2']['risk_score']}/10")
                    st.metric("Risk Level", comparison['contract2']['risk_level'])
                    st.metric("Findings", comparison['contract2']['total_findings'])
                
                st.markdown("---")
                st.subheader("📊 Comparison Results")
                st.success(f"**Safer Contract:** {comparison['comparison']['safer_contract']}")
                st.metric("Risk Score Difference", 
                         f"{abs(comparison['comparison']['risk_score_diff']):.2f}")

# Tab 5: History
with tab5:
    st.header("📜 Analysis History")
    
    if st.session_state.contract_history:
        for i, item in enumerate(reversed(st.session_state.contract_history), 1):
            with st.expander(f"{i}. {item['filename']} - {item['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Type:** {item['contract_type']}")
                with col2:
                    st.write(f"**Risk Score:** {item['risk_score']}/10")
                with col3:
                    st.write(f"**Hash:** {item['file_hash'][:16]}...")
    else:
        st.info("No analysis history yet. Upload contracts to get started!")

# Tab 6: Multi-language
with tab6:
    st.header("🌍 Multi-language Support")
    
    if st.session_state.analysis_complete:
        risk_summary = risk_analyzer.generate_risk_summary(st.session_state.risk_analysis)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🇬🇧 English")
            st.markdown(risk_summary)
        
        with col2:
            st.subheader("🇮🇳 Hindi (हिंदी)")
            lang = st.selectbox("Select Language", ["Hindi", "Spanish", "French", "German", "Chinese"])
            
            lang_codes = {
                "Hindi": "hi",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                "Chinese": "zh-CN"
            }
            
            if st.button("🔄 Translate"):
                with st.spinner(f"Translating to {lang}..."):
                    translated = translate_text(risk_summary, lang_codes[lang])
                    st.info(translated)
    else:
        st.info("📤 Please upload a contract in the 'Upload & Analyze' tab first.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>Legal Fly Pro v2.0.0</strong> | Powered by Advanced AI</p>
    <p><em>⚠️ This analysis is for informational purposes only and does not constitute legal advice.</em></p>
</div>
""", unsafe_allow_html=True)
