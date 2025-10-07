"""
Configuration File for Multi-Agent Healthcare System
Location: config.py

Central configuration for paths, thresholds, and constants.
"""

import os
from pathlib import Path

# ============= PROJECT PATHS =============

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Use /tmp for uploads on Render (ephemeral storage)
if os.environ.get('RENDER'):
    UPLOADS_DIR = Path("/tmp/uploads")
    LOGS_DIR = Path("/tmp/logs")
else:
    UPLOADS_DIR = BASE_DIR / "uploads"
    LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [UPLOADS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)   
    
# Data directories
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Data files
PHARMACIES_FILE = DATA_DIR / "pharmacies.json"
INVENTORY_FILE = DATA_DIR / "inventory.csv"
DOCTORS_FILE = DATA_DIR / "doctors.csv"
MEDS_FILE = DATA_DIR / "meds.csv"
INTERACTIONS_FILE = DATA_DIR / "interactions.csv"
ZIPCODES_FILE = DATA_DIR / "zipcodes.csv"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOADS_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)


# ============= AGENT SETTINGS =============

# Imaging Agent
IMAGING_CONFIG = {
    "confidence_threshold": 0.6,  # Below this triggers doctor escalation
    "supported_formats": [".png", ".jpg", ".jpeg"],
    "max_image_size_mb": 10,
    "image_resize_threshold": 1024,  # Resize if larger than this
    "default_severity": "mild"
}

# Therapy Agent
THERAPY_CONFIG = {
    "max_otc_options": 5,  # Maximum OTC medicines to recommend
    "min_patient_age": 0,
    "interaction_check_enabled": True,
    "allergy_check_enabled": True,
    "age_check_enabled": True
}

# Pharmacy Agent
PHARMACY_CONFIG = {
    "max_search_radius_km": 25,  # Maximum delivery distance
    "max_results": 10,  # Maximum pharmacies to return
    "default_delivery_time_minutes": 45,
    "speed_kmph": 30,  # Assumed delivery speed for ETA calculation
    "base_delivery_fee": 25  # Base delivery charge in rupees
}

# Doctor Agent
DOCTOR_CONFIG = {
    "max_doctors_to_show": 5,
    "slot_duration_minutes": 30,
    "default_consultation_fee": 500
}


# ============= MEDICAL THRESHOLDS =============

# SpO2 (Oxygen Saturation) Levels
SPO2_THRESHOLDS = {
    "critical": 90,    # Below this = emergency
    "warning": 92,     # Below this = immediate care
    "moderate": 95,    # Below this = monitor closely
    "normal": 95       # Above this = normal
}

# Severity Classification
SEVERITY_RULES = {
    "severe": {
        "spo2_max": 90,
        "keywords": ["severe", "acute", "critical", "emergency", "unconscious"],
        "conditions_threshold": 0.7  # Sum of serious conditions
    },
    "moderate": {
        "spo2_max": 94,
        "keywords": ["persistent", "worsening", "high fever", "difficulty"],
        "conditions_threshold": 0.5
    },
    "mild": {
        "default": True
    }
}

# Red Flag Keywords (require immediate medical attention)
RED_FLAG_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "breathing difficulty",
    "confusion",
    "disorientation",
    "unconscious",
    "unresponsive",
    "severe pain",
    "coughing blood",
    "blood in stool",
    "severe headache",
    "seizure"
]

# Conditions requiring prescription (not OTC-treatable)
PRESCRIPTION_REQUIRED_CONDITIONS = [
    "tb_suspect",
    "severe_pneumonia",
    "acute_bronchitis"
]


# ============= DRUG INTERACTION LEVELS =============

INTERACTION_SEVERITY = {
    "mild": {
        "emoji": "⚠️",
        "action": "Monitor for side effects"
    },
    "moderate": {
        "emoji": "⚠️⚠️",
        "action": "Consult pharmacist before use"
    },
    "high": {
        "emoji": "🚨",
        "action": "Consult doctor before use"
    },
    "severe": {
        "emoji": "🚨🚨",
        "action": "DO NOT COMBINE - Seek medical advice"
    }
}


# ============= SYSTEM SETTINGS =============

# Logging
LOGGING_CONFIG = {
    "enabled": True,
    "log_to_file": True,
    "log_to_console": True,
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "max_log_size_mb": 10,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# API/Performance
SYSTEM_CONFIG = {
    "max_processing_time_seconds": 30,
    "enable_caching": False,
    "timeout_seconds": 60,
    "max_retries": 3
}

# Upload constraints
UPLOAD_CONFIG = {
    "max_file_size_mb": 10,
    "allowed_image_formats": [".png", ".jpg", ".jpeg"],
    "allowed_document_formats": [".pdf", ".txt"],
    "upload_folder": str(UPLOADS_DIR),
    "cleanup_after_hours": 24  # Delete uploads after this time
}


# ============= UI/UX SETTINGS =============

# Streamlit configuration
UI_CONFIG = {
    "title": "Multi-Agent Healthcare Assistant",
    "page_icon": "🏥",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "theme": {
        "primaryColor": "#FF4B4B",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730"
    }
}

# Disclaimer text
DISCLAIMER_TEXT = """
⚠️ **IMPORTANT DISCLAIMER**

This is an **EDUCATIONAL DEMONSTRATION ONLY** and is **NOT MEDICAL ADVICE**.

- This system does NOT provide medical diagnoses
- Recommendations are simulated and for demonstration purposes only
- Always consult qualified healthcare professionals for medical concerns
- In case of emergency, call emergency services immediately (911/108)
- Do not use this system for real medical decision-making

By using this system, you acknowledge this is a proof-of-concept demonstration.
"""

# Safety warnings for UI
SAFETY_WARNINGS = {
    "critical": "🚨 CRITICAL: Seek emergency medical care immediately",
    "warning": "⚠️ WARNING: Medical consultation recommended within 24 hours",
    "info": "ℹ️ INFO: Monitor symptoms and consult doctor if condition worsens",
    "success": "✅ Mild condition - OTC treatment may be appropriate"
}


# ============= CONDITION MAPPINGS =============

# Map conditions to symptoms/indications
CONDITION_TO_INDICATION = {
    "normal": [],
    "pneumonia": ["cough", "fever", "pain", "chest congestion"],
    "covid_suspect": ["fever", "cough", "pain", "fatigue"],
    "bronchitis": ["cough", "chest congestion", "wheezing"],
    "tb_suspect": ["cough", "fever", "night sweats", "weight loss"]
}

# Specialty mapping for doctor escalation
CONDITION_TO_SPECIALTY = {
    "pneumonia": "Pulmonology",
    "covid_suspect": "Internal Medicine",
    "bronchitis": "Pulmonology",
    "tb_suspect": "Pulmonology",
    "normal": "General Medicine"
}


# ============= GEOGRAPHICAL SETTINGS =============

# Default location (Mumbai, Maharashtra)
DEFAULT_LOCATION = {
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "lat": 19.0760,
    "lon": 72.8777,
    "pincode": "400001"
}

# Distance calculation settings
GEO_CONFIG = {
    "unit": "km",  # kilometers
    "earth_radius_km": 6371,
    "max_delivery_radius": 25,
    "default_delivery_speed_kmph": 30
}


# ============= DOSAGE REFERENCE DATABASE =============

# Standard OTC dosages (simplified reference)
DOSAGE_DATABASE = {
    "Paracetamol": {
        "adult_dose": "500-650 mg",
        "frequency": "Every 6-8 hours",
        "max_daily": "3000 mg",
        "warnings": ["Do not exceed max dose", "Avoid alcohol"]
    },
    "Ibuprofen": {
        "adult_dose": "200-400 mg",
        "frequency": "Every 6-8 hours",
        "max_daily": "1200 mg",
        "warnings": ["Take with food", "Avoid if kidney disease"]
    },
    "Cetirizine": {
        "adult_dose": "10 mg",
        "frequency": "Once daily",
        "max_daily": "10 mg",
        "warnings": ["May cause drowsiness"]
    },
    "Omeprazole": {
        "adult_dose": "20 mg",
        "frequency": "Once daily before breakfast",
        "max_daily": "20 mg",
        "warnings": ["Take on empty stomach"]
    }
}


# ============= VALIDATION SCHEMAS =============

# Expected input/output schemas for validation
AGENT_SCHEMAS = {
    "ingestion_output": {
        "required": ["patient", "xray_path"],
        "optional": ["notes", "spo2"]
    },
    "imaging_output": {
        "required": ["condition_probs", "severity_hint", "confidence"],
        "optional": ["red_flags", "recommendations"]
    },
    "therapy_output": {
        "required": ["otc_options", "escalate_to_doctor"],
        "optional": ["interaction_warnings", "safety_advice"]
    },
    "pharmacy_output": {
        "required": ["pharmacy_id", "items", "eta_min", "delivery_fee"],
        "optional": ["pharmacy_name", "distance_km"]
    }
}


# ============= MOCK ORDER SETTINGS =============

ORDER_CONFIG = {
    "order_id_prefix": "ORD",
    "order_id_length": 8,
    "estimated_delivery_buffer_minutes": 15,  # Add buffer to ETA
    "payment_methods": ["COD", "UPI", "Card"],
    "default_payment_method": "COD"
}


# ============= DEVELOPMENT/DEBUG SETTINGS =============

DEBUG_CONFIG = {
    "debug_mode": False,  # Set to True for verbose logging
    "mock_data_enabled": True,  # Use mock data if real data unavailable
    "skip_validation": False,  # Skip validation (only for testing)
    "log_api_calls": True,
    "save_intermediate_results": True  # Save agent outputs for debugging
}


# ============= HELPER FUNCTIONS =============

def get_data_file_path(filename: str) -> Path:
    """Get full path for a data file."""
    return DATA_DIR / filename


def ensure_directories_exist():
    """Ensure all required directories exist."""
    for directory in [DATA_DIR, UPLOADS_DIR, LOGS_DIR, MODELS_DIR]:
        directory.mkdir(exist_ok=True)


def validate_configuration():
    """Validate configuration settings."""
    errors = []
    
    # Check if data files exist
    required_files = [
        PHARMACIES_FILE,
        INVENTORY_FILE,
        DOCTORS_FILE,
        MEDS_FILE,
        INTERACTIONS_FILE,
        ZIPCODES_FILE
    ]
    
    for file_path in required_files:
        if not file_path.exists():
            errors.append(f"Missing required data file: {file_path}")
    
    # Check thresholds are valid
    if SPO2_THRESHOLDS["critical"] >= SPO2_THRESHOLDS["normal"]:
        errors.append("Invalid SpO2 threshold configuration")
    
    if errors:
        print("⚠️ Configuration Warnings:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def get_config_summary() -> dict:
    """Get summary of current configuration."""
    return {
        "project_root": str(BASE_DIR),
        "data_directory": str(DATA_DIR),
        "uploads_directory": str(UPLOADS_DIR),
        "logs_directory": str(LOGS_DIR),
        "debug_mode": DEBUG_CONFIG["debug_mode"],
        "confidence_threshold": IMAGING_CONFIG["confidence_threshold"],
        "max_delivery_radius_km": PHARMACY_CONFIG["max_search_radius_km"]
    }


# ============= INITIALIZATION =============

# Ensure directories exist on import
ensure_directories_exist()

# Validate configuration (optional - comment out if causing issues)
if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURATION VALIDATION")
    print("=" * 60)
    
    print("\n📁 Directory Structure:")
    print(f"  Base: {BASE_DIR}")
    print(f"  Data: {DATA_DIR}")
    print(f"  Uploads: {UPLOADS_DIR}")
    print(f"  Logs: {LOGS_DIR}")
    
    print("\n⚙️ System Settings:")
    summary = get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Validating configuration...")
    is_valid = validate_configuration()
    
    if is_valid:
        print("\n✅ Configuration is valid and ready")
    else:
        print("\n⚠️ Configuration has warnings (see above)")
    
    print("=" * 60)