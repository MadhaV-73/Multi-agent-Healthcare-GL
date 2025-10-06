# 🏥 Multi-Agent Healthcare Platform

A comprehensive healthcare platform with AI-powered diagnostics, patient analysis, and therapy recommendations.

## 🌟 Features

- **Patient Analysis**: Comprehensive patient data collection and medical document processing
- **AI Diagnostics**: Advanced X-ray analysis and intelligent therapy recommendations
- **Smart Matching**: Pharmacy inventory matching and doctor consultation services
- **Document Processing**: Multi-file upload support with OCR and PII masking
- **API Integration**: Full REST API backend with FastAPI

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ Backend API (FastAPI) ←→ AI Agents
     Port 8501              Port 8000
```

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)

Simply double-click `start.bat` to start both frontend and backend servers.

### Option 2: Manual Start

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Start Backend API
```bash
# Terminal 1
python api/main.py
```
Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

#### 3. Start Frontend
```bash
# Terminal 2
python -m streamlit run app.py
```
Frontend will be available at: http://localhost:8501

## 📡 API Endpoints

### Health Check
```
GET http://localhost:8000/api/v1/health
```

### Submit Patient Analysis
```
POST http://localhost:8000/api/v1/patient/analysis
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "birth_date": "1990-01-01",
  "gender": "Male",
  "address": "123 Main St",
  "zip_code": "12345",
  ...
}
```

### Get Patient Info
```
GET http://localhost:8000/api/v1/patient/{patient_id}
```

### X-Ray Analysis
```
POST http://localhost:8000/api/v1/xray/analyze
Content-Type: multipart/form-data
file: [X-ray image file]
```

### Therapy Recommendations
```
GET http://localhost:8000/api/v1/therapy/recommendations/{patient_id}
```

## 📁 Project Structure

```
multi-agent-healthcare/
├── api/                        # Backend API
│   ├── main.py                # FastAPI application
│   ├── routes.py              # API routes
│   ├── schema.py              # Pydantic models
│   └── dependencies.py        # Auth & dependencies
├── agents/                     # AI Agents
│   ├── base_agent.py
│   ├── ingestion_agent.py
│   ├── imaging_agent.py
│   ├── therapy_agent.py
│   ├── pharmacy_agent.py
│   └── doctor_agent.py
├── utils/                      # Utilities
│   ├── api_client.py          # API client for frontend
│   ├── validators.py
│   └── logger.py
├── data/                       # Data files
├── uploads/                    # Uploaded files
├── app.py                      # Streamlit frontend
├── start.bat                   # Startup script
└── requirements.txt            # Dependencies
```

## 🔧 Configuration

Backend API URL can be configured in `utils/api_client.py`:
```python
api_client = HealthCareAPIClient(base_url="http://localhost:8000")
```

## 🧪 Testing with Postman

1. Import the API endpoints from http://localhost:8000/docs
2. Use the following payload for patient submission:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "birth_date": "1990-01-01",
  "gender": "Male",
  "address": "123 Main St, City, State",
  "zip_code": "12345",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567891",
  "emergency_contact_relation": "Spouse",
  "allergies": "Penicillin",
  "current_medications": "Aspirin 100mg daily",
  "medical_conditions": "Hypertension",
  "symptoms": "Headache, fatigue",
  "xray_analysis_enabled": true,
  "ocr_enabled": true,
  "pii_masking_enabled": true,
  "analysis_priority": "Standard"
}
```

## 📊 Frontend Features

### Home Page
- Platform statistics dashboard
- API connection status
- Feature overview

### Patient Analysis
- Comprehensive patient form
- Multi-file document upload
- Real-time API integration
- Progress tracking

### X-Ray Analysis
- AI-powered image classification
- Confidence scores
- Detailed findings

### Therapy Recommendations
- Personalized medication suggestions
- Nearby pharmacy matching
- Treatment notes

## 🔐 Security Features

- PII Masking
- Document validation
- Secure file uploads
- API authentication ready

## 🐛 Troubleshooting

### Backend not connecting?
1. Make sure the API server is running: `python api/main.py`
2. Check if port 8000 is available
3. Verify API status in the frontend sidebar

### Frontend issues?
1. Clear browser cache
2. Restart Streamlit: `python -m streamlit run app.py`
3. Check console for errors

## 📝 License

This project is part of a multi-agent healthcare system demonstration.

## 👥 Contributors

Healthcare AI Team

## 🔗 Links

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501
