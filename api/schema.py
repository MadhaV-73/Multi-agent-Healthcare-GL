from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    prefer_not_to_say = "Prefer not to say"

class PriorityEnum(str, Enum):
    standard = "Standard"
    urgent = "Urgent"
    emergency = "Emergency"

class EmergencyContact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relation: Optional[str] = None

class MedicalInfo(BaseModel):
    allergies: Optional[str] = None
    medications: Optional[str] = None
    conditions: Optional[str] = None
    symptoms: Optional[str] = None

class AnalysisOptions(BaseModel):
    xray_analysis: bool = False
    ocr_enabled: bool = True
    pii_masking: bool = True
    priority: PriorityEnum = PriorityEnum.standard

class PatientAnalysisRequest(BaseModel):
    # Required fields
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    gender: GenderEnum
    address: str
    zip_code: str
    
    # Optional fields
    emergency_contact: Optional[EmergencyContact] = None
    medical_info: Optional[MedicalInfo] = None
    analysis_options: Optional[AnalysisOptions] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError('Phone number must contain at least 10 digits')
        return v
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('ZIP code must be at least 5 characters')
        return v.strip()

class SimplePatientRequest(BaseModel):
    """Simplified patient registration for quick X-ray analysis"""
    name: str
    birth_date: date
    gender: str  # M, F, or U
    city: str
    zip_code: str
    symptoms: Optional[str] = ""
    allergies: Optional[str] = ""
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.upper() not in ['M', 'F', 'U']:
            raise ValueError('Gender must be M, F, or U')
        return v.upper()
    
    @validator('zip_code')
    def validate_zip(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('ZIP code must be at least 5 characters')
        return v.strip()

class PatientAnalysisResponse(BaseModel):
    success: bool
    message: str
    patient_id: Optional[str] = None
    analysis_id: Optional[str] = None
    timestamp: datetime
    next_steps: List[str]

class HealthCheckResponse(BaseModel):
    status: str
    message: str

class PatientInfoResponse(BaseModel):
    patient_id: int
    name: str
    age: int
    condition: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    file_name: str
    file_size: int
    file_type: str

class XRayAnalysisRequest(BaseModel):
    """Request model for X-ray analysis (not used in multipart form)"""
    patient_id: Optional[str] = None
    symptoms: Optional[str] = None
    spo2: Optional[int] = 98

class XRayAnalysisResponse(BaseModel):
    """Response model for X-ray analysis"""
    success: bool
    status: str  # SUCCESS, ESCALATED, EMERGENCY, FAILED
    analysis_id: str
    message: str

class TherapyRecommendationResponse(BaseModel):
    """Response model for therapy recommendations"""
    success: bool
    recommendations: dict
    pharmacy_matches: Optional[List[dict]] = None