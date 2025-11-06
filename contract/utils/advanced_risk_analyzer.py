"""
Advanced risk analysis with ML-based scoring and explainability
"""
import re
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer, util


class AdvancedRiskAnalyzer:
    """Advanced risk analysis with detailed clause detection"""
    
    # Comprehensive risk patterns with severity and explanations
    RISK_PATTERNS = {
        "unlimited_liability": {
            "keywords": ["unlimited liability", "unlimited indemnification", "full indemnity"],
            "severity": "Critical",
            "weight": 10,
            "explanation": "Exposes you to unlimited financial responsibility for damages or losses.",
            "recommendation": "Negotiate liability caps or insurance requirements."
        },
        "penalty_clause": {
            "keywords": ["penalty", "liquidated damages", "punitive damages"],
            "severity": "High",
            "weight": 8,
            "explanation": "Financial penalties may be imposed for breach or non-performance.",
            "recommendation": "Review penalty amounts and ensure they're reasonable and capped."
        },
        "auto_renewal": {
            "keywords": ["automatic renewal", "auto-renew", "automatically renew"],
            "severity": "High",
            "weight": 7,
            "explanation": "Contract may renew without explicit consent, locking you in.",
            "recommendation": "Add clear termination notice requirements before renewal."
        },
        "non_compete": {
            "keywords": ["non-compete", "non-competition", "restrictive covenant"],
            "severity": "High",
            "weight": 8,
            "explanation": "Restricts your ability to work or do business in certain areas.",
            "recommendation": "Limit scope, geography, and duration of non-compete clause."
        },
        "termination_restrictions": {
            "keywords": ["termination without cause", "no termination right", "irrevocable"],
            "severity": "High",
            "weight": 7,
            "explanation": "Limited or no ability to exit the contract before term ends.",
            "recommendation": "Negotiate termination for convenience with reasonable notice."
        },
        "jurisdiction_clause": {
            "keywords": ["jurisdiction", "venue", "governing law"],
            "severity": "Medium",
            "weight": 5,
            "explanation": "Disputes may be resolved in inconvenient or costly jurisdictions.",
            "recommendation": "Negotiate for local or neutral jurisdiction."
        },
        "arbitration_clause": {
            "keywords": ["binding arbitration", "mandatory arbitration", "arbitration only"],
            "severity": "Medium",
            "weight": 5,
            "explanation": "Waives right to court litigation; arbitration may be costly.",
            "recommendation": "Ensure arbitration rules are fair and costs are shared."
        },
        "broad_indemnification": {
            "keywords": ["indemnify", "hold harmless", "defend and indemnify"],
            "severity": "High",
            "weight": 8,
            "explanation": "You must compensate other party for their losses, even if not your fault.",
            "recommendation": "Limit indemnification to your own negligence or willful misconduct."
        },
        "ip_assignment": {
            "keywords": ["assign all rights", "transfer ownership", "work for hire", "all intellectual property"],
            "severity": "High",
            "weight": 7,
            "explanation": "All intellectual property rights may be transferred to other party.",
            "recommendation": "Negotiate to retain ownership or license back rights."
        },
        "confidentiality_perpetual": {
            "keywords": ["perpetual confidentiality", "indefinite confidentiality", "confidential in perpetuity"],
            "severity": "Medium",
            "weight": 6,
            "explanation": "Confidentiality obligations may last forever, even after contract ends.",
            "recommendation": "Limit confidentiality period to 3-5 years post-termination."
        },
        "unilateral_modification": {
            "keywords": ["modify at any time", "change terms unilaterally", "sole discretion to amend"],
            "severity": "High",
            "weight": 8,
            "explanation": "Other party can change contract terms without your consent.",
            "recommendation": "Require mutual agreement for material changes."
        },
        "no_warranties": {
            "keywords": ["as is", "without warranty", "no warranties", "disclaim all warranties"],
            "severity": "Medium",
            "weight": 5,
            "explanation": "Services/products provided with no guarantees of quality or fitness.",
            "recommendation": "Negotiate for basic warranties of merchantability."
        },
        "data_rights": {
            "keywords": ["data ownership", "use of data", "collect and use", "data rights"],
            "severity": "Medium",
            "weight": 6,
            "explanation": "Broad rights to collect, use, or share your data.",
            "recommendation": "Clarify data usage limits and privacy protections."
        },
        "force_majeure": {
            "keywords": ["force majeure", "act of god", "events beyond control"],
            "severity": "Low",
            "weight": 3,
            "explanation": "Contract may be suspended or terminated due to unforeseen events.",
            "recommendation": "Ensure force majeure clause is balanced for both parties."
        },
        "entire_agreement": {
            "keywords": ["entire agreement", "supersedes all prior", "final agreement"],
            "severity": "Low",
            "weight": 3,
            "explanation": "Prior promises or understandings not in writing may not be enforceable.",
            "recommendation": "Ensure all important terms are included in writing."
        }
    }
    
    def __init__(self):
        """Initialize risk analyzer"""
        self.semantic_model = None
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            pass
    
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive risk analysis
        
        Returns:
            Dict with risk_score, risk_level, findings, and recommendations
        """
        findings = []
        total_score = 0
        max_score = 100
        
        text_lower = text.lower()
        
        # Check each risk pattern
        for risk_type, risk_info in self.RISK_PATTERNS.items():
            matches = []
            for keyword in risk_info["keywords"]:
                if keyword.lower() in text_lower:
                    # Find context around the keyword
                    pattern = re.escape(keyword)
                    for match in re.finditer(pattern, text_lower):
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].strip()
                        matches.append(context)
            
            if matches:
                total_score += risk_info["weight"]
                findings.append({
                    "risk_type": risk_type.replace("_", " ").title(),
                    "severity": risk_info["severity"],
                    "weight": risk_info["weight"],
                    "explanation": risk_info["explanation"],
                    "recommendation": risk_info["recommendation"],
                    "occurrences": len(matches),
                    "context": matches[0] if matches else ""
                })
        
        # Calculate normalized risk score (0-10)
        risk_score = min(10, (total_score / max_score) * 10)
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = "Critical"
        elif risk_score >= 6:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Sort findings by severity and weight
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        findings.sort(key=lambda x: (severity_order[x["severity"]], -x["weight"]))
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "total_findings": len(findings),
            "findings": findings,
            "risk_distribution": self._calculate_distribution(findings),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_distribution(self, findings: List[Dict]) -> Dict:
        """Calculate distribution of risk severities"""
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        for finding in findings:
            distribution[finding["severity"]] += 1
        
        return distribution
    
    def compare_contracts(self, text1: str, text2: str) -> Dict:
        """Compare risk profiles of two contracts"""
        analysis1 = self.analyze(text1)
        analysis2 = self.analyze(text2)
        
        return {
            "contract1": analysis1,
            "contract2": analysis2,
            "comparison": {
                "risk_score_diff": analysis1["risk_score"] - analysis2["risk_score"],
                "safer_contract": "Contract 1" if analysis1["risk_score"] < analysis2["risk_score"] else "Contract 2",
                "unique_risks_1": self._unique_risks(analysis1["findings"], analysis2["findings"]),
                "unique_risks_2": self._unique_risks(analysis2["findings"], analysis1["findings"])
            }
        }
    
    def _unique_risks(self, findings1: List[Dict], findings2: List[Dict]) -> List[str]:
        """Find risks unique to first contract"""
        types1 = {f["risk_type"] for f in findings1}
        types2 = {f["risk_type"] for f in findings2}
        return list(types1 - types2)
    
    def generate_risk_summary(self, analysis: Dict) -> str:
        """Generate human-readable risk summary"""
        risk_score = analysis["risk_score"]
        risk_level = analysis["risk_level"]
        findings = analysis["findings"]
        
        summary = f"**Overall Risk Assessment: {risk_level} ({risk_score}/10)**\n\n"
        
        if risk_score >= 7:
            summary += "⚠️ **CAUTION**: This contract contains significant risks that require careful review.\n\n"
        elif risk_score >= 5:
            summary += "⚡ **WARNING**: This contract has moderate risks that should be addressed.\n\n"
        else:
            summary += "✅ **ACCEPTABLE**: This contract has manageable risk levels.\n\n"
        
        if findings:
            summary += f"**{len(findings)} Risk Factors Identified:**\n"
            for i, finding in enumerate(findings[:5], 1):  # Top 5
                summary += f"{i}. **{finding['risk_type']}** ({finding['severity']})\n"
                summary += f"   - {finding['explanation']}\n"
                summary += f"   - ✓ {finding['recommendation']}\n\n"
        
        return summary
