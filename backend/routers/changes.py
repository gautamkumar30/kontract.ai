"""
Changes Router

Handles change detection and tracking between contract versions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Change, Contract, RiskLevel
from schemas import ChangeResponse, ChangeDetailResponse
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/{contract_id}/changes", response_model=List[ChangeResponse])
def list_changes(
    contract_id: str,
    risk_level: Optional[str] = Query(None, description="Filter by risk level (critical, high, medium, low)"),
    change_type: Optional[str] = Query(None, description="Filter by change type (added, removed, modified, rewritten)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all changes for a specific contract.
    
    Supports filtering by risk level and change type.
    Returns changes in descending order (newest first).
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )
    
    # Build query
    query = db.query(Change).filter(Change.contract_id == contract_id)
    
    # Apply filters
    if risk_level:
        try:
            query = query.filter(Change.risk_level == RiskLevel(risk_level))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk level: {risk_level}. Must be one of: critical, high, medium, low"
            )
    
    if change_type:
        query = query.filter(Change.change_type == change_type)
    
    # Get changes
    changes = query.order_by(
        Change.detected_at.desc()
    ).offset(skip).limit(limit).all()
    
    return changes


@router.get("/changes/{change_id}", response_model=ChangeDetailResponse)
def get_change(
    change_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific change.
    
    Includes before/after clause text, risk analysis, and AI explanation.
    """
    change = db.query(Change).filter(Change.id == change_id).first()
    
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change with ID {change_id} not found"
        )
    
    return change


@router.get("/changes/stats/{contract_id}")
def get_change_stats(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics about changes for a contract.
    
    Returns counts by risk level and change type.
    """
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )
    
    # Get all changes
    changes = db.query(Change).filter(Change.contract_id == contract_id).all()
    
    # Calculate stats
    stats = {
        "total": len(changes),
        "by_risk_level": {
            "critical": len([c for c in changes if c.risk_level == RiskLevel.CRITICAL]),
            "high": len([c for c in changes if c.risk_level == RiskLevel.HIGH]),
            "medium": len([c for c in changes if c.risk_level == RiskLevel.MEDIUM]),
            "low": len([c for c in changes if c.risk_level == RiskLevel.LOW]),
        },
        "by_change_type": {}
    }
    
    # Count by change type
    for change in changes:
        change_type = change.change_type.value if hasattr(change.change_type, 'value') else str(change.change_type)
        stats["by_change_type"][change_type] = stats["by_change_type"].get(change_type, 0) + 1
    
    return stats
