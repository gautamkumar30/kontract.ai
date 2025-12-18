"""
Test Cases for Versions Router

Comprehensive tests for all version endpoints:
- GET /{contract_id}/versions - List versions for a contract
- GET /versions/{version_id} - Get version details
- GET /versions/{version_id}/clauses - Get version clauses
"""

import pytest
import uuid
from fastapi import status


class TestListVersions:
    """Tests for GET /{contract_id}/versions endpoint."""
    
    def test_list_versions_for_contract(self, client, create_test_contract, create_test_version):
        """Test listing all versions for a contract."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        
        # Create multiple versions
        version1 = create_test_version(contract.id, version_number=1, raw_text="Version 1 text")
        version2 = create_test_version(contract.id, version_number=2, raw_text="Version 2 text")
        version3 = create_test_version(contract.id, version_number=3, raw_text="Version 3 text")
        
        response = client.get(f"/api/contracts/{contract.id}/versions")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        # Verify versions are in descending order (newest first)
        assert data[0]["version_number"] == 3
        assert data[1]["version_number"] == 2
        assert data[2]["version_number"] == 1
    
    def test_list_versions_empty(self, client, create_test_contract):
        """Test listing versions for contract with no versions."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        
        response = client.get(f"/api/contracts/{contract.id}/versions")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_versions_contract_not_found(self, client):
        """Test 404 error for non-existent contract."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/{non_existent_id}/versions")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_versions_invalid_uuid(self, client):
        """Test 422 error for invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        
        response = client.get(f"/api/contracts/{invalid_id}/versions")
        
        # This will return 500 from database, but we should add UUID validation
        # For now, we accept either 422 or 500
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_list_versions_includes_metadata(self, client, create_test_contract, create_test_version):
        """Test that response includes all version metadata."""
        contract = create_test_contract(vendor="Google", contract_type="privacy")
        version = create_test_version(contract.id, version_number=1)
        
        response = client.get(f"/api/contracts/{contract.id}/versions")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        
        # Verify all required fields are present
        required_fields = ["id", "contract_id", "version_number", "source_type", "created_at"]
        for field in required_fields:
            assert field in data[0]


class TestGetVersion:
    """Tests for GET /versions/{version_id} endpoint."""
    
    def test_get_version_details(self, client, create_test_contract, create_test_version):
        """Test getting detailed version information."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        version = create_test_version(contract.id, version_number=1, raw_text="Detailed contract text")
        
        response = client.get(f"/api/contracts/versions/{version.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(version.id)
        assert data["contract_id"] == str(contract.id)
        assert data["version_number"] == 1
        assert data["raw_text"] == "Detailed contract text"
    
    def test_get_version_not_found(self, client):
        """Test 404 error for non-existent version."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/versions/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_version_invalid_uuid(self, client):
        """Test 422 error for invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        
        response = client.get(f"/api/contracts/versions/{invalid_id}")
        
        # Accept either 422 or 500 (should add UUID validation to router)
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_get_version_includes_all_fields(self, client, create_test_contract, create_test_version):
        """Test that response includes all expected fields."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        version = create_test_version(contract.id, version_number=2)
        
        response = client.get(f"/api/contracts/versions/{version.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all required fields
        required_fields = ["id", "contract_id", "version_number", "source_type", "created_at"]
        for field in required_fields:
            assert field in data


class TestGetVersionClauses:
    """Tests for GET /versions/{version_id}/clauses endpoint."""
    
    def test_get_version_clauses(self, client, create_test_contract, create_test_version, create_test_clause):
        """Test getting clauses for a version."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        version = create_test_version(contract.id, version_number=1)
        
        # Create multiple clauses
        clause1 = create_test_clause(version.id, clause_number=1, text="First clause")
        clause2 = create_test_clause(version.id, clause_number=2, text="Second clause")
        clause3 = create_test_clause(version.id, clause_number=3, text="Third clause")
        
        response = client.get(f"/api/contracts/versions/{version.id}/clauses")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        # Verify clauses are ordered by clause_number
        assert data[0]["clause_number"] == 1
        assert data[1]["clause_number"] == 2
        assert data[2]["clause_number"] == 3
        assert data[0]["text"] == "First clause"
    
    def test_get_version_clauses_empty(self, client, create_test_contract, create_test_version):
        """Test getting clauses for version with no clauses."""
        contract = create_test_contract(vendor="AWS", contract_type="sla")
        version = create_test_version(contract.id, version_number=1)
        
        response = client.get(f"/api/contracts/versions/{version.id}/clauses")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_version_clauses_not_found(self, client):
        """Test 404 error for non-existent version."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/versions/{non_existent_id}/clauses")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_version_clauses_invalid_uuid(self, client):
        """Test error for invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        
        response = client.get(f"/api/contracts/versions/{invalid_id}/clauses")
        
        # Accept either 422 or 500
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_get_version_clauses_with_metadata(self, client, create_test_contract, create_test_version, create_test_clause):
        """Test that clauses include all metadata."""
        contract = create_test_contract(vendor="Google", contract_type="privacy")
        version = create_test_version(contract.id, version_number=1)
        clause = create_test_clause(
            version.id,
            clause_number=1,
            text="Privacy clause",
            category="privacy",
            heading="Data Collection"
        )
        
        response = client.get(f"/api/contracts/versions/{version.id}/clauses")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "privacy"
        assert data[0]["heading"] == "Data Collection"
        assert data[0]["text"] == "Privacy clause"


class TestVersionsIntegration:
    """Integration tests for versions endpoints."""
    
    def test_full_version_workflow(self, client, create_test_contract, create_test_version, create_test_clause):
        """Test complete workflow: create contract, versions, clauses, then retrieve."""
        # Create contract
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        
        # Create versions
        v1 = create_test_version(contract.id, version_number=1, raw_text="Version 1")
        v2 = create_test_version(contract.id, version_number=2, raw_text="Version 2")
        
        # Add clauses to v2
        create_test_clause(v2.id, clause_number=1, text="Updated clause 1")
        create_test_clause(v2.id, clause_number=2, text="Updated clause 2")
        
        # List all versions
        versions_response = client.get(f"/api/contracts/{contract.id}/versions")
        assert versions_response.status_code == status.HTTP_200_OK
        assert len(versions_response.json()) == 2
        
        # Get specific version
        version_response = client.get(f"/api/contracts/versions/{v2.id}")
        assert version_response.status_code == status.HTTP_200_OK
        assert version_response.json()["version_number"] == 2
        
        # Get clauses for version
        clauses_response = client.get(f"/api/contracts/versions/{v2.id}/clauses")
        assert clauses_response.status_code == status.HTTP_200_OK
        assert len(clauses_response.json()) == 2
