"""
Enhanced Routes for Multi-Agent Healthcare System
Integrates with Coordinator and all agents
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.schema import (
    HealthCheckResponse, 
    PatientInfoResponse, 
    PatientAnalysisRequest,
    PatientAnalysisResponse,
    FileUploadResponse,
    ErrorResponse,
    XRayAnalysisRequest,
    XRayAnalysisResponse,
    TherapyRecommendationResponse,
    SimplePatientRequest
)

# Import agents
from agents.coordinator import Coordinator
from agents.ingestion_agent import IngestionAgent
from agents.imaging_agent import ImagingAgent
from agents.therapy_agent import TherapyAgent
from agents.pharmacy_agent import PharmacyAgent
from agents.doctor_agent import DoctorAgent

router = APIRouter(prefix="/api/v1", tags=["Healthcare"])

# Initialize Coordinator
coordinator = Coordinator(data_dir="./data", upload_dir="./uploads")

# In-memory storage for demo (use database in production)
patients_db = {}
files_db = {}
analysis_results = {}

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Multi-Agent Healthcare API is running successfully",
        "agents_initialized": {
            "coordinator": coordinator is not None,
            "ingestion": coordinator.ingestion_agent is not None,
            "imaging": coordinator.imaging_agent is not None,
            "therapy": coordinator.therapy_agent is not None,
            "pharmacy": coordinator.pharmacy_agent is not None,
            "doctor": coordinator.doctor_agent is not None
        }
    }

@router.post("/patient/simple")
async def create_simple_patient(patient_data: SimplePatientRequest):
    """Simplified patient registration for quick X-ray analysis"""
    try:
        # Generate unique IDs
        patient_id = str(uuid.uuid4())
        
        # Calculate age from birth date
        today = datetime.now().date()
        age = today.year - patient_data.birth_date.year - \
              ((today.month, today.day) < (patient_data.birth_date.month, patient_data.birth_date.day))
        
        # Store simplified patient data
        patient_record = {
            "patient_id": patient_id,
            "name": patient_data.name,
            "birth_date": patient_data.birth_date.isoformat(),
            "age": age,
            "gender": patient_data.gender,
            "city": patient_data.city,
            "zip_code": patient_data.zip_code,
            "symptoms": patient_data.symptoms,
            "allergies": patient_data.allergies,
            "created_at": datetime.now().isoformat()
        }
        
        patients_db[patient_id] = patient_record
        
        return {
            "success": True,
            "message": f"Patient registered: {patient_data.name}",
            "patient_id": patient_id,
            "next_step": "Upload X-ray for analysis"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

@router.post("/patient/analysis", response_model=PatientAnalysisResponse)
async def create_patient_analysis(patient_data: PatientAnalysisRequest):
    """Create a new patient analysis request (legacy - full form)"""
    try:
        # Generate unique IDs
        patient_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())
        
        # Calculate age from birth date
        today = datetime.now().date()
        age = today.year - patient_data.birth_date.year - \
              ((today.month, today.day) < (patient_data.birth_date.month, patient_data.birth_date.day))
        
        # Store patient data
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
        
        # Determine next steps
        next_steps = [
            "✅ Patient data received and validated",
            "🔄 Multi-agent analysis pipeline initialized"
        ]
        
        if patient_data.analysis_options:
            if patient_data.analysis_options.xray_analysis:
                next_steps.append("🩻 X-ray analysis agent ready")
            if patient_data.analysis_options.ocr_enabled:
                next_steps.append("📖 Document OCR processing enabled")
            if patient_data.analysis_options.pii_masking:
                next_steps.append("🔒 PII masking activated")
        
        next_steps.extend([
            "📊 Upload X-ray and documents to start analysis",
            "💊 Therapy recommendations will be generated",
            "🏥 Pharmacy matching will be performed"
        ])
        
        return PatientAnalysisResponse(
            success=True,
            message=f"Patient analysis created for {patient_data.first_name} {patient_data.last_name}",
            patient_id=patient_id,
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            next_steps=next_steps
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing patient analysis: {str(e)}"
        )

@router.post("/xray/analyze")
async def analyze_xray(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    spo2: Optional[int] = Form(98),
    documents: Optional[List[UploadFile]] = File(default=None),
    patient_profile: Optional[str] = Form(None),
    clinical_summary: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None)
):
    """
    Analyze X-ray using Coordinator pipeline
    
    This endpoint triggers the complete multi-agent pipeline:
    1. Ingestion Agent - Validates file
    2. Imaging Agent - Classifies X-ray  
    3. Therapy Agent - Recommends OTC medicines
    4. Pharmacy Agent - Matches nearby pharmacies
    OR Doctor Agent - Escalates if needed
    """
    try:
        # Save uploaded files temporarily
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        saved_documents: List[Path] = []
        if documents:
            for doc in documents:
                doc_path = upload_dir / f"{uuid.uuid4()}_{doc.filename}"
                doc_bytes = await doc.read()
                with open(doc_path, "wb") as handle:
                    handle.write(doc_bytes)
                saved_documents.append(doc_path)
        
        # Get patient info if patient_id provided
        patient_info = {}
        if patient_id and patient_id in patients_db:
            patient_record = patients_db[patient_id]
            personal = patient_record["personal_info"]
            medical = patient_record.get("medical_info", {})
            
            patient_info = {
                "age": personal.get("age", 40),
                "gender": personal.get("gender", "U"),
                "allergies": medical.get("allergies", "").split(",") if medical and medical.get("allergies") else []
            }
        else:
            patient_info = {
                "age": 40,
                "gender": "U",
                "allergies": []
            }

        # Merge inline patient profile if available
        if patient_profile:
            try:
                profile_data = json.loads(patient_profile)
                if isinstance(profile_data, dict):
                    if "age" in profile_data:
                        try:
                            patient_info["age"] = int(profile_data["age"])
                        except (TypeError, ValueError):
                            pass
                    if "gender" in profile_data:
                        patient_info["gender"] = profile_data["gender"]
                    if "allergies" in profile_data:
                        allergies = profile_data["allergies"]
                        if isinstance(allergies, str):
                            allergies = [item.strip() for item in allergies.split(",") if item.strip()]
                        patient_info["allergies"] = allergies or []
                    if "current_medications" in profile_data:
                        meds = profile_data.get("current_medications", [])
                        if isinstance(meds, str):
                            meds = [item.strip() for item in meds.split(",") if item.strip()]
                        patient_info["current_medications"] = meds or []
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid patient_profile JSON payload")
        
        # Prepare upload data for Coordinator
        summary_text = clinical_summary or symptoms or "No symptoms reported"
        pincode_value = (
            pincode
            or patients_db.get(patient_id, {}).get("personal_info", {}).get("zip_code")
            if patient_id else None
        )
        if not pincode_value and isinstance(profile_data := locals().get("profile_data"), dict):
            pincode_value = profile_data.get("zip_code") or profile_data.get("pincode")
        
        upload_data = {
            "xray_file": str(file_path),
            "documents": saved_documents,
            "patient_info": patient_info,
            "symptoms": symptoms if symptoms else summary_text,
            "clinical_summary": summary_text,
            "spo2": spo2,
            "pincode": pincode_value or "380001"
        }
        
        # Execute multi-agent pipeline
        result = coordinator.execute_pipeline(upload_data)
        
        # Store analysis result
        analysis_id = str(uuid.uuid4())
        analysis_results[analysis_id] = {
            "analysis_id": analysis_id,
            "patient_id": patient_id,
            "file_name": file.filename,
            "result": result,
            "created_at": datetime.now().isoformat()
        }
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        for doc_path in saved_documents:
            try:
                os.remove(doc_path)
            except:
                pass
        
        # Format response based on result status
        if result.get("status") == "EMERGENCY":
            return {
                "success": True,
                "status": "EMERGENCY",
                "analysis_id": analysis_id,
                "message": result.get("message"),
                "severity": result.get("severity"),
                "red_flags": result.get("red_flags", []),
                "recommendations": result.get("recommendations", []),
                "action_required": result.get("action_required"),
                "disclaimer": result.get("disclaimer")
            }
        
        elif result.get("status") == "ESCALATED":
            return {
                "success": True,
                "status": "ESCALATED",
                "analysis_id": analysis_id,
                "message": result.get("message"),
                "severity": result.get("severity"),
                "condition": result.get("condition", {}),
                "red_flags": result.get("red_flags", []),
                "doctor_recommendations": result.get("doctor_recommendations", {}),
                "escalation_reason": result.get("escalation_reason"),
                "disclaimer": result.get("disclaimer")
            }
        
        elif result.get("status") == "SUCCESS":
            assessment = result.get("assessment", {})
            treatment = result.get("treatment", {})
            pharmacy = result.get("pharmacy", {})
            
            return {
                "success": True,
                "status": "SUCCESS",
                "analysis_id": analysis_id,
                "message": "Analysis completed successfully",
                "assessment": {
                    "condition": assessment.get("primary_condition"),
                    "probabilities": assessment.get("condition_probabilities", {}),
                    "severity": assessment.get("severity"),
                    "confidence": assessment.get("confidence"),
                    "red_flags": assessment.get("red_flags", [])
                },
                "treatment": {
                    "otc_medicines": treatment.get("otc_medicines", []),
                    "safety_advice": treatment.get("safety_advice", []),
                    "interaction_warnings": treatment.get("interaction_warnings", [])
                },
                "pharmacy": pharmacy if pharmacy else None,
                "order": result.get("order"),
                "recommendations": result.get("recommendations", []),
                "disclaimers": result.get("disclaimers", []),
                "event_log": result.get("event_log", [])
            }
        
        else:  # FAILED
            return {
                "success": False,
                "status": "FAILED",
                "analysis_id": analysis_id,
                "message": result.get("message", "Analysis failed"),
                "error": result.get("error"),
                "failed_at": result.get("failed_at"),
                "recommendations": result.get("recommendations", [])
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing X-ray: {str(e)}"
        )

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]

@router.get("/patient/{patient_id}")
async def get_patient_info(patient_id: str):
    """Get patient information by ID"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patients_db[patient_id]

@router.get("/patients")
async def get_all_patients():
    """Get all patients (for testing)"""
    return {
        "total_patients": len(patients_db),
        "patients": list(patients_db.values())
    }

@router.post("/upload/documents")
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
                responses.append({
                    "success": False,
                    "message": f"File type {file.content_type} not allowed",
                    "file_name": file.filename
                })
                continue
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size (10MB limit)
            if file_size > 10 * 1024 * 1024:
                responses.append({
                    "success": False,
                    "message": "File size exceeds 10MB limit",
                    "file_name": file.filename
                })
                continue
            
            # Save file
            upload_dir = Path("./uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_id = str(uuid.uuid4())
            file_path = upload_dir / f"{file_id}_{file.filename}"
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Store metadata
            file_record = {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "content_type": file.content_type,
                "size": file_size,
                "patient_id": patient_id,
                "uploaded_at": datetime.now().isoformat(),
                "status": "uploaded"
            }
            
            files_db[file_id] = file_record
            
            responses.append({
                "success": True,
                "message": "File uploaded successfully",
                "file_id": file_id,
                "file_name": file.filename,
                "file_size": file_size,
                "file_type": file.content_type
            })
            
        except Exception as e:
            responses.append({
                "success": False,
                "message": f"Error uploading file: {str(e)}",
                "file_name": file.filename
            })
    
    return responses

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Multi-Agent Healthcare API is working!",
        "agents": {
            "coordinator": "initialized",
            "ingestion": "ready",
            "imaging": "ready",
            "therapy": "ready",
            "pharmacy": "ready",
            "doctor": "ready"
        },
        "data_status": {
            "medicines": "30 OTC medicines loaded",
            "pharmacies": "1500 pharmacies available",
            "doctors": "20 doctors available",
            "interactions": "10 drug interactions loaded"
        }
    }
