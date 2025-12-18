"""
Alerts Router

Handles alert management and notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Alert, AlertStatus, AlertType
from schemas import AlertResponse, AlertUpdate
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (pending, sent, failed)"),
    alert_type: Optional[str] = Query(None, description="Filter by type (email, slack, dashboard)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all alerts with optional filtering.
    
    Returns alerts in descending order (newest first).
    """
    query = db.query(Alert)
    
    # Apply filters
    if status_filter:
        try:
            query = query.filter(Alert.status == AlertStatus(status_filter))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}. Must be one of: pending, sent, failed"
            )
    
    if alert_type:
        try:
            query = query.filter(Alert.alert_type == AlertType(alert_type))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid alert type: {alert_type}. Must be one of: email, slack, dashboard"
            )
    
    # Get alerts
    alerts = query.order_by(
        Alert.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Update alert status (e.g., mark as read/sent).
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    # Update status if provided
    if alert_update.status:
        try:
            alert.status = AlertStatus(alert_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {alert_update.status}"
            )
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None


@router.get("/stats/summary")
def get_alert_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics for all alerts.
    """
    alerts = db.query(Alert).all()
    
    stats = {
        "total": len(alerts),
        "by_status": {
            "pending": len([a for a in alerts if a.status == AlertStatus.PENDING]),
            "sent": len([a for a in alerts if a.status == AlertStatus.SENT]),
            "failed": len([a for a in alerts if a.status == AlertStatus.FAILED]),
        },
        "by_type": {
            "email": len([a for a in alerts if a.alert_type == AlertType.EMAIL]),
            "slack": len([a for a in alerts if a.alert_type == AlertType.SLACK]),
            "dashboard": len([a for a in alerts if a.alert_type == AlertType.DASHBOARD]),
        }
    }
    
    return stats
