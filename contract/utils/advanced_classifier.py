"""
Advanced contract classification with multiple models and ensemble approach
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Tuple
import re


class AdvancedContractClassifier:
    """Advanced contract classifier with ensemble methods"""
    
    CONTRACT_TYPES = {
        0: "🏠 Lease/Rental Agreement",
        1: "👨‍💼 Employment Agreement",
        2: "📦 Vendor/Supplier Contract",
        3: "🔒 Non-Disclosure Agreement (NDA)",
        4: "🤝 Partnership Agreement",
        5: "💼 Service Agreement",
        6: "🏢 Licensing Agreement",
        7: "⚖️ Settlement Agreement",
        8: "📋 Consulting Agreement",
        9: "🛡️ Terms of Service",
        10: "📄 General Contract"
    }
    
    # Enhanced keyword patterns
    KEYWORD_PATTERNS = {
        0: ["lease", "landlord", "tenant", "rent", "premises", "property", "occupancy"],
        1: ["employee", "employer", "employment", "salary", "wages", "termination", "position", "duties"],
        2: ["vendor", "supplier", "purchase order", "goods", "delivery", "procurement"],
        3: ["confidential", "non-disclosure", "proprietary", "trade secret", "nda"],
        4: ["partner", "partnership", "joint venture", "profit sharing", "contribution"],
        5: ["service", "provider", "client", "deliverables", "scope of work"],
        6: ["license", "licensee", "licensor", "intellectual property", "royalty"],
        7: ["settlement", "dispute", "claims", "release", "waiver"],
        8: ["consultant", "consulting", "independent contractor", "professional services"],
        9: ["terms of service", "terms and conditions", "user agreement", "acceptable use"],
        10: ["agreement", "contract", "party", "obligation"]
    }
    
    def __init__(self, model_path: str = None):
        """Initialize classifier with optional custom model"""
        self.use_ml = False
        self.semantic_model = None
        
        # Try to load fine-tuned model
        if model_path:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                self.use_ml = True
            except Exception as e:
                print(f"Could not load custom model: {e}")
        
        # Load semantic similarity model
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._prepare_embeddings()
        except Exception as e:
            print(f"Could not load semantic model: {e}")
    
    def _prepare_embeddings(self):
        """Pre-compute embeddings for contract type descriptions"""
        descriptions = {
            0: "rental property lease landlord tenant housing agreement",
            1: "employment job work employee employer salary compensation",
            2: "vendor supplier purchase goods products delivery",
            3: "confidential information trade secrets non-disclosure nda",
            4: "business partnership joint venture profit sharing",
            5: "professional services client provider deliverables",
            6: "software license intellectual property rights royalties",
            7: "legal settlement dispute resolution claims",
            8: "consulting services independent contractor advisory",
            9: "website terms conditions user agreement policies",
            10: "general legal agreement contract obligations"
        }
        
        self.type_embeddings = {}
        for type_id, desc in descriptions.items():
            self.type_embeddings[type_id] = self.semantic_model.encode(desc, convert_to_tensor=True)
    
    def _keyword_score(self, text: str) -> Dict[int, float]:
        """Score contract types based on keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for type_id, keywords in self.KEYWORD_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[type_id] = score / len(keywords)  # Normalize
        
        return scores
    
    def _semantic_score(self, text: str) -> Dict[int, float]:
        """Score contract types using semantic similarity"""
        if not self.semantic_model:
            return {}
        
        # Use first 1000 words for efficiency
        text_sample = ' '.join(text.split()[:1000])
        text_embedding = self.semantic_model.encode(text_sample, convert_to_tensor=True)
        
        scores = {}
        for type_id, type_embedding in self.type_embeddings.items():
            similarity = util.cos_sim(text_embedding, type_embedding).item()
            scores[type_id] = similarity
        
        return scores
    
    def _ml_predict(self, text: str) -> Tuple[int, float]:
        """Predict using ML model"""
        if not self.use_ml:
            return None, 0.0
        
        inputs = self.tokenizer(
            text[:512],  # Limit input length
            return_tensors="pt",
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            confidence, prediction = torch.max(probs, dim=1)
        
        return prediction.item(), confidence.item()
    
    def classify(self, text: str) -> Dict:
        """
        Classify contract using ensemble of methods
        
        Returns:
            Dict with contract_type, confidence, and all_scores
        """
        keyword_scores = self._keyword_score(text)
        semantic_scores = self._semantic_score(text)
        
        # Combine scores
        ensemble_scores = {}
        for type_id in self.CONTRACT_TYPES.keys():
            scores = []
            
            if keyword_scores:
                scores.append(keyword_scores.get(type_id, 0) * 0.4)
            
            if semantic_scores:
                scores.append(semantic_scores.get(type_id, 0) * 0.6)
            
            ensemble_scores[type_id] = sum(scores)
        
        # Get ML prediction if available
        ml_pred, ml_conf = self._ml_predict(text)
        
        # Final decision
        if self.use_ml and ml_conf > 0.7:
            predicted_type = ml_pred
            confidence = ml_conf
        else:
            predicted_type = max(ensemble_scores, key=ensemble_scores.get)
            confidence = ensemble_scores[predicted_type]
        
        return {
            "contract_type": self.CONTRACT_TYPES[predicted_type],
            "type_id": predicted_type,
            "confidence": float(confidence),
            "keyword_scores": keyword_scores,
            "semantic_scores": semantic_scores,
            "ml_prediction": ml_pred if self.use_ml else None,
            "ml_confidence": float(ml_conf) if self.use_ml else None
        }
    
    def extract_contract_parties(self, text: str) -> List[str]:
        """Extract party names from contract"""
        parties = []
        
        # Pattern for "between X and Y"
        pattern1 = r"between\s+([^,\n]+?)\s+(?:and|&)\s+([^,\n]+?)(?:\.|,|\n)"
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            parties.extend([match.group(1).strip(), match.group(2).strip()])
        
        # Pattern for "Party A" and "Party B" definitions
        pattern2 = r'"([^"]+)"\s*(?:\(|referred to as)'
        matches = re.finditer(pattern2, text)
        for match in matches:
            parties.append(match.group(1).strip())
        
        return list(set(parties))[:5]  # Return unique parties, max 5
