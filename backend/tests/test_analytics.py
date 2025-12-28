import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from models import RiskLevel, ChangeType

def test_get_change_trends(client: TestClient, test_db: Session, create_test_contract, create_test_version, create_test_change):
    # Create some test data
    contract = create_test_contract(vendor="Test Vendor")
    version = create_test_version(contract_id=contract.id)
    
    create_test_change(
        contract_id=contract.id,
        to_version_id=version.id,
        change_type=ChangeType.ADDED,
        risk_level=RiskLevel.LOW
    )
    
    response = client.get("/api/analytics/trends?days=7")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["count"] >= 1 for d in data)

def test_get_risk_distribution(client: TestClient, test_db: Session, create_test_contract, create_test_version, create_test_change):
    contract = create_test_contract()
    version = create_test_version(contract_id=contract.id)
    create_test_change(contract_id=contract.id, to_version_id=version.id, risk_level=RiskLevel.HIGH)
    create_test_change(contract_id=contract.id, to_version_id=version.id, risk_level=RiskLevel.LOW)
    
    response = client.get("/api/analytics/risk-distribution")
    assert response.status_code == 200
    data = response.json()
    assert data["high"] >= 1
    assert data["low"] >= 1

def test_get_change_types(client: TestClient, test_db: Session, create_test_contract, create_test_version, create_test_change):
    contract = create_test_contract()
    version = create_test_version(contract_id=contract.id)
    create_test_change(contract_id=contract.id, to_version_id=version.id, change_type=ChangeType.ADDED)
    create_test_change(contract_id=contract.id, to_version_id=version.id, change_type=ChangeType.MODIFIED)
    
    response = client.get("/api/analytics/change-types")
    assert response.status_code == 200
    data = response.json()
    assert data["added"] >= 1
    assert data["modified"] >= 1

def test_get_vendor_stats(client: TestClient, test_db: Session, create_test_contract, create_test_version, create_test_change):
    contract = create_test_contract(vendor="Test Vendor")
    version = create_test_version(contract_id=contract.id)
    create_test_change(contract_id=contract.id, to_version_id=version.id)
    create_test_change(contract_id=contract.id, to_version_id=version.id)
    
    response = client.get("/api/analytics/vendor-stats?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["vendor"] == "Test Vendor"
    assert data[0]["changes"] >= 2
    assert data[0]["contracts"] == 1
