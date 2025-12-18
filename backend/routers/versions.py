"""
Versions Router

Handles contract version management and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Version, Contract, Clause
from schemas import VersionResponse, VersionDetailResponse
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/{contract_id}/versions", response_model=List[VersionResponse])
def list_versions(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    List all versions for a specific contract.
    
    Returns versions in descending order (newest first).
    """
    # Validate UUID format
    import uuid
    try:
        uuid.UUID(contract_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {contract_id}"
        )
    
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )
    
    # Get all versions
    versions = db.query(Version).filter(
        Version.contract_id == contract_id
    ).order_by(Version.version_number.desc()).all()
    
    return versions


@router.get("/versions/{version_id}", response_model=VersionDetailResponse)
def get_version(
    version_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific version.
    
    Includes all clauses and metadata.
    """
    # Validate UUID format
    import uuid
    try:
        uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {version_id}"
        )
    
    version = db.query(Version).filter(Version.id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version with ID {version_id} not found"
        )
    
    return version


@router.get("/versions/{version_id}/clauses")
def get_version_clauses(
    version_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all clauses for a specific version.
    """
    # Validate UUID format
    import uuid
    try:
        uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {version_id}"
        )
    
    version = db.query(Version).filter(Version.id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version with ID {version_id} not found"
        )
    
    clauses = db.query(Clause).filter(
        Clause.version_id == version_id
    ).order_by(Clause.clause_number).all()
    
    return clauses


@router.get("/versions/{version_id}/compare/{other_version_id}")
async def compare_versions(
    version_id: str,
    other_version_id: str,
    db: Session = Depends(get_db)
):
    """
    Compare two versions and return detailed clause-level differences.
    
    - **version_id**: First version UUID (typically older version)
    - **other_version_id**: Second version UUID (typically newer version)
    
    Returns detailed comparison with changes, risk levels, and statistics.
    """
    import uuid
    from models import Change, Fingerprint
    
    # Validate UUIDs
    try:
        uuid.UUID(version_id)
        uuid.UUID(other_version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid UUID format"
        )
    
    # Get both versions
    version1 = db.query(Version).filter(Version.id == version_id).first()
    version2 = db.query(Version).filter(Version.id == other_version_id).first()
    
    if not version1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found"
        )
    
    if not version2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {other_version_id} not found"
        )
    
    # Verify they belong to the same contract
    if version1.contract_id != version2.contract_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Versions must belong to the same contract"
        )
    
    # Get changes between these versions
    changes = db.query(Change).filter(
        Change.from_version_id == version_id,
        Change.to_version_id == other_version_id
    ).all()
    
    # Build detailed response
    change_details = []
    for change in changes:
        # Get clause information
        clause = db.query(Clause).filter(Clause.id == change.clause_id).first()
        
        change_detail = {
            "id": str(change.id),
            "change_type": change.change_type.value,
            "similarity_score": change.similarity_score,
            "risk_level": change.risk_level.value if change.risk_level else None,
            "risk_score": change.risk_score,
            "explanation": change.explanation,
            "detected_at": change.detected_at,
            "clause": {
                "id": str(clause.id),
                "clause_number": clause.clause_number,
                "category": clause.category,
                "heading": clause.heading,
                "text": clause.text
            } if clause else None
        }
        
        change_details.append(change_detail)
    
    # Calculate statistics
    from models import RiskLevel
    high_risk_count = sum(
        1 for c in changes 
        if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    )
    
    response = {
        "contract_id": str(version1.contract_id),
        "from_version": {
            "id": str(version1.id),
            "version_number": version1.version_number,
            "created_at": version1.created_at
        },
        "to_version": {
            "id": str(version2.id),
            "version_number": version2.version_number,
            "created_at": version2.created_at
        },
        "changes": change_details,
        "statistics": {
            "total_changes": len(changes),
            "high_risk_count": high_risk_count,
            "changes_by_type": {
                "added": sum(1 for c in changes if c.change_type.value == "added"),
                "removed": sum(1 for c in changes if c.change_type.value == "removed"),
                "modified": sum(1 for c in changes if c.change_type.value == "modified"),
                "rewritten": sum(1 for c in changes if c.change_type.value == "rewritten")
            }
        }
    }
    
    logger.info(f"Compared versions {version_id} and {other_version_id}: {len(changes)} changes found")
    
    return response
