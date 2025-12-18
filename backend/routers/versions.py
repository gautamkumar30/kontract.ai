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
