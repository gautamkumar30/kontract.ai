"""
Test Cases for Alerts Router

Comprehensive tests for all alert endpoints:
- GET / - List alerts with filtering
- GET /{alert_id} - Get alert details
- PATCH /{alert_id} - Update alert status
- DELETE /{alert_id} - Delete alert
- GET /stats/summary - Get alert statistics
"""

import pytest
import uuid
from fastapi import status


class TestListAlerts:
    """Tests for GET / endpoint."""
    
    def test_list_all_alerts(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test listing all alerts."""
        from models import AlertType, AlertStatus
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        
        # Create multiple alerts
        create_test_alert(change.id, alert_type=AlertType.EMAIL, status=AlertStatus.PENDING)
        create_test_alert(change.id, alert_type=AlertType.SLACK, status=AlertStatus.SENT)
        create_test_alert(change.id, alert_type=AlertType.DASHBOARD, status=AlertStatus.FAILED)
        
        response = client.get("/api/alerts/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_list_alerts_empty(self, client):
        """Test listing alerts when none exist."""
        response = client.get("/api/alerts/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_filter_by_status(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test filtering alerts by status."""
        from models import AlertStatus
        
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        
        # Create alerts with different statuses
        create_test_alert(change.id, status=AlertStatus.PENDING)
        create_test_alert(change.id, status=AlertStatus.SENT)
        create_test_alert(change.id, status=AlertStatus.FAILED)
        
        # Filter by pending
        response = client.get("/api/alerts/?status=pending")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        
        # Filter by sent
        response = client.get("/api/alerts/?status=sent")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
    
    def test_filter_by_alert_type(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test filtering alerts by type."""
        from models import AlertType
        
        contract = create_test_contract(vendor="Google", contract_type="privacy")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        
        # Create alerts with different types
        create_test_alert(change.id, alert_type=AlertType.EMAIL)
        create_test_alert(change.id, alert_type=AlertType.SLACK)
        create_test_alert(change.id, alert_type=AlertType.DASHBOARD)
        
        # Filter by email
        response = client.get("/api/alerts/?alert_type=email")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
    
    def test_pagination(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test pagination with skip and limit."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        
        # Create 10 alerts
        for i in range(10):
            create_test_alert(change.id)
        
        # Test skip
        response = client.get("/api/alerts/?skip=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5
        
        # Test limit
        response = client.get("/api/alerts/?limit=3")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
    
    def test_invalid_status_filter(self, client):
        """Test 400 error for invalid status filter."""
        response = client.get("/api/alerts/?status=invalid")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status" in response.json()["detail"]
    
    def test_invalid_alert_type_filter(self, client):
        """Test 400 error for invalid alert type filter."""
        response = client.get("/api/alerts/?alert_type=invalid")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid alert type" in response.json()["detail"]


class TestGetAlert:
    """Tests for GET /{alert_id} endpoint."""
    
    def test_get_alert_details(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test getting alert details."""
        from models import AlertType, AlertStatus
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        alert = create_test_alert(
            change.id,
            alert_type=AlertType.EMAIL,
            status=AlertStatus.PENDING,
            recipient="test@example.com"
        )
        
        response = client.get(f"/api/alerts/{alert.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(alert.id)
        assert data["alert_type"] == "email"
        assert data["status"] == "pending"
    
    def test_get_alert_not_found(self, client):
        """Test 404 error for non-existent alert."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/alerts/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAlert:
    """Tests for PATCH /{alert_id} endpoint."""
    
    def test_update_alert_status_to_sent(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test updating alert status to sent."""
        from models import AlertStatus
        
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        alert = create_test_alert(change.id, status=AlertStatus.PENDING)
        
        response = client.patch(
            f"/api/alerts/{alert.id}",
            json={"status": "sent"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "sent"
    
    def test_update_alert_status_to_failed(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test updating alert status to failed."""
        from models import AlertStatus
        
        contract = create_test_contract(vendor="Google", contract_type="privacy")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        alert = create_test_alert(change.id, status=AlertStatus.PENDING)
        
        response = client.patch(
            f"/api/alerts/{alert.id}",
            json={"status": "failed"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "failed"
    
    def test_update_alert_not_found(self, client):
        """Test 404 error for non-existent alert."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.patch(
            f"/api/alerts/{non_existent_id}",
            json={"status": "sent"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_alert_invalid_status(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test 400 error for invalid status value."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        alert = create_test_alert(change.id)
        
        response = client.patch(
            f"/api/alerts/{alert.id}",
            json={"status": "invalid"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteAlert:
    """Tests for DELETE /{alert_id} endpoint."""
    
    def test_delete_alert_success(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test successfully deleting an alert."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        alert = create_test_alert(change.id)
        
        response = client.delete(f"/api/alerts/{alert.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify alert is deleted
        get_response = client.get(f"/api/alerts/{alert.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_alert_not_found(self, client):
        """Test 404 error for non-existent alert."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.delete(f"/api/alerts/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetAlertStats:
    """Tests for GET /stats/summary endpoint."""
    
    def test_get_alert_statistics(self, client, create_test_contract, create_test_version, create_test_change, create_test_alert):
        """Test getting alert statistics."""
        from models import AlertType, AlertStatus
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(contract.id, v2.id, v1.id)
        
        # Create alerts with different statuses and types
        create_test_alert(change.id, alert_type=AlertType.EMAIL, status=AlertStatus.PENDING)
        create_test_alert(change.id, alert_type=AlertType.EMAIL, status=AlertStatus.SENT)
        create_test_alert(change.id, alert_type=AlertType.SLACK, status=AlertStatus.SENT)
        create_test_alert(change.id, alert_type=AlertType.DASHBOARD, status=AlertStatus.FAILED)
        
        response = client.get("/api/alerts/stats/summary")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify total count
        assert data["total"] == 4
        
        # Verify counts by status
        assert data["by_status"]["pending"] == 1
        assert data["by_status"]["sent"] == 2
        assert data["by_status"]["failed"] == 1
        
        # Verify counts by type
        assert data["by_type"]["email"] == 2
        assert data["by_type"]["slack"] == 1
        assert data["by_type"]["dashboard"] == 1
    
    def test_get_stats_empty(self, client):
        """Test statistics when no alerts exist."""
        response = client.get("/api/alerts/stats/summary")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["by_status"]["pending"] == 0
        assert data["by_type"]["email"] == 0
