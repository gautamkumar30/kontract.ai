from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from database import Base


class ContractType(str, enum.Enum):
    """Contract type enumeration."""
    TOS = "tos"  # Terms of Service
    SLA = "sla"  # Service Level Agreement
    DPA = "dpa"  # Data Processing Agreement
    PRIVACY = "privacy"  # Privacy Policy
    OTHER = "other"


class SourceType(str, enum.Enum):
    """Source type for contract versions."""
    PDF = "pdf"
    URL = "url"
    TEXT = "text"


class ChangeType(str, enum.Enum):
    """Type of change detected."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    REWRITTEN = "rewritten"


class RiskLevel(str, enum.Enum):
    """Risk level classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertType(str, enum.Enum):
    """Alert delivery type."""
    EMAIL = "email"
    SLACK = "slack"
    DASHBOARD = "dashboard"


class AlertStatus(str, enum.Enum):
    """Alert delivery status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Contract(Base):
    """Contract model representing a vendor's contract."""
    
    __tablename__ = "contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor = Column(String(255), nullable=False, index=True)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    versions = relationship("Version", back_populates="contract", cascade="all, delete-orphan")
    changes = relationship("Change", back_populates="contract", cascade="all, delete-orphan")


class Version(Base):
    """Version model representing a specific version of a contract."""
    
    __tablename__ = "versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    source_url = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="versions")
    clauses = relationship("Clause", back_populates="version", cascade="all, delete-orphan")
    changes_from = relationship("Change", foreign_keys="Change.from_version_id", back_populates="from_version")
    changes_to = relationship("Change", foreign_keys="Change.to_version_id", back_populates="to_version")


class Clause(Base):
    """Clause model representing an individual clause within a version."""
    
    __tablename__ = "clauses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=False, index=True)
    clause_number = Column(Integer, nullable=False)
    category = Column(String(50), nullable=True)  # liability, data_usage, termination, etc.
    heading = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    position_start = Column(Integer, nullable=True)
    position_end = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    version = relationship("Version", back_populates="clauses")
    fingerprint = relationship("Fingerprint", back_populates="clause", uselist=False, cascade="all, delete-orphan")
    changes = relationship("Change", back_populates="clause", cascade="all, delete-orphan")


class Fingerprint(Base):
    """Fingerprint model storing semantic fingerprint of a clause."""
    
    __tablename__ = "fingerprints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("clauses.id"), unique=True, nullable=False)
    text_hash = Column(String(64), nullable=False)
    simhash = Column(String(64), nullable=True)
    tfidf_vector = Column(JSON, nullable=True)  # Store as JSON array
    keywords = Column(JSON, nullable=True)  # Top keywords with weights
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    clause = relationship("Clause", back_populates="fingerprint")


class Change(Base):
    """Change model representing detected changes between versions."""
    
    __tablename__ = "changes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True)
    from_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=True)
    to_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=False)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("clauses.id"), nullable=True)
    change_type = Column(SQLEnum(ChangeType), nullable=False)
    similarity_score = Column(Float, nullable=True)
    risk_level = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    risk_score = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="changes")
    from_version = relationship("Version", foreign_keys=[from_version_id], back_populates="changes_from")
    to_version = relationship("Version", foreign_keys=[to_version_id], back_populates="changes_to")
    clause = relationship("Clause", back_populates="changes")
    alerts = relationship("Alert", back_populates="change", cascade="all, delete-orphan")


class Alert(Base):
    """Alert model representing notifications sent for changes."""
    
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_id = Column(UUID(as_uuid=True), ForeignKey("changes.id"), nullable=False)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    recipient = Column(String(255), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    change = relationship("Change", back_populates="alerts")
