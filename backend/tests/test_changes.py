"""
Test Cases for Changes Router

Comprehensive tests for all change endpoints:
- GET /{contract_id}/changes - List changes with filtering
- GET /changes/{change_id} - Get change details
- GET /changes/stats/{contract_id} - Get change statistics
"""

import pytest
import uuid
from fastapi import status


class TestListChanges:
    """Tests for GET /{contract_id}/changes endpoint."""
    
    def test_list_changes_for_contract(self, client, create_test_contract, create_test_version, create_test_change):
        """Test listing all changes for a contract."""
        from models import ChangeType, RiskLevel
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        
        # Create multiple changes
        change1 = create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.MODIFIED, risk_level=RiskLevel.HIGH)
        change2 = create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.ADDED, risk_level=RiskLevel.LOW)
        change3 = create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.REMOVED, risk_level=RiskLevel.CRITICAL)
        
        response = client.get(f"/api/contracts/{contract.id}/changes")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_list_changes_empty(self, client, create_test_contract):
        """Test listing changes for contract with no changes."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        
        response = client.get(f"/api/contracts/{contract.id}/changes")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_filter_by_risk_level(self, client, create_test_contract, create_test_version, create_test_change):
        """Test filtering changes by risk level."""
        from models import ChangeType, RiskLevel
        
        contract = create_test_contract(vendor="Google", contract_type="privacy")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        
        # Create changes with different risk levels
        create_test_change(contract.id, v2.id, v1.id, risk_level=RiskLevel.CRITICAL)
        create_test_change(contract.id, v2.id, v1.id, risk_level=RiskLevel.HIGH)
        create_test_change(contract.id, v2.id, v1.id, risk_level=RiskLevel.MEDIUM)
        create_test_change(contract.id, v2.id, v1.id, risk_level=RiskLevel.LOW)
        
        # Filter by critical
        response = client.get(f"/api/contracts/{contract.id}/changes?risk_level=critical")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        
        # Filter by high
        response = client.get(f"/api/contracts/{contract.id}/changes?risk_level=high")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
    
    def test_filter_by_change_type(self, client, create_test_contract, create_test_version, create_test_change):
        """Test filtering changes by change type."""
        from models import ChangeType, RiskLevel
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        
        # Create changes with different types
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.ADDED)
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.MODIFIED)
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.REMOVED)
        
        # Filter by added
        response = client.get(f"/api/contracts/{contract.id}/changes?change_type=added")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
    
    def test_pagination(self, client, create_test_contract, create_test_version, create_test_change):
        """Test pagination with skip and limit."""
        from models import ChangeType
        
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        
        # Create 10 changes
        for i in range(10):
            create_test_change(contract.id, v2.id, v1.id)
        
        # Test skip
        response = client.get(f"/api/contracts/{contract.id}/changes?skip=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5
        
        # Test limit
        response = client.get(f"/api/contracts/{contract.id}/changes?limit=3")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
    
    def test_contract_not_found(self, client):
        """Test 404 error for non-existent contract."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/{non_existent_id}/changes")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_risk_level(self, client, create_test_contract):
        """Test 400 error for invalid risk level."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        
        response = client.get(f"/api/contracts/{contract.id}/changes?risk_level=invalid")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid risk level" in response.json()["detail"]


class TestGetChange:
    """Tests for GET /changes/{change_id} endpoint."""
    
    def test_get_change_details(self, client, create_test_contract, create_test_version, create_test_change):
        """Test getting detailed change information."""
        from models import ChangeType, RiskLevel
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        change = create_test_change(
            contract.id, v2.id, v1.id,
            change_type=ChangeType.MODIFIED,
            risk_level=RiskLevel.HIGH,
            explanation="Significant change detected"
        )
        
        response = client.get(f"/api/contracts/changes/{change.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(change.id)
        assert data["change_type"] == "modified"
        assert data["risk_level"] == "high"
    
    def test_get_change_not_found(self, client):
        """Test 404 error for non-existent change."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/changes/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetChangeStats:
    """Tests for GET /changes/stats/{contract_id} endpoint."""
    
    def test_get_change_statistics(self, client, create_test_contract, create_test_version, create_test_change):
        """Test getting change statistics for a contract."""
        from models import ChangeType, RiskLevel
        
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        v1 = create_test_version(contract.id, version_number=1)
        v2 = create_test_version(contract.id, version_number=2)
        
        # Create changes with different risk levels and types
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.ADDED, risk_level=RiskLevel.CRITICAL)
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.MODIFIED, risk_level=RiskLevel.HIGH)
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.MODIFIED, risk_level=RiskLevel.MEDIUM)
        create_test_change(contract.id, v2.id, v1.id, change_type=ChangeType.REMOVED, risk_level=RiskLevel.LOW)
        
        response = client.get(f"/api/contracts/changes/stats/{contract.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify total count
        assert data["total"] == 4
        
        # Verify counts by risk level
        assert data["by_risk_level"]["critical"] == 1
        assert data["by_risk_level"]["high"] == 1
        assert data["by_risk_level"]["medium"] == 1
        assert data["by_risk_level"]["low"] == 1
        
        # Verify counts by change type
        assert data["by_change_type"]["added"] == 1
        assert data["by_change_type"]["modified"] == 2
        assert data["by_change_type"]["removed"] == 1
    
    def test_get_stats_empty(self, client, create_test_contract):
        """Test statistics for contract with no changes."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        
        response = client.get(f"/api/contracts/changes/stats/{contract.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["by_risk_level"]["critical"] == 0
    
    def test_get_stats_contract_not_found(self, client):
        """Test 404 error for non-existent contract."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/changes/stats/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
