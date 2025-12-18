"""
Contract Processor Service

Orchestrates the complete contract processing pipeline:
1. Text extraction (already done during upload)
2. Clause segmentation
3. Fingerprint generation
4. Drift detection (if previous version exists)
5. Risk classification
6. Alert creation
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import (
    Contract, Version, Clause, Fingerprint, Change, Alert,
    ChangeType, RiskLevel, AlertType, AlertStatus
)
from services.clause_segmenter import ClauseSegmenter
from services.fingerprint_engine import FingerprintEngine
from services.drift_detector import DriftDetector
from services.risk_classifier import RiskClassifier
from services.gemini_service import GeminiService
from logger import get_logger

logger = get_logger(__name__)


class ContractProcessor:
    """Orchestrates the complete contract processing pipeline."""
    
    def __init__(
        self,
        db: Session,
        gemini_service: Optional[GeminiService] = None
    ):
        """
        Initialize contract processor.
        
        Args:
            db: Database session
            gemini_service: Optional Gemini service for AI-powered analysis
        """
        self.db = db
        self.segmenter = ClauseSegmenter()
        self.fingerprint_engine = FingerprintEngine()
        self.drift_detector = DriftDetector(gemini_service=gemini_service)
        self.risk_classifier = RiskClassifier(gemini_service=gemini_service)
        self.gemini_service = gemini_service
    
    async def process_new_version(self, version_id: UUID) -> Dict:
        """
        Process a new contract version through the complete pipeline.
        
        Args:
            version_id: UUID of the version to process
            
        Returns:
            Dict with processing results and statistics
        """
        logger.info(f"Starting processing pipeline for version {version_id}")
        
        try:
            # 1. Get version from database
            version = self.db.query(Version).filter(Version.id == version_id).first()
            if not version:
                raise ValueError(f"Version {version_id} not found")
            
            if not version.raw_text:
                raise ValueError(f"Version {version_id} has no raw text to process")
            
            logger.info(f"Processing version {version.version_number} for contract {version.contract_id}")
            
            # 2. Segment into clauses
            logger.info("Segmenting contract into clauses...")
            clauses_data = self.segmenter.segment_text(version.raw_text)
            logger.info(f"Segmented into {len(clauses_data)} clauses")
            
            # 3. Create clause records in database
            clause_records = []
            for clause_data in clauses_data:
                clause = Clause(
                    version_id=version_id,
                    clause_number=clause_data["clause_number"],
                    category=clause_data.get("category"),
                    heading=clause_data.get("heading"),
                    text=clause_data["text"],
                    position_start=clause_data.get("position_start"),
                    position_end=clause_data.get("position_end")
                )
                self.db.add(clause)
                clause_records.append(clause)
            
            self.db.commit()
            logger.info(f"Created {len(clause_records)} clause records in database")
            
            # 4. Generate fingerprints for all clauses
            logger.info("Generating fingerprints...")
            clause_texts = [c.text for c in clause_records]
            fingerprints_data = self.fingerprint_engine.create_batch_fingerprints(clause_texts)
            
            for clause, fp_data in zip(clause_records, fingerprints_data):
                fingerprint = Fingerprint(
                    clause_id=clause.id,
                    text_hash=fp_data["text_hash"],
                    simhash=fp_data["simhash"],
                    tfidf_vector=fp_data["tfidf_vector"],
                    keywords=fp_data["keywords"]
                )
                self.db.add(fingerprint)
            
            self.db.commit()
            logger.info(f"Generated {len(fingerprints_data)} fingerprints")
            
            # 5. Detect drift if previous version exists
            changes_detected = []
            previous_version = self._get_previous_version(version)
            
            if previous_version:
                logger.info(f"Comparing with previous version {previous_version.version_number}")
                changes_detected = await self._detect_and_classify_changes(
                    previous_version=previous_version,
                    current_version=version
                )
                logger.info(f"Detected {len(changes_detected)} changes")
            else:
                logger.info("No previous version found - skipping drift detection")
            
            # 6. Create alerts for high-risk changes
            alerts_created = await self._create_alerts_for_changes(
                changes=changes_detected,
                contract_id=version.contract_id
            )
            
            # 7. Prepare summary
            result = {
                "success": True,
                "version_id": str(version_id),
                "contract_id": str(version.contract_id),
                "version_number": version.version_number,
                "statistics": {
                    "clauses_created": len(clause_records),
                    "fingerprints_generated": len(fingerprints_data),
                    "changes_detected": len(changes_detected),
                    "alerts_created": alerts_created,
                    "high_risk_changes": sum(
                        1 for c in changes_detected 
                        if c.get("risk_level") in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                    )
                }
            }
            
            logger.info(f"Processing complete: {result['statistics']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing version {version_id}: {str(e)}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "version_id": str(version_id),
                "error": str(e)
            }
    
    def _get_previous_version(self, current_version: Version) -> Optional[Version]:
        """
        Get the previous version of a contract.
        
        Args:
            current_version: Current version
            
        Returns:
            Previous version or None
        """
        previous = self.db.query(Version).filter(
            Version.contract_id == current_version.contract_id,
            Version.version_number < current_version.version_number
        ).order_by(desc(Version.version_number)).first()
        
        return previous
    
    async def _detect_and_classify_changes(
        self,
        previous_version: Version,
        current_version: Version
    ) -> List[Dict]:
        """
        Detect changes between versions and classify their risk.
        
        Args:
            previous_version: Previous version
            current_version: Current version
            
        Returns:
            List of change records with risk classification
        """
        # Get clauses with fingerprints for both versions
        old_clauses = self._get_clauses_with_fingerprints(previous_version.id)
        new_clauses = self._get_clauses_with_fingerprints(current_version.id)
        
        # Detect changes
        changes = await self.drift_detector.detect_changes(
            old_clauses=old_clauses,
            new_clauses=new_clauses
        )
        
        # Classify risk for each change and save to database
        change_records = []
        for change_data in changes:
            # Get the relevant clause for risk classification
            clause = None
            if change_data.get("new_clause_id"):
                clause = next(
                    (c for c in new_clauses if c["id"] == change_data["new_clause_id"]),
                    None
                )
            elif change_data.get("old_clause_id"):
                clause = next(
                    (c for c in old_clauses if c["id"] == change_data["old_clause_id"]),
                    None
                )
            
            # Classify risk
            if clause:
                risk_data = await self.risk_classifier.classify_risk(
                    change=change_data,
                    clause=clause
                )
            else:
                # Default risk for clauses without data
                risk_data = {
                    "risk_level": RiskLevel.LOW,
                    "risk_score": 0,
                    "explanation": "Unable to classify risk"
                }
            
            # Create change record
            change = Change(
                contract_id=current_version.contract_id,
                from_version_id=previous_version.id,
                to_version_id=current_version.id,
                clause_id=change_data.get("new_clause_id") or change_data.get("old_clause_id"),
                change_type=change_data["change_type"],
                similarity_score=change_data.get("similarity_score"),
                risk_level=risk_data["risk_level"],
                risk_score=risk_data["risk_score"],
                explanation=risk_data.get("explanation")
            )
            
            self.db.add(change)
            change_records.append({
                "change": change,
                "risk_level": risk_data["risk_level"],
                "risk_score": risk_data["risk_score"]
            })
        
        self.db.commit()
        
        return change_records
    
    def _get_clauses_with_fingerprints(self, version_id: UUID) -> List[Dict]:
        """
        Get all clauses for a version with their fingerprints.
        
        Args:
            version_id: Version UUID
            
        Returns:
            List of clause dictionaries with fingerprint data
        """
        clauses = self.db.query(Clause).filter(
            Clause.version_id == version_id
        ).all()
        
        result = []
        for clause in clauses:
            fingerprint = self.db.query(Fingerprint).filter(
                Fingerprint.clause_id == clause.id
            ).first()
            
            if fingerprint:
                result.append({
                    "id": clause.id,
                    "text": clause.text,
                    "category": clause.category,
                    "heading": clause.heading,
                    "fingerprint": {
                        "text_hash": fingerprint.text_hash,
                        "simhash": fingerprint.simhash,
                        "tfidf_vector": fingerprint.tfidf_vector,
                        "keywords": fingerprint.keywords
                    }
                })
        
        return result
    
    async def _create_alerts_for_changes(
        self,
        changes: List[Dict],
        contract_id: UUID
    ) -> int:
        """
        Create alerts for high-risk changes.
        
        Args:
            changes: List of change records with risk data
            contract_id: Contract UUID
            
        Returns:
            Number of alerts created
        """
        alerts_created = 0
        
        for change_data in changes:
            risk_level = change_data.get("risk_level")
            
            # Create alerts for HIGH and CRITICAL risk changes
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                # Create dashboard alert (always)
                alert = Alert(
                    change_id=change_data["change"].id,
                    alert_type=AlertType.DASHBOARD,
                    status=AlertStatus.SENT  # Dashboard alerts are immediately visible
                )
                self.db.add(alert)
                alerts_created += 1
                
                # TODO: Create email/Slack alerts based on user preferences
                # This will be implemented in Sprint 3
        
        if alerts_created > 0:
            self.db.commit()
            logger.info(f"Created {alerts_created} alerts for high-risk changes")
        
        return alerts_created
