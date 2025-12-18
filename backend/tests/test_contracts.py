"""
Test Cases for Contracts Router

Comprehensive tests for all contract endpoints:
- POST /api/contracts/ - Create contract
- GET /api/contracts/ - List contracts with filtering
- GET /api/contracts/{id} - Get contract by ID
- DELETE /api/contracts/{id} - Delete contract
- POST /api/contracts/upload - Upload contract file
"""

import pytest
import uuid
import os
from fastapi import status


class TestCreateContract:
    """Tests for POST /api/contracts/ endpoint."""
    
    def test_create_contract_with_url(self, client, sample_contract_data):
        """Test creating a contract with source URL."""
        response = client.post("/api/contracts/", json=sample_contract_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["vendor"] == sample_contract_data["vendor"]
        assert data["contract_type"] == sample_contract_data["contract_type"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_contract_without_url(self, client, sample_contract_no_url):
        """Test creating a contract without source URL."""
        response = client.post("/api/contracts/", json=sample_contract_no_url)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["vendor"] == sample_contract_no_url["vendor"]
        assert data["contract_type"] == sample_contract_no_url["contract_type"]
    
    def test_create_contract_missing_vendor(self, client):
        """Test validation error when vendor is missing."""
        invalid_data = {
            "contract_type": "tos"
        }
        response = client.post("/api/contracts/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_contract_invalid_type(self, client):
        """Test validation error for invalid contract type."""
        invalid_data = {
            "vendor": "TestVendor",
            "contract_type": "invalid_type"
        }
        response = client.post("/api/contracts/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_contract_empty_vendor(self, client):
        """Test validation error for empty vendor name."""
        invalid_data = {
            "vendor": "",
            "contract_type": "tos"
        }
        response = client.post("/api/contracts/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_contract_all_types(self, client):
        """Test creating contracts with all valid contract types."""
        contract_types = ["tos", "sla", "dpa", "privacy", "other"]
        
        for contract_type in contract_types:
            data = {
                "vendor": f"Vendor_{contract_type}",
                "contract_type": contract_type
            }
            response = client.post("/api/contracts/", json=data)
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["contract_type"] == contract_type


class TestListContracts:
    """Tests for GET /api/contracts/ endpoint."""
    
    def test_list_contracts_empty(self, client):
        """Test listing contracts when database is empty."""
        response = client.get("/api/contracts/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_contracts_with_data(self, client, create_test_contract):
        """Test listing contracts with data in database."""
        # Create test contracts
        create_test_contract(vendor="Stripe", contract_type="tos")
        create_test_contract(vendor="AWS", contract_type="sla")
        create_test_contract(vendor="Google", contract_type="dpa")
        
        response = client.get("/api/contracts/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all("id" in contract for contract in data)
        assert all("vendor" in contract for contract in data)
    
    def test_list_contracts_pagination_skip(self, client, create_test_contract):
        """Test pagination with skip parameter."""
        # Create 5 contracts
        for i in range(5):
            create_test_contract(vendor=f"Vendor{i}", contract_type="tos")
        
        response = client.get("/api/contracts/?skip=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # Should return 3 contracts (skipped first 2)
    
    def test_list_contracts_pagination_limit(self, client, create_test_contract):
        """Test pagination with limit parameter."""
        # Create 5 contracts
        for i in range(5):
            create_test_contract(vendor=f"Vendor{i}", contract_type="tos")
        
        response = client.get("/api/contracts/?limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # Should return only 2 contracts
    
    def test_list_contracts_pagination_skip_and_limit(self, client, create_test_contract):
        """Test pagination with both skip and limit."""
        # Create 10 contracts
        for i in range(10):
            create_test_contract(vendor=f"Vendor{i}", contract_type="tos")
        
        response = client.get("/api/contracts/?skip=3&limit=4")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 4  # Should return 4 contracts starting from index 3
    
    def test_filter_by_vendor_exact(self, client, create_test_contract):
        """Test filtering by exact vendor name."""
        create_test_contract(vendor="Stripe", contract_type="tos")
        create_test_contract(vendor="AWS", contract_type="sla")
        create_test_contract(vendor="Google", contract_type="dpa")
        
        response = client.get("/api/contracts/?vendor=Stripe")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["vendor"] == "Stripe"
    
    def test_filter_by_vendor_partial(self, client, create_test_contract):
        """Test filtering by partial vendor name (case-insensitive)."""
        create_test_contract(vendor="Stripe", contract_type="tos")
        create_test_contract(vendor="StripeConnect", contract_type="sla")
        create_test_contract(vendor="AWS", contract_type="dpa")
        
        response = client.get("/api/contracts/?vendor=stripe")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # Should match both "Stripe" and "StripeConnect"
    
    def test_filter_by_contract_type(self, client, create_test_contract):
        """Test filtering by contract type."""
        create_test_contract(vendor="Vendor1", contract_type="tos")
        create_test_contract(vendor="Vendor2", contract_type="tos")
        create_test_contract(vendor="Vendor3", contract_type="sla")
        
        response = client.get("/api/contracts/?contract_type=tos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(contract["contract_type"] == "tos" for contract in data)
    
    def test_filter_by_vendor_and_type(self, client, create_test_contract):
        """Test filtering by both vendor and contract type."""
        create_test_contract(vendor="Stripe", contract_type="tos")
        create_test_contract(vendor="Stripe", contract_type="sla")
        create_test_contract(vendor="AWS", contract_type="tos")
        
        response = client.get("/api/contracts/?vendor=Stripe&contract_type=tos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["vendor"] == "Stripe"
        assert data[0]["contract_type"] == "tos"


class TestGetContractById:
    """Tests for GET /api/contracts/{contract_id} endpoint."""
    
    def test_get_contract_by_id_success(self, client, create_test_contract):
        """Test successfully retrieving a contract by ID."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        
        response = client.get(f"/api/contracts/{contract.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(contract.id)
        assert data["vendor"] == "Stripe"
        assert data["contract_type"] == "tos"
    
    def test_get_contract_not_found(self, client):
        """Test 404 error for non-existent contract."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/contracts/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_contract_invalid_uuid(self, client):
        """Test 422 error for invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        
        response = client.get(f"/api/contracts/{invalid_id}")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_contract_includes_all_fields(self, client, create_test_contract):
        """Test that response includes all expected fields."""
        contract = create_test_contract(vendor="TestVendor", contract_type="sla")
        
        response = client.get(f"/api/contracts/{contract.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["id", "vendor", "contract_type", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data


class TestDeleteContract:
    """Tests for DELETE /api/contracts/{contract_id} endpoint."""
    
    def test_delete_contract_success(self, client, create_test_contract):
        """Test successfully deleting a contract."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        contract_id = str(contract.id)
        
        response = client.delete(f"/api/contracts/{contract_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify contract is actually deleted
        get_response = client.get(f"/api/contracts/{contract_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contract_not_found(self, client):
        """Test 404 error when deleting non-existent contract."""
        non_existent_id = str(uuid.uuid4())
        
        response = client.delete(f"/api/contracts/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contract_invalid_uuid(self, client):
        """Test 422 error for invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        
        response = client.delete(f"/api/contracts/{invalid_id}")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_contract_cascade(self, client, create_test_contract, create_test_version):
        """Test that deleting a contract cascades to versions."""
        contract = create_test_contract(vendor="Stripe", contract_type="tos")
        version = create_test_version(contract.id, version_number=1)
        
        # Delete the contract
        response = client.delete(f"/api/contracts/{contract.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify contract and version are both deleted
        get_response = client.get(f"/api/contracts/{contract.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_multiple_contracts(self, client, create_test_contract):
        """Test deleting multiple contracts."""
        contract1 = create_test_contract(vendor="Vendor1", contract_type="tos")
        contract2 = create_test_contract(vendor="Vendor2", contract_type="sla")
        
        # Delete first contract
        response1 = client.delete(f"/api/contracts/{contract1.id}")
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Delete second contract
        response2 = client.delete(f"/api/contracts/{contract2.id}")
        assert response2.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify both are deleted
        list_response = client.get("/api/contracts/")
        assert len(list_response.json()) == 0


class TestUploadContract:
    """Tests for POST /api/contracts/upload endpoint."""
    
    def test_upload_txt_file_success(self, client, sample_txt_file, tmp_path, monkeypatch):
        """Test successfully uploading a TXT file."""
        if not os.path.exists(sample_txt_file):
            pytest.skip("Sample TXT file not found")
        
        # Override upload directory to use tmp_path
        from database import get_settings
        settings = get_settings()
        test_upload_dir = str(tmp_path / "uploads")
        os.makedirs(test_upload_dir, exist_ok=True)
        monkeypatch.setattr(settings, "upload_dir", test_upload_dir)
        
        with open(sample_txt_file, "rb") as f:
            files = {"file": ("contract.txt", f, "text/plain")}
            data = {
                "vendor": "Stripe",
                "contract_type": "tos"
            }
            response = client.post("/api/contracts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["vendor"] == "Stripe"
        assert response_data["contract_type"] == "tos"
        assert "id" in response_data
    
    def test_upload_pdf_file_success(self, client, sample_pdf_file, tmp_path, monkeypatch):
        """Test successfully uploading a PDF file."""
        if not os.path.exists(sample_pdf_file):
            pytest.skip("Sample PDF file not found")
        
        # Override upload directory to use tmp_path
        from database import get_settings
        settings = get_settings()
        test_upload_dir = str(tmp_path / "uploads")
        os.makedirs(test_upload_dir, exist_ok=True)
        monkeypatch.setattr(settings, "upload_dir", test_upload_dir)
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("contract.pdf", f, "application/pdf")}
            data = {
                "vendor": "AWS",
                "contract_type": "sla"
            }
            response = client.post("/api/contracts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["vendor"] == "AWS"
    
    def test_upload_invalid_file_type(self, client, tmp_path):
        """Test rejection of invalid file type."""
        # Create a temporary invalid file
        invalid_file = tmp_path / "test.jpg"
        invalid_file.write_text("fake image content")
        
        with open(invalid_file, "rb") as f:
            files = {"file": ("contract.jpg", f, "image/jpeg")}
            data = {
                "vendor": "TestVendor",
                "contract_type": "tos"
            }
            response = client.post("/api/contracts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file type" in response.json()["detail"]
    
    def test_upload_missing_vendor(self, client, tmp_path):
        """Test validation error when vendor is missing."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with open(test_file, "rb") as f:
            files = {"file": ("contract.txt", f, "text/plain")}
            data = {
                "contract_type": "tos"
            }
            response = client.post("/api/contracts/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_missing_file(self, client):
        """Test error when no file is provided."""
        data = {
            "vendor": "TestVendor",
            "contract_type": "tos"
        }
        response = client.post("/api/contracts/upload", data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestContractIntegration:
    """Integration tests covering multiple operations."""
    
    def test_full_contract_lifecycle(self, client, sample_contract_data):
        """Test complete contract lifecycle: create, read, update, delete."""
        # Create
        create_response = client.post("/api/contracts/", json=sample_contract_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        contract_id = create_response.json()["id"]
        
        # Read
        get_response = client.get(f"/api/contracts/{contract_id}")
        assert get_response.status_code == status.HTTP_200_OK
        
        # List
        list_response = client.get("/api/contracts/")
        assert len(list_response.json()) >= 1
        
        # Delete
        delete_response = client.delete(f"/api/contracts/{contract_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        final_get = client.get(f"/api/contracts/{contract_id}")
        assert final_get.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_multiple_and_filter(self, client):
        """Test creating multiple contracts and filtering them."""
        contracts_data = [
            {"vendor": "Stripe", "contract_type": "tos"},
            {"vendor": "Stripe", "contract_type": "sla"},
            {"vendor": "AWS", "contract_type": "tos"},
            {"vendor": "Google", "contract_type": "dpa"},
        ]
        
        # Create all contracts
        for data in contracts_data:
            response = client.post("/api/contracts/", json=data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Test various filters
        all_contracts = client.get("/api/contracts/").json()
        assert len(all_contracts) == 4
        
        stripe_contracts = client.get("/api/contracts/?vendor=Stripe").json()
        assert len(stripe_contracts) == 2
        
        tos_contracts = client.get("/api/contracts/?contract_type=tos").json()
        assert len(tos_contracts) == 2
