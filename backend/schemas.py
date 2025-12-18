from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, List
from models import ContractType, SourceType, ChangeType, RiskLevel, AlertType, AlertStatus


# Contract Schemas
class ContractBase(BaseModel):
    vendor: str = Field(..., min_length=1, max_length=255)
    contract_type: ContractType


class ContractCreate(ContractBase):
    source_url: Optional[str] = None


class ContractListResponse(ContractBase):
    """Response for contract list with basic info."""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



class ContractResponse(ContractBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Version Schemas
class VersionBase(BaseModel):
    source_type: SourceType
    source_url: Optional[str] = None
    raw_text: Optional[str] = None


class VersionCreate(VersionBase):
    contract_id: UUID4


class VersionResponse(VersionBase):
    id: UUID4
    contract_id: UUID4
    version_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VersionDetailResponse(VersionResponse):
    """Detailed version response with clauses."""
    clauses: List['ClauseResponse'] = []
    
    class Config:
        from_attributes = True


# Clause Schemas
class ClauseBase(BaseModel):
    category: Optional[str] = None
    heading: Optional[str] = None
    text: str
    position_start: Optional[int] = None
    position_end: Optional[int] = None


class ClauseCreate(ClauseBase):
    version_id: UUID4
    clause_number: int


class ClauseResponse(ClauseBase):
    id: UUID4
    version_id: UUID4
    clause_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Fingerprint Schemas
class FingerprintBase(BaseModel):
    text_hash: str
    simhash: Optional[str] = None
    tfidf_vector: Optional[List[float]] = None
    keywords: Optional[dict] = None


class FingerprintCreate(FingerprintBase):
    clause_id: UUID4


class FingerprintResponse(FingerprintBase):
    id: UUID4
    clause_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True


# Change Schemas
class ChangeBase(BaseModel):
    change_type: ChangeType
    similarity_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[int] = None
    explanation: Optional[str] = None


class ChangeCreate(ChangeBase):
    contract_id: UUID4
    from_version_id: Optional[UUID4] = None
    to_version_id: UUID4
    clause_id: Optional[UUID4] = None


class ChangeResponse(ChangeBase):
    id: UUID4
    contract_id: UUID4
    from_version_id: Optional[UUID4]
    to_version_id: UUID4
    clause_id: Optional[UUID4]
    detected_at: datetime
    
    class Config:
        from_attributes = True


class ChangeDetailResponse(ChangeResponse):
    """Detailed change response with related data."""
    pass


# Alert Schemas
class AlertBase(BaseModel):
    alert_type: AlertType
    recipient: Optional[str] = None


class AlertCreate(AlertBase):
    change_id: UUID4


class AlertResponse(AlertBase):
    id: UUID4
    change_id: UUID4
    sent_at: Optional[datetime]
    status: AlertStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Schema for updating alert status."""
    status: Optional[str] = None


# Upload Schemas
class ContractUploadRequest(BaseModel):
    vendor: str
    contract_type: ContractType
    source_type: SourceType
    source_url: Optional[str] = None


class ContractUploadResponse(BaseModel):
    contract_id: UUID4
    version_id: UUID4
    message: str


# Comparison Schemas
class ClauseComparison(BaseModel):
    clause_id: UUID4
    change_type: ChangeType
    old_text: Optional[str]
    new_text: Optional[str]
    similarity_score: Optional[float]
    risk_level: Optional[RiskLevel]
    explanation: Optional[str]


class VersionComparisonResponse(BaseModel):
    contract_id: UUID4
    from_version: int
    to_version: int
    changes: List[ClauseComparison]
    total_changes: int
    high_risk_count: int


# Resolve forward references
VersionDetailResponse.model_rebuild()
