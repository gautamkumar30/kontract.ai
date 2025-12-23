"""
Analytics Router

Provides analytics data for the dashboard including trends, risk distribution,
change types, and vendor statistics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
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
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
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
    # Single query with GROUP BY for efficiency
    results = db.query(
        Change.risk_level,
        func.count(Change.id).label('count')
    ).group_by(Change.risk_level).all()
    
    distribution = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    for row in results:
        if row.risk_level:
            distribution[row.risk_level.value] = row.count
    
    logger.info(f"Risk distribution: {distribution}")
    return distribution


@router.get("/change-types")
def get_change_types(db: Session = Depends(get_db)):
    """
    Get distribution of changes by type.
    
    Returns counts for each change type: added, removed, modified, rewritten.
    """
    # Single query with GROUP BY for efficiency
    results = db.query(
        Change.change_type,
        func.count(Change.id).label('count')
    ).group_by(Change.change_type).all()
    
    types = {
        "added": 0,
        "removed": 0,
        "modified": 0,
        "rewritten": 0
    }
    for row in results:
        if row.change_type:
            types[row.change_type.value] = row.count
    
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
    # Single query with JOIN and aggregation to avoid N+1 problem
    results = db.query(
        Contract.vendor,
        func.count(func.distinct(Contract.id)).label('contracts'),
        func.count(Change.id).label('changes')
    ).outerjoin(
        Change, Change.contract_id == Contract.id
    ).group_by(
        Contract.vendor
    ).order_by(
        func.count(Change.id).desc()
    ).limit(limit).all()
    
    sorted_vendors = [
        {
            "vendor": row.vendor,
            "changes": row.changes,
            "contracts": row.contracts
        }
        for row in results
    ]
    
    logger.info(f"Retrieved stats for {len(sorted_vendors)} vendors")
    return sorted_vendors
