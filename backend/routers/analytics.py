"""
Analytics Router

Provides analytics data for the dashboard including trends, risk distribution,
change types, and vendor statistics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta, timezone
from typing import Optional
import random

from database import get_db
from models import Change, Contract, Version, RiskLevel, ChangeType
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
    limit: int = Query(20, ge=1, le=50, description="Maximum number of vendors to return"),
    db: Session = Depends(get_db)
):
    """
    Get vendor statistics including risk scores and trends.
    
    Returns array of {vendor, score, changes, trend, versions_count} sorted by risk score.
    """
    # Query to aggregate vendor data
    results = db.query(
        Contract.vendor,
        func.count(distinct(Change.id)).label('changes'),
        func.avg(Change.risk_score).label('avg_risk_score'),
        func.max(Version.version_number).label('versions_count')
    ).outerjoin(
        Version, Contract.id == Version.contract_id
    ).outerjoin(
        Change, Contract.id == Change.contract_id
    ).group_by(
        Contract.vendor
    ).limit(limit).all()
    
    # Calculate trend (simplified - compare recent vs older changes)
    vendor_stats = []
    for vendor, changes, avg_risk, versions in results:
        # Get recent changes (last 30 days)
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        recent_changes = db.query(func.count(Change.id)).join(
            Contract, Change.contract_id == Contract.id
        ).filter(
            Contract.vendor == vendor,
            Change.detected_at >= cutoff
        ).scalar() or 0
        
        # Get older changes (30-60 days ago)
        older_cutoff = datetime.now(timezone.utc) - timedelta(days=60)
        older_changes = db.query(func.count(Change.id)).join(
            Contract, Change.contract_id == Contract.id
        ).filter(
            Contract.vendor == vendor,
            Change.detected_at >= older_cutoff,
            Change.detected_at < cutoff
        ).scalar() or 0
        
        # Determine trend
        if recent_changes > older_changes:
            trend = "up"
        elif recent_changes < older_changes:
            trend = "down"
        else:
            trend = "stable"
        
        vendor_stats.append({
            "vendor": vendor,
            "score": int(avg_risk or 0),
            "changes": changes or 0,
            "trend": trend,
            "versions_count": versions or 0
        })
    
    # Sort by risk score descending
    vendor_stats.sort(key=lambda x: x["score"], reverse=True)
    
    logger.info(f"Retrieved stats for {len(vendor_stats)} vendors")
    return vendor_stats


@router.get("/compliance")
def get_compliance_stats(db: Session = Depends(get_db)):
    """
    Get compliance statistics by framework.
    
    Returns compliance status for major frameworks (GDPR, SOC2, HIPAA, CCPA, ISO 27001).
    Note: This is a simplified implementation. In production, you would track
    compliance status per contract in the database.
    """
    frameworks = ["GDPR", "SOC2", "HIPAA", "CCPA", "ISO 27001"]
    total_contracts = db.query(func.count(Contract.id)).scalar() or 0
    
    if total_contracts == 0:
        return []
    
    results = []
    for framework in frameworks:
        # Simplified logic - in production, you'd have a compliance tracking table
        # For now, we'll use risk levels as a proxy for compliance
        high_risk_count = db.query(func.count(distinct(Change.contract_id))).filter(
            Change.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).scalar() or 0
        
        # Estimate compliance based on risk
        non_compliant = min(high_risk_count, total_contracts)
        compliant = max(0, total_contracts - non_compliant - 1)
        pending = max(1, total_contracts - compliant - non_compliant)
        
        results.append({
            "framework": framework,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "pending": pending
        })
    
    logger.info(f"Retrieved compliance stats for {len(results)} frameworks")
    return results
