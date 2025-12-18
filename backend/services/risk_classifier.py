"""
Risk Classifier Service

Classifies risk level of contract changes based on:
- Clause category
- Change type
- Change magnitude
- Gemini-powered explanations
"""

from typing import Dict, Optional
from models import ChangeType, RiskLevel
from services.gemini_service import GeminiService


class RiskClassifier:
    """Service for classifying risk levels of changes."""
    
    # Risk weights by category
    CATEGORY_RISK_WEIGHTS = {
        "liability": 10,
        "data_usage": 10,
        "intellectual_property": 8,
        "termination": 7,
        "payment": 7,
        "jurisdiction": 6,
        "service_level": 5,
        "marketing": 3,
        "other": 2
    }
    
    # Risk weights by change type
    CHANGE_TYPE_WEIGHTS = {
        ChangeType.REMOVED: 1.5,
        ChangeType.REWRITTEN: 1.3,
        ChangeType.MODIFIED: 1.0,
        ChangeType.ADDED: 0.8
    }
    
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        """
        Initialize risk classifier.
        
        Args:
            gemini_service: Optional Gemini service for explanations
        """
        self.gemini_service = gemini_service
    
    async def classify_risk(
        self,
        change: Dict[str, any],
        clause: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Classify risk level of a change.
        
        Args:
            change: Change information
            clause: Clause information
            
        Returns:
            Risk classification with score and explanation
        """
        # Calculate base risk score
        risk_score = self._calculate_risk_score(
            category=clause.get("category"),
            change_type=change["change_type"],
            similarity=change.get("similarity_score", 0.0)
        )
        
        # Determine risk level
        risk_level = self._score_to_level(risk_score)
        
        # Generate explanation
        explanation = await self._generate_explanation(
            change=change,
            clause=clause,
            risk_level=risk_level
        )
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "explanation": explanation
        }
    
    def _calculate_risk_score(
        self,
        category: Optional[str],
        change_type: ChangeType,
        similarity: float
    ) -> int:
        """
        Calculate numerical risk score (0-100).
        
        Args:
            category: Clause category
            change_type: Type of change
            similarity: Similarity score (0-1)
            
        Returns:
            Risk score
        """
        # Base score from category
        category_weight = self.CATEGORY_RISK_WEIGHTS.get(category, 2)
        
        # Multiplier from change type
        change_weight = self.CHANGE_TYPE_WEIGHTS.get(change_type, 1.0)
        
        # Magnitude factor (lower similarity = higher risk)
        magnitude_factor = 1.0 - similarity
        
        # Calculate score
        score = category_weight * change_weight * (1 + magnitude_factor * 2)
        
        # Normalize to 0-100
        return min(100, int(score * 3))
    
    @staticmethod
    def _score_to_level(score: int) -> RiskLevel:
        """
        Convert risk score to risk level.
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            Risk level enum
        """
        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _generate_explanation(
        self,
        change: Dict[str, any],
        clause: Dict[str, any],
        risk_level: RiskLevel
    ) -> str:
        """
        Generate explanation for the risk classification.
        
        Args:
            change: Change information
            clause: Clause information
            risk_level: Classified risk level
            
        Returns:
            Explanation text
        """
        # Try Gemini-powered explanation first
        if self.gemini_service:
            try:
                explanation = await self.gemini_service.explain_risk(
                    clause_text=clause.get("text", ""),
                    category=clause.get("category", "other"),
                    change_description=change.get("summary", "")
                )
                
                if explanation:
                    return explanation
            except Exception as e:
                print(f"Error generating Gemini explanation: {e}")
        
        # Fallback to rule-based explanation
        return self._generate_rule_based_explanation(
            change_type=change["change_type"],
            category=clause.get("category"),
            risk_level=risk_level
        )
    
    @staticmethod
    def _generate_rule_based_explanation(
        change_type: ChangeType,
        category: Optional[str],
        risk_level: RiskLevel
    ) -> str:
        """
        Generate rule-based explanation.
        
        Args:
            change_type: Type of change
            category: Clause category
            risk_level: Risk level
            
        Returns:
            Explanation text
        """
        category_impacts = {
            "liability": "This affects your legal liability and potential damages.",
            "data_usage": "This impacts how your data is collected, used, or shared.",
            "termination": "This changes the terms for ending the contract.",
            "jurisdiction": "This affects which laws apply and where disputes are resolved.",
            "payment": "This impacts pricing, billing, or refund terms.",
            "intellectual_property": "This affects ownership and usage rights.",
            "service_level": "This changes service guarantees and uptime commitments.",
            "marketing": "This affects marketing communications and promotional usage.",
        }
        
        change_descriptions = {
            ChangeType.ADDED: "A new clause was added",
            ChangeType.REMOVED: "An existing clause was removed",
            ChangeType.MODIFIED: "A clause was modified",
            ChangeType.REWRITTEN: "A clause was significantly rewritten"
        }
        
        impact = category_impacts.get(category, "This may affect your contract terms.")
        change_desc = change_descriptions.get(change_type, "A change was detected")
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            urgency = "Review this change carefully before accepting."
        elif risk_level == RiskLevel.MEDIUM:
            urgency = "Consider reviewing this change."
        else:
            urgency = "This is a minor change."
        
        return f"{change_desc} in the {category or 'contract'} section. {impact} {urgency}"
    
    @staticmethod
    def should_alert(risk_level: RiskLevel, threshold: RiskLevel = RiskLevel.HIGH) -> bool:
        """
        Determine if an alert should be sent based on risk level.
        
        Args:
            risk_level: Classified risk level
            threshold: Minimum risk level for alerts
            
        Returns:
            True if alert should be sent
        """
        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3
        }
        
        return risk_order.get(risk_level, 0) >= risk_order.get(threshold, 2)
