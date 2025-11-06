"""
FastAPI REST API for Legal Fly Pro
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
import hashlib
from datetime import datetime
import uvicorn

# Import internal modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.advanced_classifier import AdvancedContractClassifier
from utils.advanced_risk_analyzer import AdvancedRiskAnalyzer
from utils.clause_extractor import ClauseExtractor
from reader import read_pdf
from reports.pdf_generator import ReportGenerator
from database.connection import get_db, init_db
from database.models import Contract, ContractAnalysis, User
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="Legal Fly Pro API",
    description="AI-Powered Contract Analysis API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models
classifier = AdvancedContractClassifier()
risk_analyzer = AdvancedRiskAnalyzer()
clause_extractor = ClauseExtractor()

# Initialize database
init_db()


# Pydantic models for API
class ContractAnalysisResponse(BaseModel):
    contract_id: int
    contract_type: str
    confidence: float
    risk_score: float
    risk_level: str
    total_findings: int
    findings: List[Dict]
    summary: Optional[str] = None
    analysis_timestamp: str


class ContractUploadResponse(BaseModel):
    contract_id: int
    message: str
    file_name: str
    contract_type: str
    analysis: ContractAnalysisResponse


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: str


# API Endpoints

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/contracts/analyze", response_model=ContractUploadResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from auth token
):
    """
    Upload and analyze a contract
    
    - **file**: PDF contract file
    - Returns: Complete contract analysis
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Save uploaded file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Extract text
        contract_text = read_pdf(file_path)
        
        if not contract_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )
        
        # Classify contract
        classification = classifier.classify(contract_text)
        
        # Analyze risks
        risk_analysis = risk_analyzer.analyze(contract_text)
        
        # Store in database
        contract = Contract(
            user_id=user_id,
            title=file.filename,
            contract_type=classification['contract_type'],
            file_name=file.filename,
            file_path=file_path,
            file_hash=file_hash,
            text_content=contract_text[:10000],  # Store first 10k chars
            page_count=contract_text.count("[Page"),
            word_count=len(contract_text.split()),
            uploaded_at=datetime.utcnow()
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        
        # Store analysis
        analysis = ContractAnalysis(
            contract_id=contract.id,
            user_id=user_id,
            risk_score=risk_analysis['risk_score'],
            risk_level=risk_analysis['risk_level'],
            risk_factors=risk_analysis['findings'],
            summary=risk_analyzer.generate_risk_summary(risk_analysis),
            model_version="2.0.0",
            created_at=datetime.utcnow()
        )
        db.add(analysis)
        db.commit()
        
        # Prepare response
        response = ContractUploadResponse(
            contract_id=contract.id,
            message="Contract analyzed successfully",
            file_name=file.filename,
            contract_type=classification['contract_type'],
            analysis=ContractAnalysisResponse(
                contract_id=contract.id,
                contract_type=classification['contract_type'],
                confidence=classification['confidence'],
                risk_score=risk_analysis['risk_score'],
                risk_level=risk_analysis['risk_level'],
                total_findings=risk_analysis['total_findings'],
                findings=risk_analysis['findings'],
                summary=risk_analyzer.generate_risk_summary(risk_analysis),
                analysis_timestamp=risk_analysis['analysis_timestamp']
            )
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing contract: {str(e)}"
        )


@app.get("/api/v1/contracts/{contract_id}")
async def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Get contract details"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get latest analysis
    analysis = db.query(ContractAnalysis)\
        .filter(ContractAnalysis.contract_id == contract_id)\
        .order_by(ContractAnalysis.created_at.desc())\
        .first()
    
    return {
        "contract": {
            "id": contract.id,
            "title": contract.title,
            "type": contract.contract_type,
            "uploaded_at": contract.uploaded_at.isoformat()
        },
        "analysis": {
            "risk_score": analysis.risk_score if analysis else None,
            "risk_level": analysis.risk_level if analysis else None,
            "summary": analysis.summary if analysis else None
        } if analysis else None
    }


@app.get("/api/v1/contracts/{contract_id}/report")
async def generate_report(
    contract_id: int,
    db: Session = Depends(get_db)
):
    """Generate PDF report for contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    analysis = db.query(ContractAnalysis)\
        .filter(ContractAnalysis.contract_id == contract_id)\
        .order_by(ContractAnalysis.created_at.desc())\
        .first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    # Generate report
    report_dir = "generated_reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_path = os.path.join(
        report_dir,
        f"contract_{contract_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    
    generator = ReportGenerator(report_path)
    generator.add_cover_page(contract.title, contract.contract_type)
    generator.add_executive_summary(
        analysis.risk_score,
        analysis.risk_level,
        len(analysis.risk_factors)
    )
    generator.add_risk_findings(analysis.risk_factors)
    generator.add_footer_note()
    generator.generate()
    
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=f"contract_report_{contract_id}.pdf"
    )


@app.post("/api/v1/contracts/compare")
async def compare_contracts(
    contract_ids: List[int],
    db: Session = Depends(get_db)
):
    """Compare multiple contracts"""
    if len(contract_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 contracts required for comparison"
        )
    
    contracts = db.query(Contract).filter(Contract.id.in_(contract_ids)).all()
    
    if len(contracts) != len(contract_ids):
        raise HTTPException(
            status_code=404,
            detail="One or more contracts not found"
        )
    
    # Compare first two contracts
    comparison = risk_analyzer.compare_contracts(
        contracts[0].text_content,
        contracts[1].text_content
    )
    
    return {
        "comparison": comparison,
        "contracts": [
            {"id": c.id, "title": c.title, "type": c.contract_type}
            for c in contracts
        ]
    }


@app.get("/api/v1/contracts")
async def list_contracts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from auth token
):
    """List all contracts for user"""
    contracts = db.query(Contract)\
        .filter(Contract.user_id == user_id)\
        .order_by(Contract.uploaded_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "contracts": [
            {
                "id": c.id,
                "title": c.title,
                "type": c.contract_type,
                "uploaded_at": c.uploaded_at.isoformat()
            }
            for c in contracts
        ],
        "total": db.query(Contract).filter(Contract.user_id == user_id).count()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
