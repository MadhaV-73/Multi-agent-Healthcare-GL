# 🏥 Multi-Agent Healthcare Platform

Try the demo at - https://multi-agent-healthcare-gl-6yahxkauhougvktyzhjwim.streamlit.app/

A comprehensive healthcare platform with AI-powered diagnostics, patient analysis, and therapy recommendations built using a multi-agent architecture.

## 🌟 Key Features

- **🩺 Patient Analysis**: Comprehensive patient data collection and medical document processing
- **🔬 AI Diagnostics**: Advanced X-ray analysis and intelligent therapy recommendations
- **💊 Smart Pharmacy Matching**: Location-aware pharmacy inventory matching with real-time availability
- **👨‍⚕️ Doctor Consultation**: Specialist matching and appointment scheduling
- **📄 Document Processing**: Multi-file upload support with OCR and PII masking
- **🔍 Observability**: Agent-by-agent event logs and reservation tracing
- **🚀 REST API**: Full FastAPI backend with automatic documentation

## 📍 Sample Data Coverage

The system ships with comprehensive sample data for **Mumbai Metropolitan Region**:

### Cities Covered (159 Pincodes Total):
- **Mumbai**: 30 pincodes (400001-400030) → 78 pharmacies in 25km
- **Navi Mumbai**: 15 pincodes (400701-400715) → 130 pharmacies in 25km
- **Thane**: 15 pincodes (400601-400615) → 142 pharmacies in 25km
- **Kalyan**: 10 pincodes (421301-421310) → 95+ pharmacies in 25km
- **Panvel**: 10 pincodes (410206-410215) → 120+ pharmacies in 25km
- **Vasai**: 10 pincodes (401201-401210) → 85+ pharmacies in 25km
- **Bhiwandi**: 7 pincodes (421302-421308) → 110+ pharmacies in 25km
- **Mira Road**: 6 pincodes (401107-401112) → 95+ pharmacies in 25km
- **Virar**: 6 pincodes (401303-401308) → 70+ pharmacies in 25km
- **Ahmedabad**: 50 pincodes (380001-380050) → Fallback to Mumbai region

### Dataset Details:
- **Total Pharmacies**: 1500 across Mumbai metropolitan region
- **Inventory Records**: 1500 with 30 OTC medicines
- **Doctors**: 20 specialists across various fields
- **Coverage**: 89% of pharmacies have pincodes within 25km radius

**All cities in the dropdown will work with the pharmacy matching system!**

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ Backend API (FastAPI) ←→ AI Agents
     Port 8501              Port 8000
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Installation & Setup

#### 1️⃣ Clone or Download the Repository
```powershell
git clone https://github.com/parth3083/multi-agent-healthcare.git
cd multi-agent-healthcare
```

#### 2️⃣ Create Virtual Environment
```powershell
python -m venv .venv
```

#### 3️⃣ Activate Virtual Environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.\.venv\Scripts\activate.bat
```

#### 4️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 5️⃣ Verify Data Files
Ensure the following data files exist in the `data/` directory:
- `pharmacies.json`
- `inventory.csv`
- `doctors.csv`
- `meds.csv`
- `interactions.csv`
- `zipcodes.csv`

### Running the Application

#### Option 1: Quick Start (Recommended) 🎯
Simply double-click `start_integrated.bat` or run:
```powershell
.\start_integrated.bat
```
This will launch both the API backend and Streamlit UI automatically!

#### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend API:**
```powershell
.\.venv\Scripts\Activate.ps1
python api/main.py
```
✅ Backend available at: http://localhost:8000
📚 API Docs at: http://localhost:8000/docs

**Terminal 2 - Frontend UI:**
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app_integrated.py
```
✅ Frontend available at: http://localhost:8501

### Testing the Application

#### Run All Tests
```powershell
pytest
```

#### Run Specific Tests
```powershell
# Integration tests
pytest test_integration.py -v

# End-to-end tests
pytest test_e2e.py -v

# Specific agent tests
pytest tests/test_coordinator.py -v
```

#### Test Coverage
```powershell
pytest --cov=agents --cov=api --cov=utils
```

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
├── app_integrated.py           # Streamlit frontend (agent-integrated)
├── start_integrated.bat        # Startup script launching API+UI
└── requirements.txt            # Dependencies
```

## ⚙️ Configuration

### Environment Variables (Optional)
Create a `.env` file in the root directory for custom configuration:
```env
API_HOST=localhost
API_PORT=8000
STREAMLIT_PORT=8501
DEBUG_MODE=False
```

### Configuration Files
- **`config.py`**: Central configuration for paths, thresholds, and system settings
- **`utils/api_client.py`**: API client configuration
```python
api_client = HealthCareAPIClient(base_url="http://localhost:8000")
```

### Key Settings (in `config.py`)
- **SpO2 Thresholds**: Oxygen saturation levels for severity classification
- **Pharmacy Search Radius**: Default 25km, configurable
- **Image Processing**: Max size 10MB, supported formats: PNG, JPG, JPEG
- **Delivery Speed**: Assumed 30 km/h for ETA calculations

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
- City/pincode aware matching with fallback visibility

### Therapy Recommendations
- Personalized medication suggestions
- Nearby pharmacy matching with reservation snapshot
- Treatment notes

## 🔐 Security Features

- PII Masking
- Document validation
- Secure file uploads
- API authentication ready

## 🐛 Troubleshooting

### Common Issues

#### ❌ "Port already in use"
```powershell
# Check which process is using the port
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### ❌ "Module not found" Error
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1
# Reinstall dependencies
pip install -r requirements.txt
```

#### ❌ Backend API Not Connecting
1. Verify API server is running: Check http://localhost:8000/api/v1/health
2. Check port 8000 availability
3. Review backend logs in the terminal
4. Check API status indicator in frontend sidebar

#### ❌ Frontend Issues
1. Clear browser cache and reload (Ctrl + Shift + R)
2. Restart Streamlit: `streamlit run app_integrated.py`
3. Check browser console for JavaScript errors (F12)

#### ❌ Data Files Missing
Run the data generation scripts:
```powershell
python generate_zipcodes.py
```

#### ❌ Virtual Environment Not Activating
- **PowerShell Execution Policy Issue:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Debug Mode
Enable debug mode in `config.py`:
```python
DEBUG_CONFIG = {
    "debug_mode": True,
    "log_api_calls": True
}
```

### Getting Help
- Check the [API Documentation](http://localhost:8000/docs) when server is running
- Review logs in the `logs/` directory
- Check test outputs for expected behavior patterns

## 🎯 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Document Processing**: PyPDF2, pdfplumber, Pillow
- **Testing**: Pytest
- **AI/ML**: Custom classifiers for medical imaging

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger UI)
- [Architecture Overview](docs/TARGET_ARCHITECTURE.md) - System architecture details
- [Deployment Guide](DEPLOYMENT_INSTRUCTIONS.md) - Production deployment instructions

## 🔐 Security & Privacy

⚠️ **IMPORTANT DISCLAIMERS:**
- This is an **EDUCATIONAL DEMONSTRATION ONLY**
- **NOT FOR PRODUCTION USE** or real medical decision-making
- No real patient data should be used
- All recommendations are simulated for demonstration purposes
- Always consult qualified healthcare professionals for medical concerns
- In emergencies, call emergency services immediately (911/108)

**Security Features:**
- PII masking capabilities
- Secure file upload handling
- Input validation and sanitization
- API authentication ready (to be implemented)

## 📝 License

This project is part of a multi-agent healthcare system demonstration for educational purposes.

## �‍💻 Author

**Madhav** (MadhaV-73)
- GitHub: [@MadhaV-73]([(https://github.com/MadhaV-73])

## 🤝 Contributing

This is an educational project. For suggestions or improvements:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Review the troubleshooting section above
- Check existing documentation in the `docs/` folder

## 🔗 Quick Links

- 🌐 **Backend API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs
- 🖥️ **Frontend UI**: http://localhost:8501
- 📊 **Project Repository**: https://github.com/MadhaV-73/Multi-agent-Healthcare-GL

---

**Made with ❤️ for healthcare innovation** 🏥
