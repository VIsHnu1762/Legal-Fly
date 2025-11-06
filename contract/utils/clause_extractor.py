"""
Advanced clause extraction and classification
"""
import re
from typing import List, Dict
import spacy
from collections import defaultdict


class ClauseExtractor:
    """Extract and classify contract clauses"""
    
    CLAUSE_TYPES = {
        "payment": ["payment", "compensation", "fees", "invoice", "cost"],
        "termination": ["termination", "cancel", "end agreement", "expiration"],
        "liability": ["liability", "indemnif", "hold harmless", "damages"],
        "confidentiality": ["confidential", "proprietary", "trade secret", "nda"],
        "intellectual_property": ["intellectual property", "copyright", "patent", "trademark", "ip rights"],
        "warranties": ["warrant", "guarantee", "representation", "assurance"],
        "dispute_resolution": ["dispute", "arbitration", "mediation", "litigation", "jurisdiction"],
        "force_majeure": ["force majeure", "act of god", "unforeseen"],
        "assignment": ["assign", "transfer", "delegate"],
        "amendment": ["amend", "modify", "change", "alter"],
        "governing_law": ["governing law", "applicable law", "governed by"],
        "notice": ["notice", "notification", "notify"],
        "entire_agreement": ["entire agreement", "complete agreement", "supersede"],
        "severability": ["severability", "severable", "invalid"],
        "non_compete": ["non-compete", "non-competition", "restrictive covenant"],
        "data_privacy": ["data", "privacy", "personal information", "gdpr", "ccpa"]
    }
    
    def __init__(self):
        """Initialize clause extractor"""
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not loaded. Some features may be limited.")
    
    def extract_clauses(self, text: str) -> List[Dict]:
        """
        Extract and classify clauses from contract text
        
        Returns:
            List of clause dictionaries
        """
        clauses = []
        
        # Split text into sections
        sections = self._split_into_sections(text)
        
        for section_num, section_text in enumerate(sections, 1):
            # Classify the section
            clause_types = self._classify_section(section_text)
            
            if clause_types:
                # Extract title
                title = self._extract_section_title(section_text)
                
                clause = {
                    "section_number": section_num,
                    "title": title,
                    "content": section_text.strip()[:500],  # First 500 chars
                    "full_content": section_text.strip(),
                    "clause_types": clause_types,
                    "word_count": len(section_text.split()),
                    "importance": self._calculate_importance(section_text, clause_types)
                }
                
                clauses.append(clause)
        
        return clauses
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split contract into logical sections"""
        # Try to split by numbered sections first
        pattern = r'\n\s*(\d+\.|\d+\)|\([a-z]\)|\([ivxl]+\))\s+'
        sections = re.split(pattern, text)
        
        # Combine section markers with their content
        combined = []
        for i in range(1, len(sections), 2):
            if i < len(sections):
                section = (sections[i-1] if i > 0 else "") + sections[i]
                if len(section.strip()) > 50:  # Minimum section length
                    combined.append(section)
        
        # If no clear sections, split by paragraphs
        if len(combined) < 3:
            combined = [p for p in text.split('\n\n') if len(p.strip()) > 100]
        
        return combined[:50]  # Limit to 50 sections
    
    def _classify_section(self, text: str) -> List[str]:
        """Classify section into clause types"""
        text_lower = text.lower()
        detected_types = []
        
        for clause_type, keywords in self.CLAUSE_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected_types.append(clause_type)
                    break
        
        return detected_types
    
    def _extract_section_title(self, text: str) -> str:
        """Extract title from section"""
        # Look for title in first line or first sentence
        lines = text.strip().split('\n')
        first_line = lines[0] if lines else ""
        
        # If first line is short and in title case or all caps, use it
        if len(first_line.split()) <= 10:
            if first_line.isupper() or first_line.istitle():
                return first_line.strip()
        
        # Otherwise, use first sentence
        sentences = re.split(r'[.!?]\s+', text)
        if sentences:
            title = sentences[0][:100]  # Max 100 chars
            return title.strip()
        
        return "Untitled Clause"
    
    def _calculate_importance(self, text: str, clause_types: List[str]) -> float:
        """Calculate importance score for clause"""
        score = 0.0
        
        # Base score on clause types
        important_types = ["liability", "termination", "payment", "intellectual_property"]
        for ct in clause_types:
            if ct in important_types:
                score += 0.3
            else:
                score += 0.1
        
        # Boost for certain keywords
        high_priority = ["shall", "must", "required", "obligation", "breach"]
        text_lower = text.lower()
        score += sum(0.05 for word in high_priority if word in text_lower)
        
        return min(1.0, score)
    
    def extract_key_terms(self, text: str) -> Dict:
        """Extract key terms and definitions"""
        terms = {}
        
        # Pattern for defined terms: "Term" means...
        pattern1 = r'"([^"]+)"\s+(?:means?|refers? to|is defined as)\s+([^.]+\.)'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()
            terms[term] = definition
        
        # Pattern for definitions section
        if "definitions" in text.lower():
            # Extract section containing definitions
            pattern2 = r'definitions.*?(?=\n\s*\d+\.|\Z)'
            match = re.search(pattern2, text, re.IGNORECASE | re.DOTALL)
            if match:
                def_section = match.group(0)
                # Extract individual terms
                term_pattern = r'([A-Z][a-zA-Z\s]+):\s+([^;]+);'
                for m in re.finditer(term_pattern, def_section):
                    terms[m.group(1).strip()] = m.group(2).strip()
        
        return terms
    
    def extract_obligations(self, text: str, party: str = "Contractor") -> List[Dict]:
        """Extract obligations for a specific party"""
        obligations = []
        
        # Patterns for obligations
        patterns = [
            rf'{party}\s+(?:shall|must|will|agrees to)\s+([^.]+\.)',
            rf'(?:The\s+)?{party}\s+is\s+(?:required|obligated)\s+to\s+([^.]+\.)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                obligation_text = match.group(1).strip()
                obligations.append({
                    "party": party,
                    "obligation": obligation_text,
                    "context": match.group(0)
                })
        
        return obligations[:20]  # Limit to top 20
    
    def summarize_clauses(self, clauses: List[Dict]) -> Dict:
        """Generate summary statistics for clauses"""
        summary = {
            "total_clauses": len(clauses),
            "clause_types": defaultdict(int),
            "high_importance": [],
            "word_count": 0
        }
        
        for clause in clauses:
            summary["word_count"] += clause["word_count"]
            
            for ct in clause["clause_types"]:
                summary["clause_types"][ct] += 1
            
            if clause["importance"] >= 0.7:
                summary["high_importance"].append({
                    "title": clause["title"],
                    "types": clause["clause_types"],
                    "importance": clause["importance"]
                })
        
        summary["clause_types"] = dict(summary["clause_types"])
        return summary
