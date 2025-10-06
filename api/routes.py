from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import List, Optional
from datetime import datetime
import uuid
import json
from api.schema import (
    HealthCheckResponse, 
    PatientInfoResponse, 
    PatientAnalysisRequest,
    PatientAnalysisResponse,
    FileUploadResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1", tags=["Healthcare"])

# In-memory storage for demo (use database in production)
patients_db = {}
files_db = {}

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }

@router.post("/patient/analysis", response_model=PatientAnalysisResponse)
async def create_patient_analysis(patient_data: PatientAnalysisRequest):
    """Create a new patient analysis request"""
    try:
        # Generate unique IDs
        patient_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())
        
        # Calculate age from birth date
        today = datetime.now().date()
        age = today.year - patient_data.birth_date.year - \
              ((today.month, today.day) < (patient_data.birth_date.month, patient_data.birth_date.day))
        
        # Store patient data (in production, save to database)
        patient_record = {
            "patient_id": patient_id,
            "analysis_id": analysis_id,
            "personal_info": {
                "first_name": patient_data.first_name,
                "last_name": patient_data.last_name,
                "email": patient_data.email,
                "phone": patient_data.phone,
                "birth_date": patient_data.birth_date.isoformat(),
                "age": age,
                "gender": patient_data.gender,
                "address": patient_data.address,
                "zip_code": patient_data.zip_code
            },
            "emergency_contact": patient_data.emergency_contact.dict() if patient_data.emergency_contact else None,
            "medical_info": patient_data.medical_info.dict() if patient_data.medical_info else None,
            "analysis_options": patient_data.analysis_options.dict() if patient_data.analysis_options else None,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        patients_db[patient_id] = patient_record
        
        # Determine next steps based on analysis options
        next_steps = ["Patient data received and validated"]
        
        if patient_data.analysis_options:
            if patient_data.analysis_options.xray_analysis:
                next_steps.append("X-ray analysis will be performed")
            if patient_data.analysis_options.ocr_enabled:
                next_steps.append("Document OCR processing initiated")
            if patient_data.analysis_options.pii_masking:
                next_steps.append("PII masking will be applied")
            
            priority_msg = f"Analysis priority: {patient_data.analysis_options.priority.value}"
            next_steps.append(priority_msg)
        
        next_steps.extend([
            "Multi-agent analysis pipeline started",
            "Results will be available in the dashboard",
            "Email notification will be sent upon completion"
        ])
        
        return PatientAnalysisResponse(
            success=True,
            message=f"Patient analysis request created successfully for {patient_data.first_name} {patient_data.last_name}",
            patient_id=patient_id,
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            next_steps=next_steps
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing patient analysis request: {str(e)}"
        )

@router.get("/patient/{patient_id}", response_model=dict)
async def get_patient_info(patient_id: str):
    """Get patient information by ID"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patients_db[patient_id]

@router.get("/patients", response_model=dict)
async def get_all_patients():
    """Get all patients (for testing)"""
    return {
        "total_patients": len(patients_db),
        "patients": list(patients_db.values())
    }

@router.post("/upload/documents", response_model=List[FileUploadResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    patient_id: Optional[str] = Form(None)
):
    """Upload multiple medical documents"""
    responses = []
    
    for file in files:
        try:
            # Validate file type
            allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
            if file.content_type not in allowed_types:
                responses.append(FileUploadResponse(
                    success=False,
                    message=f"File type {file.content_type} not allowed",
                    file_name=file.filename,
                    file_size=0,
                    file_type=file.content_type
                ))
                continue
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size (10MB limit)
            if file_size > 10 * 1024 * 1024:  # 10MB
                responses.append(FileUploadResponse(
                    success=False,
                    message="File size exceeds 10MB limit",
                    file_name=file.filename,
                    file_size=file_size,
                    file_type=file.content_type
                ))
                continue
            
            # Generate file ID and store metadata
            file_id = str(uuid.uuid4())
            file_record = {
                "file_id": file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file_size,
                "patient_id": patient_id,
                "uploaded_at": datetime.now().isoformat(),
                "status": "uploaded"
            }
            
            files_db[file_id] = file_record
            
            responses.append(FileUploadResponse(
                success=True,
                message="File uploaded successfully",
                file_id=file_id,
                file_name=file.filename,
                file_size=file_size,
                file_type=file.content_type
            ))
            
        except Exception as e:
            responses.append(FileUploadResponse(
                success=False,
                message=f"Error uploading file: {str(e)}",
                file_name=file.filename,
                file_size=0,
                file_type=file.content_type if hasattr(file, 'content_type') else "unknown"
            ))
    
    return responses

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working!",
        "data": {
            "framework": "FastAPI",
            "language": "Python"
        }
    }