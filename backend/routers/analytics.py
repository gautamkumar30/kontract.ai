"""
Analytics Router

Provides analytics data for the dashboard including trends, risk distribution,
change types, and vendor statistics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import Change, Contract, RiskLevel, ChangeType
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/trends")
def get_change_trends(
    days: Optional[int] = Query(30, description="Number of days to include (7, 30, 90, 365, or 0 for all)"),
    db: Session = Depends(get_db)
):
    """
    Get change trends over time.
    
    Returns an array of {date, count} objects showing changes per day.
    """
    query = db.query(
        func.date(Change.detected_at).label('date'),
        func.count(Change.id).label('count')
    )
    
    # Apply date filter if specified
    if days and days > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Change.detected_at >= cutoff_date)
    
    # Group by date and order
    results = query.group_by(
        func.date(Change.detected_at)
    ).order_by(
        func.date(Change.detected_at)
    ).all()
    
    # Format response
    trends = [
        {
            "date": result.date.strftime("%Y-%m-%d") if result.date else None,
            "count": result.count
        }
        for result in results
    ]
    
    logger.info(f"Retrieved {len(trends)} trend data points for {days} days")
    return trends


@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Get distribution of changes by risk level.
    
    Returns counts for each risk level: critical, high, medium, low.
    """
    # Count changes by risk level
    critical = db.query(func.count(Change.id)).filter(
        Change.risk_level == RiskLevel.CRITICAL
    ).scalar() or 0
    
    high = db.query(func.count(Change.id)).filter(
        Change.risk_level == RiskLevel.HIGH
    ).scalar() or 0
    
    medium = db.query(func.count(Change.id)).filter(
        Change.risk_level == RiskLevel.MEDIUM
    ).scalar() or 0
    
    low = db.query(func.count(Change.id)).filter(
        Change.risk_level == RiskLevel.LOW
    ).scalar() or 0
    
    distribution = {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }
    
    logger.info(f"Risk distribution: {distribution}")
    return distribution


@router.get("/change-types")
def get_change_types(db: Session = Depends(get_db)):
    """
    Get distribution of changes by type.
    
    Returns counts for each change type: added, removed, modified, rewritten.
    """
    # Count changes by type
    added = db.query(func.count(Change.id)).filter(
        Change.change_type == ChangeType.ADDED
    ).scalar() or 0
    
    removed = db.query(func.count(Change.id)).filter(
        Change.change_type == ChangeType.REMOVED
    ).scalar() or 0
    
    modified = db.query(func.count(Change.id)).filter(
        Change.change_type == ChangeType.MODIFIED
    ).scalar() or 0
    
    rewritten = db.query(func.count(Change.id)).filter(
        Change.change_type == ChangeType.REWRITTEN
    ).scalar() or 0
    
    types = {
        "added": added,
        "removed": removed,
        "modified": modified,
        "rewritten": rewritten
    }
    
    logger.info(f"Change types: {types}")
    return types


@router.get("/vendor-stats")
def get_vendor_stats(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of vendors to return"),
    db: Session = Depends(get_db)
):
    """
    Get top vendors by change count.
    
    Returns array of {vendor, changes, contracts} sorted by change count.
    """
    # Get all contracts with their vendors
    contracts = db.query(Contract).all()
    
    # Count changes per contract
    vendor_data = {}
    for contract in contracts:
        vendor = contract.vendor
        if vendor not in vendor_data:
            vendor_data[vendor] = {
                "vendor": vendor,
                "changes": 0,
                "contracts": 0
            }
        
        vendor_data[vendor]["contracts"] += 1
        
        # Count changes for this contract
        change_count = db.query(func.count(Change.id)).filter(
            Change.contract_id == contract.id
        ).scalar() or 0
        
        vendor_data[vendor]["changes"] += change_count
    
    # Sort by change count and limit
    sorted_vendors = sorted(
        vendor_data.values(),
        key=lambda x: x["changes"],
        reverse=True
    )[:limit]
    
    logger.info(f"Retrieved stats for {len(sorted_vendors)} vendors")
    return sorted_vendors
