"""
Clauses Router

Handles clause-related operations including listing clauses for a version
and retrieving individual clause details with fingerprints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Clause, Fingerprint, Version
from schemas import ClauseResponse
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/versions/{version_id}/clauses", response_model=List[ClauseResponse])
def list_clauses_for_version(
    version_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all clauses for a specific version.
    
    - **version_id**: UUID of the version
    
    Returns list of clauses with their metadata.
    """
    # Validate UUID format
    try:
        uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {version_id}"
        )
    
    # Verify version exists
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version with ID {version_id} not found"
        )
    
    # Get all clauses for this version
    clauses = db.query(Clause).filter(
        Clause.version_id == version_id
    ).order_by(Clause.clause_number).all()
    
    logger.info(f"Retrieved {len(clauses)} clauses for version {version_id}")
    
    return clauses


@router.get("/clauses/{clause_id}")
def get_clause(
    clause_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific clause.
    
    Returns clause with its fingerprint data.
    """
    # Validate UUID format
    try:
        uuid.UUID(clause_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {clause_id}"
        )
    
    # Get clause
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clause with ID {clause_id} not found"
        )
    
    # Get fingerprint
    fingerprint = db.query(Fingerprint).filter(
        Fingerprint.clause_id == clause_id
    ).first()
    
    # Build response
    response = {
        "id": str(clause.id),
        "version_id": str(clause.version_id),
        "clause_number": clause.clause_number,
        "category": clause.category,
        "heading": clause.heading,
        "text": clause.text,
        "position_start": clause.position_start,
        "position_end": clause.position_end,
        "created_at": clause.created_at,
        "fingerprint": None
    }
    
    if fingerprint:
        response["fingerprint"] = {
            "id": str(fingerprint.id),
            "text_hash": fingerprint.text_hash,
            "simhash": fingerprint.simhash,
            "keywords": fingerprint.keywords,
            "created_at": fingerprint.created_at
        }
    
    logger.info(f"Retrieved clause {clause_id} with fingerprint data")
    
    return response
