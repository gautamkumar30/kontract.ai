"""
Drift Detector Service

Detects changes between contract versions by comparing clause fingerprints.
"""

from typing import List, Dict, Optional, Tuple
from models import ChangeType
from services.fingerprint_engine import FingerprintEngine
from services.gemini_service import GeminiService


class DriftDetector:
    """Service for detecting changes between contract versions."""
    
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        """
        Initialize drift detector.
        
        Args:
            gemini_service: Optional Gemini service for enhanced analysis
        """
        self.fingerprint_engine = FingerprintEngine()
        self.gemini_service = gemini_service
        
        # Similarity thresholds
        self.IDENTICAL_THRESHOLD = 0.95
        self.MODIFIED_THRESHOLD = 0.6
        self.REWRITTEN_THRESHOLD = 0.3
    
    async def detect_changes(
        self,
        old_clauses: List[Dict[str, any]],
        new_clauses: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Detect changes between two versions of a contract.
        
        Args:
            old_clauses: Clauses from previous version (with fingerprints)
            new_clauses: Clauses from new version (with fingerprints)
            
        Returns:
            List of detected changes
        """
        changes = []
        
        # Track which clauses have been matched
        matched_old = set()
        matched_new = set()
        
        # Find matches and modifications
        for new_clause in new_clauses:
            best_match = None
            best_similarity = 0.0
            
            for old_clause in old_clauses:
                if old_clause["id"] in matched_old:
                    continue
                
                # Calculate similarity
                similarity = self.fingerprint_engine.calculate_similarity(
                    old_clause["fingerprint"],
                    new_clause["fingerprint"]
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = old_clause
            
            # Classify change type
            if best_similarity >= self.IDENTICAL_THRESHOLD:
                # No significant change
                matched_old.add(best_match["id"])
                matched_new.add(new_clause["id"])
            
            elif best_similarity >= self.MODIFIED_THRESHOLD:
                # Modified clause
                change = await self._create_change(
                    change_type=ChangeType.MODIFIED,
                    old_clause=best_match,
                    new_clause=new_clause,
                    similarity=best_similarity
                )
                changes.append(change)
                matched_old.add(best_match["id"])
                matched_new.add(new_clause["id"])
            
            elif best_similarity >= self.REWRITTEN_THRESHOLD:
                # Significantly rewritten
                change = await self._create_change(
                    change_type=ChangeType.REWRITTEN,
                    old_clause=best_match,
                    new_clause=new_clause,
                    similarity=best_similarity
                )
                changes.append(change)
                matched_old.add(best_match["id"])
                matched_new.add(new_clause["id"])
            
            else:
                # New clause (no good match found)
                change = await self._create_change(
                    change_type=ChangeType.ADDED,
                    old_clause=None,
                    new_clause=new_clause,
                    similarity=0.0
                )
                changes.append(change)
                matched_new.add(new_clause["id"])
        
        # Find removed clauses
        for old_clause in old_clauses:
            if old_clause["id"] not in matched_old:
                change = await self._create_change(
                    change_type=ChangeType.REMOVED,
                    old_clause=old_clause,
                    new_clause=None,
                    similarity=0.0
                )
                changes.append(change)
        
        return changes
    
    async def _create_change(
        self,
        change_type: ChangeType,
        old_clause: Optional[Dict[str, any]],
        new_clause: Optional[Dict[str, any]],
        similarity: float
    ) -> Dict[str, any]:
        """
        Create a change object with optional Gemini-powered summary.
        
        Args:
            change_type: Type of change
            old_clause: Old clause (if any)
            new_clause: New clause (if any)
            similarity: Similarity score
            
        Returns:
            Change dictionary
        """
        change = {
            "change_type": change_type,
            "old_clause_id": old_clause["id"] if old_clause else None,
            "new_clause_id": new_clause["id"] if new_clause else None,
            "similarity_score": similarity,
            "summary": None
        }
        
        # Generate summary using Gemini if available
        if self.gemini_service:
            try:
                old_text = old_clause["text"] if old_clause else ""
                new_text = new_clause["text"] if new_clause else ""
                
                summary = await self.gemini_service.generate_change_summary(
                    old_text=old_text,
                    new_text=new_text,
                    change_type=change_type.value
                )
                
                change["summary"] = summary
            except Exception as e:
                print(f"Error generating summary: {e}")
        
        return change
    
    @staticmethod
    def calculate_change_magnitude(similarity: float) -> str:
        """
        Calculate magnitude of change.
        
        Args:
            similarity: Similarity score
            
        Returns:
            Magnitude label (major/moderate/minor)
        """
        if similarity >= 0.8:
            return "minor"
        elif similarity >= 0.5:
            return "moderate"
        else:
            return "major"
    
    def generate_diff(
        self,
        old_text: str,
        new_text: str
    ) -> Dict[str, any]:
        """
        Generate a detailed diff between two texts.
        
        Args:
            old_text: Original text
            new_text: New text
            
        Returns:
            Diff information
        """
        # Simple word-level diff
        old_words = old_text.split()
        new_words = new_text.split()
        
        # Calculate additions and deletions
        old_set = set(old_words)
        new_set = set(new_words)
        
        added_words = new_set - old_set
        removed_words = old_set - new_set
        
        return {
            "old_text": old_text,
            "new_text": new_text,
            "added_words": list(added_words),
            "removed_words": list(removed_words),
            "word_count_change": len(new_words) - len(old_words)
        }
