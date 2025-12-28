"""
Stats Router

Provides dashboard statistics and metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Contract, Change, Alert, RiskLevel, AlertStatus
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics.
    
    Returns:
        - total_contracts: Total number of contracts
        - high_risk_changes: Number of HIGH and CRITICAL risk changes
        - monitored_vendors: Number of unique vendors
        - pending_alerts: Number of pending alerts
    """
    # Total contracts
    total_contracts = db.query(func.count(Contract.id)).scalar() or 0
    
    # High-risk changes (HIGH + CRITICAL)
    high_risk_changes = db.query(func.count(Change.id)).filter(
        Change.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
    ).scalar() or 0
    
    # Monitored vendors (distinct vendors)
    monitored_vendors = db.query(
        func.count(func.distinct(Contract.vendor))
    ).scalar() or 0
    
    # Pending alerts
    pending_alerts = db.query(func.count(Alert.id)).filter(
        Alert.status == AlertStatus.PENDING
    ).scalar() or 0
    
    logger.info(f"Dashboard stats: {total_contracts} contracts, {high_risk_changes} high-risk changes")
    
    return {
        "total_contracts": total_contracts,
        "high_risk_changes": high_risk_changes,
        "monitored_vendors": monitored_vendors,
        "pending_alerts": pending_alerts
    }
