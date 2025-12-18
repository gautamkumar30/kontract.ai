"""
Contracts Router

Handles contract CRUD operations and file uploads.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from datetime import datetime

from database import get_db, get_settings
from models import Contract, Version, ContractType, SourceType
from schemas import ContractCreate, ContractResponse, ContractListResponse
from services.text_extractor import TextExtractor
from services.contract_processor import ContractProcessor
from logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new contract.
    
    - **vendor**: Vendor name (e.g., "Stripe", "AWS")
    - **contract_type**: Type of contract (tos, sla, dpa, privacy, other)
    - **source_url**: Optional URL to monitor for changes
    """
    try:
        logger.info(f"Creating new contract for vendor: {contract.vendor}, type: {contract.contract_type}")
        
        # Create contract
        db_contract = Contract(
            vendor=contract.vendor,
            contract_type=ContractType(contract.contract_type)
        )
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        
        logger.info(f"Contract created successfully: ID={db_contract.id}")
        
        # Create initial version if URL provided
        if contract.source_url:
            logger.info(f"Extracting text from URL: {contract.source_url}")
            extractor = TextExtractor()
            result = await extractor.extract_from_url(contract.source_url)
            
            if result["success"]:
                version = Version(
                    contract_id=db_contract.id,
                    version_number=1,
                    source_type=SourceType.URL,
                    source_url=contract.source_url,
                    raw_text=result["raw_text"]
                )
                db.add(version)
                db.commit()
                db.refresh(version)
                logger.info(f"Initial version created for contract {db_contract.id}")
                
                # Trigger processing pipeline
                processor = ContractProcessor(db=db)
                processing_result = await processor.process_new_version(version.id)
                logger.info(f"Processing pipeline completed: {processing_result.get('statistics')}")
            else:
                logger.warning(f"Text extraction failed for {contract.source_url}: {result.get('error')}")
        
        return db_contract
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create contract for vendor {contract.vendor}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contract: {str(e)}"
        )


@router.get("/", response_model=List[ContractListResponse])
def list_contracts(
    skip: int = 0,
    limit: int = 100,
    vendor: Optional[str] = None,
    contract_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all contracts with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **vendor**: Filter by vendor name
    - **contract_type**: Filter by contract type
    """
    query = db.query(Contract)
    
    if vendor:
        query = query.filter(Contract.vendor.ilike(f"%{vendor}%"))
    
    if contract_type:
        query = query.filter(Contract.contract_type == contract_type)
    
    contracts = query.offset(skip).limit(limit).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    Get contract details by ID.
    
    Returns full contract information including relationships.
    """
    # Validate UUID format
    try:
        uuid.UUID(contract_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {contract_id}"
        )
    
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )
    
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a contract and all associated data.
    
    This will cascade delete all versions, clauses, changes, and alerts.
    
    """
    # Validate UUID format
    try:
        uuid.UUID(contract_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {contract_id}"
        )
    
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )
    
    db.delete(contract)
    db.commit()
    
    return None


@router.post("/upload", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    vendor: str = Form(..., description="Vendor name"),
    contract_type: str = Form(..., description="Contract type (tos, sla, dpa, privacy, other)"),
    file: UploadFile = File(..., description="Contract file (PDF, TXT, DOC)"),
    db: Session = Depends(get_db)
):
    """
    Upload a contract file.
    
    Supports PDF, TXT, and DOC files. The file will be processed to extract text.
    """
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    logger.info(f"Uploading contract file: {file.filename}, type: {file.content_type}, vendor: {vendor}")
    
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type rejected: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed: PDF, TXT, DOC, DOCX"
        )
    
    # Validate file size (10MB max)
    content = await file.read()
    file_size_mb = len(content) / 1024 / 1024
    
    if len(content) > settings.max_upload_size:
        logger.warning(f"File too large: {file_size_mb:.2f}MB (max: {settings.max_upload_size / 1024 / 1024}MB)")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    logger.info(f"File validated: {file.filename} ({file_size_mb:.2f}MB)")
    
    try:
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(settings.upload_dir, f"{file_id}{file_extension}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Create contract
        db_contract = Contract(
            vendor=vendor,
            contract_type=ContractType(contract_type)
        )
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        
        logger.info(f"Contract created for upload: ID={db_contract.id}")
        
        # Extract text
        extractor = TextExtractor()
        
        if file.content_type == "application/pdf":
            logger.info(f"Extracting text from PDF: {file.filename}")
            result = await extractor.extract_from_pdf(file_path)
            source_type = SourceType.PDF
        else:
            logger.info(f"Extracting text from text file: {file.filename}")
            # For text files, read directly
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            result = await extractor.extract_from_text(text)
            source_type = SourceType.TEXT
        
        # Create version
        if result["success"] and result["raw_text"]:
            version = Version(
                contract_id=db_contract.id,
                version_number=1,
                source_type=source_type,
                raw_text=result["raw_text"]
            )
            db.add(version)
            db.commit()
            db.refresh(version)
            logger.info(f"Version created for contract {db_contract.id}, extracted {len(result['raw_text'])} characters")
            
            # Trigger processing pipeline
            processor = ContractProcessor(db=db)
            processing_result = await processor.process_new_version(version.id)
            logger.info(f"Processing pipeline completed: {processing_result.get('statistics')}")
        else:
            # If extraction failed, still keep the contract but log error
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Text extraction failed for {file.filename}: {error_msg}")
        
        logger.info(f"Contract upload completed successfully: {db_contract.id}")
        return db_contract
    
    except Exception as e:
        db.rollback()
        # Clean up uploaded file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file after error: {file_path}")
        
        logger.error(f"Failed to upload contract {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload contract: {str(e)}"
        )
