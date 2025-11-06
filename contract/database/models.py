"""
Database models for Legal Fly Pro
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    contracts = relationship("Contract", back_populates="user")
    analyses = relationship("ContractAnalysis", back_populates="user")


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    contract_type = Column(String(100))
    file_name = Column(String(500))
    file_path = Column(String(1000))
    file_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash
    text_content = Column(Text)
    page_count = Column(Integer)
    word_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="contracts")
    analyses = relationship("ContractAnalysis", back_populates="contract", cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")


class ContractAnalysis(Base):
    __tablename__ = "contract_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Risk Analysis
    risk_score = Column(Float)
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    risk_factors = Column(JSON)  # List of risk factors
    
    # Summary
    summary = Column(Text)
    key_points = Column(JSON)  # List of key points
    
    # Compliance
    compliance_issues = Column(JSON)
    jurisdiction = Column(String(100))
    
    # Metadata
    analysis_duration = Column(Float)  # seconds
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="analyses")
    user = relationship("User", back_populates="analyses")


class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    clause_type = Column(String(100))  # e.g., "termination", "payment", "liability"
    title = Column(String(500))
    content = Column(Text)
    page_number = Column(Integer)
    risk_level = Column(String(20))
    importance_score = Column(Float)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="clauses")


class ComparisonSession(Base):
    __tablename__ = "comparison_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_name = Column(String(500))
    contract_ids = Column(JSON)  # List of contract IDs being compared
    comparison_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # e.g., "upload", "analyze", "export"
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
