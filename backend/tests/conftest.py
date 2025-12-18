"""
Pytest Configuration and Shared Fixtures

Provides test database setup, test client, and reusable fixtures for testing.
"""

import pytest
import os
import sys
import uuid as uuid_pkg
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String, TypeDecorator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import Base, get_db
from models import Contract, Version, ContractType, SourceType


# Custom UUID type for SQLite compatibility
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses String(36)."""
    
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid_pkg.UUID):
                return str(value)
            return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid_pkg.UUID):
            return value
        return uuid_pkg.UUID(value)


# Test database setup - using existing Docker PostgreSQL database
# Tests will clean up their data before and after each test
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres_password@localhost:5433/contract_drifter"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database session for each test."""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, pool_pre_ping=True)
    
    # Drop all tables to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables fresh
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Clean up - drop all tables after test to leave database clean
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing."""
    return {
        "vendor": "Stripe",
        "contract_type": "tos",
        "source_url": "https://stripe.com/legal/tos"
    }


@pytest.fixture
def sample_contract_no_url():
    """Sample contract data without URL."""
    return {
        "vendor": "AWS",
        "contract_type": "sla"
    }


@pytest.fixture
def create_test_contract(test_db):
    """Fixture to create a test contract in the database."""
    def _create_contract(vendor="TestVendor", contract_type=ContractType.TOS):
        contract = Contract(
            vendor=vendor,
            contract_type=contract_type
        )
        test_db.add(contract)
        test_db.commit()
        test_db.refresh(contract)
        return contract
    
    return _create_contract


@pytest.fixture
def create_test_version(test_db):
    """Fixture to create a test version for a contract."""
    def _create_version(contract_id, version_number=1, raw_text="Sample contract text"):
        version = Version(
            contract_id=contract_id,
            version_number=version_number,
            source_type=SourceType.TEXT,
            raw_text=raw_text
        )
        test_db.add(version)
        test_db.commit()
        test_db.refresh(version)
        return version
    
    return _create_version


@pytest.fixture
def sample_pdf_file():
    """Path to sample PDF file for upload testing."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    return os.path.join(fixtures_dir, "sample_contract.pdf")


@pytest.fixture
def sample_txt_file():
    """Path to sample TXT file for upload testing."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    return os.path.join(fixtures_dir, "sample_contract.txt")


@pytest.fixture
def create_test_clause(test_db):
    """Fixture to create a test clause for a version."""
    from models import Clause
    
    def _create_clause(version_id, clause_number=1, text="Sample clause text", **kwargs):
        clause = Clause(
            version_id=version_id,
            clause_number=clause_number,
            text=text,
            category=kwargs.get('category'),
            heading=kwargs.get('heading'),
            position_start=kwargs.get('position_start'),
            position_end=kwargs.get('position_end')
        )
        test_db.add(clause)
        test_db.commit()
        test_db.refresh(clause)
        return clause
    
    return _create_clause


@pytest.fixture
def create_test_change(test_db):
    """Fixture to create a test change."""
    from models import Change, ChangeType, RiskLevel
    
    def _create_change(contract_id, to_version_id, from_version_id=None, **kwargs):
        change = Change(
            contract_id=contract_id,
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            change_type=kwargs.get('change_type', ChangeType.MODIFIED),
            risk_level=kwargs.get('risk_level', RiskLevel.MEDIUM),
            similarity_score=kwargs.get('similarity_score'),
            risk_score=kwargs.get('risk_score'),
            explanation=kwargs.get('explanation'),
            clause_id=kwargs.get('clause_id')
        )
        test_db.add(change)
        test_db.commit()
        test_db.refresh(change)
        return change
    
    return _create_change


@pytest.fixture
def create_test_alert(test_db):
    """Fixture to create a test alert."""
    from models import Alert, AlertType, AlertStatus
    
    def _create_alert(change_id, **kwargs):
        alert = Alert(
            change_id=change_id,
            alert_type=kwargs.get('alert_type', AlertType.EMAIL),
            status=kwargs.get('status', AlertStatus.PENDING),
            recipient=kwargs.get('recipient')
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)
        return alert
    
    return _create_alert
