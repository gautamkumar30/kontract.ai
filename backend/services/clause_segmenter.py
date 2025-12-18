"""
Clause Segmenter Service

Intelligently segments contract text into individual clauses
with category classification.
"""

import re
from typing import List, Dict, Optional


class ClauseSegmenter:
    """Service for segmenting contracts into clauses."""
    
    # Legal keywords for category classification
    CATEGORY_KEYWORDS = {
        "liability": [
            "liability", "indemnification", "damages", "limitation of liability",
            "warranty", "warranties", "disclaimer", "limitation", "cap"
        ],
        "data_usage": [
            "data", "privacy", "personal information", "data processing",
            "data protection", "gdpr", "ccpa", "confidential", "confidentiality"
        ],
        "termination": [
            "termination", "terminate", "cancellation", "cancel", "end",
            "expiration", "expire", "renewal", "term"
        ],
        "jurisdiction": [
            "jurisdiction", "governing law", "venue", "arbitration",
            "dispute resolution", "legal", "court", "forum"
        ],
        "payment": [
            "payment", "fees", "pricing", "billing", "subscription",
            "refund", "charge", "cost", "price"
        ],
        "intellectual_property": [
            "intellectual property", "copyright", "trademark", "patent",
            "ip", "proprietary", "ownership", "license"
        ],
        "service_level": [
            "sla", "service level", "uptime", "availability", "performance",
            "guarantee", "commitment"
        ],
        "marketing": [
            "marketing", "promotional", "communication", "newsletter",
            "advertising", "email"
        ]
    }
    
    @staticmethod
    def segment_text(text: str, sections: List[Dict[str, str]] = None) -> List[Dict[str, any]]:
        """
        Segment text into clauses.
        
        Args:
            text: Full contract text
            sections: Pre-detected sections (optional)
            
        Returns:
            List of clauses with metadata
        """
        clauses = []
        
        if sections:
            # Use pre-detected sections
            for idx, section in enumerate(sections):
                clause = ClauseSegmenter._create_clause(
                    clause_number=idx + 1,
                    heading=section.get("heading"),
                    text=section.get("text", ""),
                    position_start=0,  # Would need to calculate actual position
                    position_end=len(section.get("text", ""))
                )
                clauses.append(clause)
        else:
            # Fallback: segment by paragraphs
            paragraphs = ClauseSegmenter._split_into_paragraphs(text)
            for idx, para in enumerate(paragraphs):
                clause = ClauseSegmenter._create_clause(
                    clause_number=idx + 1,
                    heading=None,
                    text=para,
                    position_start=0,
                    position_end=len(para)
                )
                clauses.append(clause)
        
        return clauses
    
    @staticmethod
    def _create_clause(
        clause_number: int,
        heading: Optional[str],
        text: str,
        position_start: int,
        position_end: int
    ) -> Dict[str, any]:
        """
        Create a clause object with metadata.
        
        Args:
            clause_number: Sequential clause number
            heading: Clause heading (if any)
            text: Clause text
            position_start: Start position in document
            position_end: End position in document
            
        Returns:
            Clause dictionary
        """
        # Classify category
        category = ClauseSegmenter._classify_category(text, heading)
        
        return {
            "clause_number": clause_number,
            "heading": heading,
            "text": text.strip(),
            "category": category,
            "position_start": position_start,
            "position_end": position_end,
            "word_count": len(text.split())
        }
    
    @staticmethod
    def _classify_category(text: str, heading: Optional[str] = None) -> Optional[str]:
        """
        Classify clause category based on keywords.
        
        Args:
            text: Clause text
            heading: Clause heading (optional)
            
        Returns:
            Category name or None
        """
        combined_text = (heading or "") + " " + text
        combined_text = combined_text.lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in ClauseSegmenter.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    @staticmethod
    def _split_into_paragraphs(text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Full text
            
        Returns:
            List of paragraphs
        """
        # Split by double newlines or numbered sections
        paragraphs = re.split(r'\n\n+|\n(?=\d+\.)', text)
        
        # Filter out empty paragraphs and very short ones
        paragraphs = [
            p.strip() for p in paragraphs
            if p.strip() and len(p.strip().split()) > 10
        ]
        
        return paragraphs
    
    @staticmethod
    def merge_short_clauses(clauses: List[Dict[str, any]], min_words: int = 20) -> List[Dict[str, any]]:
        """
        Merge very short clauses with adjacent ones.
        
        Args:
            clauses: List of clauses
            min_words: Minimum word count for a clause
            
        Returns:
            List of merged clauses
        """
        if not clauses:
            return []
        
        merged = []
        current = clauses[0].copy()
        
        for clause in clauses[1:]:
            if current["word_count"] < min_words:
                # Merge with next clause
                current["text"] += " " + clause["text"]
                current["word_count"] += clause["word_count"]
                current["position_end"] = clause["position_end"]
                if not current["heading"] and clause["heading"]:
                    current["heading"] = clause["heading"]
            else:
                merged.append(current)
                current = clause.copy()
        
        # Add last clause
        merged.append(current)
        
        # Renumber clauses
        for idx, clause in enumerate(merged, 1):
            clause["clause_number"] = idx
        
        return merged
