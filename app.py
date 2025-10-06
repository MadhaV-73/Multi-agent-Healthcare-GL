import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.api_client import HealthCareAPIClient

# Initialize API Client
api_client = HealthCareAPIClient(base_url="http://localhost:8000")

def init_session_state():
    """Initialize session state variables"""
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'patient_id' not in st.session_state:
        st.session_state.patient_id = None
    if 'api_status' not in st.session_state:
        st.session_state.api_status = "checking"

def home_page():
    """Professional home page"""
    # Hero Section
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 3rem 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin-bottom: 1rem;">
            🏥 HealthCare AI Platform
        </h1>
        <p style="color: white; text-align: center; font-size: 1.2rem; margin-bottom: 0;">
            Advanced Multi-Agent System for Comprehensive Healthcare Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <h3 style="color: #2c3e50;">📋 Patient Analysis</h3>
            <p>Comprehensive patient data collection and medical document processing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <h3 style="color: #2c3e50;">🔬 AI Diagnostics</h3>
            <p>Advanced X-ray analysis and intelligent therapy recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <h3 style="color: #2c3e50;">💊 Smart Matching</h3>
            <p>Pharmacy inventory matching and doctor consultation services</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistics Dashboard
    st.subheader("📊 Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Patients Analyzed", "1,234", "12%")
    with col2:
        st.metric("Documents Processed", "5,678", "8%")
    with col3:
        st.metric("X-rays Classified", "890", "15%")
    with col4:
        st.metric("Pharmacy Partners", "156", "3%")
    
    # API Status Check
    st.markdown("---")
    st.subheader("🔌 Backend API Status")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Check API Status"):
            with st.spinner("Checking API..."):
                health = api_client.health_check()
                if health.get("status") == "healthy":
                    st.success("✅ API is running!")
                    st.session_state.api_status = "healthy"
                else:
                    st.error(f"❌ API Error: {health.get('message', 'Unknown error')}")
                    st.session_state.api_status = "error"
    with col2:
        if st.session_state.api_status == "healthy":
            st.success("🟢 Backend API is healthy and running")
        elif st.session_state.api_status == "error":
            st.error("🔴 Backend API is not responding. Please start the server.")
        else:
            st.info("⚪ Click 'Check API Status' to verify backend connection")

def patient_analysis_page():
    """Patient analysis form with document upload"""
    st.markdown("""
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
        <h2 style="color: #1976d2; margin-bottom: 0.5rem;">👤 Patient Analysis & Document Processing</h2>
        <p style="color: #424242; margin: 0;">Complete the patient information form and upload relevant medical documents for comprehensive analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Patient Information Form
    with st.container():
        st.subheader("📝 Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="Enter first name")
            email = st.text_input("Email Address *", placeholder="patient@example.com")
            birth_date = st.date_input("Date of Birth *", max_value=date.today())
            address = st.text_area("Address *", placeholder="Street address, City, State")
            
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Enter last name")
            phone = st.text_input("Phone Number *", placeholder="+1 (555) 123-4567")
            gender = st.selectbox("Gender *", ["Select", "Male", "Female", "Other", "Prefer not to say"])
            zip_code = st.text_input("ZIP Code *", placeholder="12345")
        
        # Emergency Contact
        st.markdown("### 🚨 Emergency Contact")
        col1, col2 = st.columns(2)
        with col1:
            emergency_name = st.text_input("Emergency Contact Name", placeholder="Contact person name")
            emergency_phone = st.text_input("Emergency Contact Phone", placeholder="+1 (555) 123-4567")
        with col2:
            emergency_relation = st.text_input("Relationship", placeholder="Spouse, Parent, Sibling, etc.")
        
        # Medical History
        st.markdown("### 🩺 Medical Information")
        col1, col2 = st.columns(2)
        with col1:
            allergies = st.text_area("Known Allergies", placeholder="List any known allergies...")
            current_medications = st.text_area("Current Medications", placeholder="List current medications...")
        with col2:
            medical_conditions = st.text_area("Medical Conditions", placeholder="List any existing medical conditions...")
            symptoms = st.text_area("Current Symptoms", placeholder="Describe current symptoms...")
    
    st.markdown("---")
    
    # Document Upload Section
    with st.container():
        st.subheader("📎 Medical Document Upload")
        st.markdown("""
        <div style="background: #fff3e0; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
            <strong>📋 Supported Formats:</strong> PDF, PNG, JPG, JPEG<br>
            <strong>📏 Max Size:</strong> 10MB per file<br>
            <strong>📚 Multiple Files:</strong> You can upload multiple documents
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload Medical Documents",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload X-rays, lab reports, prescriptions, or other medical documents"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display uploaded files
            st.markdown("### 📁 Uploaded Files")
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.getvalue()) / 1024 / 1024  # Size in MB
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {file.name}")
                with col2:
                    st.write(f"{file_size:.2f} MB")
                with col3:
                    st.write(f"✅ {file.type}")
    
    st.markdown("---")
    
    # Analysis Options
    with st.container():
        st.subheader("🔬 Analysis Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            enable_xray = st.checkbox("🩻 X-Ray Analysis", help="Enable AI-powered X-ray classification")
        with col2:
            enable_ocr = st.checkbox("📖 Document OCR", help="Extract text from uploaded documents", value=True)
        with col3:
            enable_pii = st.checkbox("🔒 PII Masking", help="Mask personally identifiable information", value=True)
        
        analysis_priority = st.selectbox("Analysis Priority", ["Standard", "Urgent", "Emergency"])
    
    # Submit Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            # Validate required fields
            required_fields = [first_name, last_name, email, phone, birth_date, address, zip_code, gender]
            if all(required_fields) and gender != "Select":
                # Prepare patient data
                patient_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'birth_date': str(birth_date),
                    'gender': gender,
                    'address': address,
                    'zip_code': zip_code,
                    'emergency_contact_name': emergency_name,
                    'emergency_contact_phone': emergency_phone,
                    'emergency_contact_relation': emergency_relation,
                    'allergies': allergies,
                    'current_medications': current_medications,
                    'medical_conditions': medical_conditions,
                    'symptoms': symptoms,
                    'xray_analysis_enabled': enable_xray,
                    'ocr_enabled': enable_ocr,
                    'pii_masking_enabled': enable_pii,
                    'analysis_priority': analysis_priority
                }
                
                # Show loading spinner
                with st.spinner("🔄 Submitting data to backend..."):
                    # Submit to backend API
                    response = api_client.submit_patient_analysis(
                        patient_data=patient_data,
                        files=uploaded_files if uploaded_files else None
                    )
                
                # Handle response
                if response.get("status") == "success":
                    st.session_state.patient_data = patient_data
                    st.session_state.patient_id = response.get("patient_id")
                    st.session_state.uploaded_files = uploaded_files if uploaded_files else []
                    
                    st.success(f"✅ Patient data submitted successfully! Patient ID: {response.get('patient_id')}")
                    st.balloons()
                    
                    # Show response details
                    with st.expander("📋 Submission Details"):
                        st.json(response)
                    
                    # Show next steps
                    st.info("🔄 **Next Steps:**\n1. Documents are being processed\n2. AI agents are analyzing the data\n3. Results will be available in the Dashboard")
                else:
                    st.error(f"❌ Error submitting data: {response.get('message', 'Unknown error')}")
                    st.warning("💡 Make sure the backend API server is running on http://localhost:8000")
            else:
                st.error("❌ Please fill in all required fields marked with *")

def documents_page():
    """Enhanced document management page"""
    st.subheader("📁 Document Management")
    
    if st.session_state.uploaded_files:
        st.write(f"**Total Documents:** {len(st.session_state.uploaded_files)}")
        
        for i, file in enumerate(st.session_state.uploaded_files):
            with st.expander(f"📄 {file.name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {file.type}")
                    st.write(f"**Size:** {len(file.getvalue()) / 1024:.2f} KB")
                with col2:
                    if st.button(f"🔍 Analyze", key=f"analyze_{i}"):
                        st.info("Analysis started for this document!")
    else:
        st.info("No documents uploaded yet. Go to Patient Analysis to upload documents.")

def xray_analysis_page():
    """X-Ray analysis page"""
    st.subheader("🩻 X-Ray Analysis")
    
    st.markdown("""
    <div style="background: #f3e5f5; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4 style="color: #6a1b9a; margin-bottom: 0.5rem;">AI-Powered X-Ray Classification</h4>
        <p style="margin: 0;">Upload chest X-rays for automated analysis and classification</p>
    </div>
    """, unsafe_allow_html=True)
    
    xray_file = st.file_uploader("Upload X-Ray Image", type=['png', 'jpg', 'jpeg'])
    
    if xray_file:
        col1, col2 = st.columns(2)
        with col1:
            st.image(xray_file, caption="Uploaded X-Ray", width=300)
        with col2:
            if st.button("🔬 Analyze X-Ray"):
                with st.spinner("🔄 Analyzing X-Ray via API..."):
                    # Call backend API
                    result = api_client.get_xray_analysis(xray_file)
                
                if result.get("status") == "success":
                    st.success("✅ Analysis Complete!")
                    analysis = result.get("analysis", {})
                    st.write(f"**Classification:** {analysis.get('classification', 'N/A')}")
                    st.write(f"**Confidence:** {analysis.get('confidence', 'N/A')}")
                    st.write(f"**Findings:** {analysis.get('findings', 'N/A')}")
                    st.write(f"**Recommendations:** {analysis.get('recommendations', 'N/A')}")
                    
                    with st.expander("📊 Full Analysis Report"):
                        st.json(result)
                else:
                    st.error(f"❌ Error: {result.get('message', 'Analysis failed')}")
                    st.warning("💡 Make sure the backend API is running")

def therapy_page():
    """Therapy recommendations page"""
    st.subheader("💊 Therapy Recommendations")
    
    st.markdown("""
    <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4 style="color: #2e7d2e; margin-bottom: 0.5rem;">Personalized Treatment Suggestions</h4>
        <p style="margin: 0;">Get AI-powered therapy and medication recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_data and st.session_state.patient_id:
        st.write("**Patient:** " + st.session_state.patient_data.get('first_name', '') + " " + st.session_state.patient_data.get('last_name', ''))
        st.write(f"**Patient ID:** {st.session_state.patient_id}")
        
        if st.button("🧠 Generate Recommendations"):
            with st.spinner("🔄 Generating personalized recommendations via API..."):
                # Call backend API
                result = api_client.get_therapy_recommendations(st.session_state.patient_id)
                
                if result.get("status") == "success":
                    st.success("✅ Recommendations Generated!")
                    
                    recommendations = result.get("recommendations", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 💊 Suggested Medications")
                        medications = recommendations.get("medications", [])
                        if medications:
                            for med in medications:
                                st.write(f"• **{med.get('name')}** - {med.get('dosage')}")
                                st.caption(f"  {med.get('instructions')}")
                        else:
                            st.info("No specific medications recommended")
                    
                    with col2:
                        st.markdown("### 🏥 Nearby Pharmacies")
                        pharmacies = recommendations.get("nearby_pharmacies", [])
                        if pharmacies:
                            for pharmacy in pharmacies:
                                st.write(f"📍 **{pharmacy.get('name')}** - {pharmacy.get('distance')}")
                                st.caption(f"  {pharmacy.get('address')}")
                        else:
                            st.info("No pharmacies found")
                    
                    # Additional info
                    if recommendations.get("notes"):
                        st.markdown("### 📝 Additional Notes")
                        st.info(recommendations.get("notes"))
                    
                    with st.expander("� Full Recommendation Report"):
                        st.json(result)
                else:
                    st.error(f"❌ Error: {result.get('message', 'Failed to generate recommendations')}")
                    st.warning("💡 Make sure the backend API is running")
    else:
        st.info("Complete patient analysis first to get personalized recommendations.")

def main():
    st.set_page_config(
        page_title="HealthCare AI Platform",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: bold;
        }
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🏥 Navigation")
        page = st.radio(
            "Select Page:",
            ["🏠 Home", "👤 Patient Analysis", "📁 Documents", "🩻 X-Ray Analysis", "💊 Therapy Recommendations"],
            index=0
        )
        
        st.markdown("---")
        
        # API Connection Status
        st.markdown("### 🔌 API Connection")
        health = api_client.health_check()
        if health.get("status") == "healthy":
            st.success("🟢 Backend Connected")
        else:
            st.error("🔴 Backend Offline")
            with st.expander("ℹ️ How to start backend?"):
                st.code("cd multi-agent-healthcare\npython api/main.py", language="bash")
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        if st.session_state.patient_data:
            st.success("✅ Patient Data: Complete")
            if st.session_state.patient_id:
                st.info(f"🆔 Patient ID: {st.session_state.patient_id}")
        else:
            st.warning("⏳ Patient Data: Pending")
            
        if st.session_state.uploaded_files:
            st.success(f"✅ Documents: {len(st.session_state.uploaded_files)}")
        else:
            st.info("📁 Documents: None")
    
    # Page Routing
    if page == "🏠 Home":
        home_page()
    elif page == "👤 Patient Analysis":
        patient_analysis_page()
    elif page == "📁 Documents":
        documents_page()
    elif page == "🩻 X-Ray Analysis":
        xray_analysis_page()
    elif page == "💊 Therapy Recommendations":
        therapy_page()

if __name__ == "__main__":
    main()
