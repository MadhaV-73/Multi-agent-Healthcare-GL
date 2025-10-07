"""
Enhanced Streamlit Frontend for Multi-Agent Healthcare System
Integrated with Coordinator pipeline
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# API Configuration
# Priority: Streamlit secrets > Environment variable > Default production URL
try:
    API_BASE_URL = st.secrets.get("api", {}).get("base_url", None)
except:
    API_BASE_URL = None

if not API_BASE_URL:
    API_BASE_URL = os.getenv("API_BASE_URL", "https://multi-agent-healthcare-gl-1.onrender.com")

# Remove trailing slash if present
API_BASE_URL = API_BASE_URL.rstrip("/")


@st.cache_data(show_spinner=False)
def load_zip_data() -> pd.DataFrame:
    """Load sample zipcode coverage from the data folder."""
    path = Path("data/zipcodes.csv")
    df = pd.read_csv(path)
    df["pincode"] = df["pincode"].astype(str)
    df["label"] = df["city"] + " – " + df["pincode"]
    return df.sort_values(["city", "pincode"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_medicine_reference() -> tuple[list[str], list[str], list[str]]:
    """Return medicine names, symptom tags, and allergy keywords from sample data."""
    meds_path = Path("data/meds.csv")
    meds_df = pd.read_csv(meds_path)

    med_names = sorted(meds_df["drug_name"].dropna().unique().tolist())

    symptom_tokens: set[str] = set()
    for entry in meds_df["indication"].dropna():
        for token in str(entry).split():
            clean = token.strip().lower()
            if clean:
                symptom_tokens.add(clean)

    allergy_tokens: set[str] = set()
    for entry in meds_df["contra_allergy_keywords"].dropna():
        for token in str(entry).split():
            clean = token.strip().lower()
            if clean and clean != "none":
                allergy_tokens.add(clean)

    return med_names, sorted(symptom_tokens), sorted(allergy_tokens)

def check_api_status():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
        return response.status_code == 200, response.json()
    except:
        return False, None

def init_session_state():
    """Initialize session state variables"""
    if 'patient_id' not in st.session_state:
        st.session_state.patient_id = None
    if 'patient_name' not in st.session_state:
        st.session_state.patient_name = None
    if 'analysis_id' not in st.session_state:
        st.session_state.analysis_id = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

def home_page():
    """Homepage with overview"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🏥 Multi-Agent Healthcare Assistant</h1>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">AI-Powered Healthcare Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API status
    api_status, api_info = check_api_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h2 style="color: #1976d2; margin: 0;">🤖 6 Agents</h2>
            <p style="margin: 0.5rem 0 0 0;">Collaborative AI System</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_color = "#4caf50" if api_status else "#f44336"
        status_text = "Online" if api_status else "Offline"
        st.markdown(f"""
        <div style="background: {status_color}20; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h2 style="color: {status_color}; margin: 0;">🌐 API {status_text}</h2>
            <p style="margin: 0.5rem 0 0 0;">Backend Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #fff3e0; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h2 style="color: #ff9800; margin: 0;">🩻 AI Analysis</h2>
            <p style="margin: 0.5rem 0 0 0;">X-ray Classification</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Overview
    st.markdown("### 🎯 System Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🤖 Multi-Agent Pipeline:**
        - 📥 **Ingestion Agent** - File validation & preprocessing
        - 🩻 **Imaging Agent** - X-ray classification (Normal/COVID/Pneumonia)
        - 💊 **Therapy Agent** - OTC medicine recommendations
        - 🏥 **Pharmacy Agent** - Location-based matching
        - 👨‍⚕️ **Doctor Agent** - Escalation for severe cases
        - 🎯 **Coordinator** - Orchestrates entire pipeline
        """)
    
    with col2:
        st.markdown("""
        **✨ Key Features:**
        - Real-time X-ray analysis
        - Drug interaction checking
        - Pharmacy inventory matching
        - Distance-based recommendations
        - Doctor booking for escalations
        - PII masking for privacy
        - OCR for medical documents
        """)
    
    if api_status and api_info:
        with st.expander("🔍 API Details"):
            st.json(api_info)
    else:
        st.warning("⚠️ **Backend API is not running!** Please start it with: `python api/main.py`")
    
    # Quick start guide
    st.markdown("---")
    st.markdown("### 🚀 Quick Start Guide")
    st.markdown("""
    1. **Upload X-Ray** - Go to 🩻 X-Ray Analysis page
    2. **Enter Symptoms** - Describe patient symptoms
    3. **Get Results** - Receive AI-powered analysis
    4. **View Recommendations** - See medicines and pharmacies
    5. **Book Doctor** - If escalation needed
    """)


def patient_intake_page():
    """Simplified patient intake aligned with assignment contract."""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">📝 Patient Intake</h2>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">Use sample master data to register a patient in one step.</p>
    </div>
    """, unsafe_allow_html=True)

    zip_df = load_zip_data()
    med_names, symptom_tags, allergy_tags = load_medicine_reference()

    city_options = zip_df["city"].unique().tolist()
    symptom_display = {tag.replace("_", " ").title(): tag for tag in symptom_tags}
    allergy_display = {tag.replace("_", " ").title(): tag for tag in allergy_tags}

    with st.form("patient_intake_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            name = st.text_input("Patient Name", value="John Doe")
            birth_date = st.date_input(
                "Date of Birth",
                value=datetime(1985, 1, 1).date(),
                max_value=datetime.now().date(),
            )
            gender = st.selectbox("Gender", ["M", "F", "U"], help="M = Male, F = Female, U = Unspecified")

        with col2:
            selected_city = st.selectbox("City", city_options)
            city_pin_df = zip_df[zip_df["city"] == selected_city]
            pincode = st.selectbox(
                "Pincode",
                city_pin_df["pincode"].tolist(),
                help="Loaded from sample zipcode coverage",
            )

        symptom_labels = list(symptom_display.keys())
        default_symptoms = symptom_labels[:1] if symptom_labels else []
        selected_symptoms = st.multiselect(
            "Common Symptoms",
            symptom_labels,
            default=default_symptoms,
        )
        selected_allergies = st.multiselect(
            "Known Allergies",
            list(allergy_display.keys()),
            help="Powered by contraindication tags from sample medicines",
        )

        submitted = st.form_submit_button("Register Patient", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Patient name is required.")
            return

        payload = {
            "name": name.strip(),
            "birth_date": birth_date.isoformat(),
            "gender": gender,
            "city": selected_city,
            "zip_code": pincode,
            "symptoms": ", ".join(selected_symptoms) if selected_symptoms else "",
            "allergies": ", ".join(selected_allergies) if selected_allergies else "",
        }

        try:
            response = requests.post(f"{API_BASE_URL}/api/v1/patient/simple", json=payload, timeout=10)
        except requests.exceptions.RequestException as exc:
            st.error(f"Unable to reach backend API: {exc}")
            return

        if response.status_code == 200:
            data = response.json()
            st.session_state.patient_id = data.get("patient_id")
            st.session_state.patient_name = name.strip()
            st.success(data.get("message", "Patient registered successfully."))
            st.info(data.get("next_step", "Proceed to X-ray analysis."))
        else:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            st.error(f"Registration failed: {detail}")
def xray_analysis_page():
    """Enhanced X-Ray analysis page with full pipeline integration"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100 %); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">🩻 X-Ray Analysis & Treatment Recommendations</h2>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">Upload chest X-ray for complete multi-agent analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("⚠️ Educational demo only — this workflow does not provide medical advice or diagnoses. Call emergency services immediately if someone is in distress.")
    st.caption("Pipeline steps: 1) Ingestion → 2) Imaging → 3) Therapy → 4) Pharmacy/Doctor → 5) Mock order receipt")

    zip_df = load_zip_data()
    med_names, symptom_tags, allergy_tags = load_medicine_reference()
    symptom_display = {tag.replace("_", " ").title(): tag for tag in symptom_tags}
    allergy_display = {tag.replace("_", " ").title(): tag for tag in allergy_tags}
    
    # Check API status
    api_status, _ = check_api_status()
    if not api_status:
        st.error("❌ **Backend API is offline!** Please start it first: `python api/main.py`")
        return
    
    # Input form
    with st.form("xray_form"):
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📋 Patient Snapshot")
            age = st.number_input("Age", min_value=1, max_value=120, value=40, help="Required for dosage safety checks")
            gender = st.selectbox("Gender", ["M", "F", "U"], help="Used for anonymised patient context")
            selected_city = st.selectbox("City", zip_df["city"].unique().tolist(), help="Loaded from sample zipcode coverage")
            city_subset = zip_df[zip_df["city"] == selected_city]
            zip_code = st.selectbox(
                "ZIP / PIN Code",
                city_subset["pincode"].tolist(),
                help="Helps the pharmacy matcher estimate delivery ETA",
            )
            selected_meds = st.multiselect(
                "Current Medications",
                med_names,
                help="Choose from sample OTC catalog",
            )
            custom_med_entry = st.text_input("Add another medication", placeholder="Comma separated if multiple")

        with col2:
            st.markdown("#### 🩺 Presenting Symptoms")
            symptom_choices = list(symptom_display.keys())
            default_symptoms = symptom_choices[:2] if symptom_choices else []
            selected_symptoms = st.multiselect(
                "Primary symptoms",
                symptom_choices,
                default=default_symptoms,
                help="Tags derived from sample medicine indications",
            )
            symptom_notes = st.text_area(
                "Additional notes / history",
                placeholder="Optional clinical summary, vitals, lab findings",
                height=110,
            )
            spo2 = st.slider("SpO2 (%)", min_value=80, max_value=100, value=98)
            allergy_choices = list(allergy_display.keys())
            selected_allergies = st.multiselect(
                "Medication allergies",
                allergy_choices,
                help="Known sensitizers from sample OTC catalog",
            )
            custom_allergy_entry = st.text_input("Add another allergy", placeholder="Comma separated if multiple")

        st.markdown("---")
        st.markdown("#### 🩻 Upload evidence")
        xray_file = st.file_uploader("Chest X-ray (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
        report_files = st.file_uploader(
            "Optional supporting documents (PDF/PNG/JPG)",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Upload lab reports or ID proof for ingestion & OCR",
        )

        submitted = st.form_submit_button("🚀 Run complete agent pipeline", use_container_width=True)
    
    if submitted and xray_file:
        # Show uploaded image
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(xray_file, caption="Uploaded X-Ray", use_column_width=True)
        
        with col2:
            st.markdown("### 🔄 Processing Pipeline")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare data
            multipart_files = [
                ('file', (xray_file.name, xray_file.getvalue(), xray_file.type or 'application/octet-stream'))
            ]

            for doc in report_files or []:
                multipart_files.append(
                    (
                        'documents',
                        (doc.name, doc.getvalue(), doc.type or 'application/octet-stream')
                    )
                )

            patient_profile = {
                "age": age,
                "gender": gender,
                "zip_code": zip_code,
                "city": selected_city,
            }
            allergy_list = [allergy_display.get(label, label) for label in selected_allergies]
            if custom_allergy_entry:
                allergy_list.extend(
                    [entry.strip() for entry in custom_allergy_entry.split(",") if entry.strip()]
                )
            if allergy_list:
                patient_profile["allergies"] = allergy_list

            med_list = list(selected_meds)
            if custom_med_entry:
                med_list.extend([entry.strip() for entry in custom_med_entry.split(",") if entry.strip()])
            if med_list:
                patient_profile["current_medications"] = med_list

            if st.session_state.patient_id:
                patient_profile["registered_patient_id"] = st.session_state.patient_id

            symptom_text = ", ".join(selected_symptoms)
            summary_parts = [part for part in [symptom_text, symptom_notes.strip()] if part]
            clinical_summary = " | ".join(summary_parts) if summary_parts else "Symptoms not provided"

            data = {
                'symptoms': symptom_text,
                'spo2': str(spo2),
                'patient_profile': json.dumps(patient_profile),
                'clinical_summary': clinical_summary,
                'pincode': zip_code,
            }
            
            # Call API
            try:
                status_text.text("📥 Uploading X-ray...")
                progress_bar.progress(20)
                
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/xray/analyze",
                    files=multipart_files,
                    data=data,
                    timeout=30
                )
                
                progress_bar.progress(50)
                status_text.text("🤖 Multi-agent analysis in progress...")
                
                if response.status_code == 200:
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    result = response.json()
                    st.session_state.analysis_result = result
                    
                    # Display results based on status
                    display_analysis_results(result)
                else:
                    st.error(f"❌ Error: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif submitted and not xray_file:
        st.warning("⚠️ Please upload an X-ray image first!")

def display_analysis_results(result):
    """Display formatted analysis results"""
    status = result.get("status")
    
    st.markdown("---")
    
    if status == "EMERGENCY":
        st.error("🚨 **EMERGENCY CASE DETECTED**")
        st.markdown(f"### {result.get('message')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚠️ Severity")
            st.error(f"**{result.get('severity')}**")
            
            st.markdown("#### 🚩 Red Flags")
            for flag in result.get('red_flags', []):
                st.markdown(f"- {flag}")
        
        with col2:
            st.markdown("#### 📞 Action Required")
            st.info(result.get('action_required'))
            
            st.markdown("#### 💡 Recommendations")
            for rec in result.get('recommendations', []):
                st.markdown(f"- {rec}")
        
        st.warning(result.get('disclaimer'))
        render_event_log(result)
    
    elif status == "ESCALATED":
        st.warning("👨‍⚕️ **CASE ESCALATED TO DOCTOR**")
        st.markdown(f"### {result.get('message')}")

        condition = result.get('condition', {})
        condition_probs = condition.get('probs', {})
        primary_condition = "unknown"
        if condition_probs:
            primary_condition = max(condition_probs.items(), key=lambda x: x[1])[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Likely Condition", primary_condition.replace('_', ' ').title())
        with col2:
            st.metric("Severity", result.get('severity', 'N/A'))
        with col3:
            confidence = condition.get('confidence', 0)
            st.metric("Confidence", f"{confidence:.1%}")

        if condition_probs:
            st.markdown("#### 📊 Classification Probabilities")
            cols = st.columns(min(4, len(condition_probs)))
            for idx, (label, value) in enumerate(condition_probs.items()):
                safe_label = label.replace('_', ' ').title()
                cols[idx % len(cols)].metric(safe_label, f"{value*100:.1f}%")
        
        # Doctor recommendations
        doctors = result.get('doctor_recommendations', {})
        doctor_list = doctors.get('available_doctors') or doctors.get('recommended_doctors') or []
        if doctor_list:
            st.markdown("### 👨‍⚕️ Recommended Doctors")
            
            for doc in doctor_list[:3]:
                doc_name = doc.get('name', 'Doctor')
                specialty = doc.get('specialty', 'General Physician')
                with st.expander(f"Dr. {doc_name} - {specialty}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if doc.get('hospital'):
                            st.write(f"**Hospital:** {doc['hospital']}")
                        if doc.get('experience_years') is not None:
                            st.write(f"**Experience:** {doc['experience_years']} years")
                        if doc.get('match_score') is not None:
                            st.write(f"**Match Score:** {doc['match_score']:.1f}/100")
                    with col2:
                        if doc.get('available_slots'):
                            st.write(f"**Available Slots:** {doc['available_slots']}")
                        if doc.get('consultation_fee') is not None:
                            st.write(f"**Consultation Fee:** ₹{doc['consultation_fee']}")
                        button_key = doc.get('doctor_id') or f"book_{doc_name}_{specialty}"
                        if st.button("📅 Book Appointment", key=button_key):
                            st.success(f"Booking appointment with Dr. {doc_name}...")
        
        # Red flags
        if result.get('red_flags'):
            st.markdown("### 🚩 Warning Signs")
            for flag in result['red_flags']:
                st.error(f"• {flag}")
        
        st.info(result.get('disclaimer'))
        render_event_log(result)
    
    elif status == "SUCCESS":
        st.success("✅ **ANALYSIS COMPLETED SUCCESSFULLY**")
        
        assessment = result.get('assessment', {})
        treatment = result.get('treatment', {})
        pharmacy = result.get('pharmacy', {})
        
        # Assessment
        st.markdown("### 🩺 Medical Assessment")
        col1, col2, col3 = st.columns(3)
        with col1:
            primary_condition_value = assessment.get('primary_condition') or assessment.get('condition', 'N/A')
            if isinstance(primary_condition_value, str):
                primary_condition_value = primary_condition_value.replace('_', ' ').title()
            st.metric("Condition", primary_condition_value)
        with col2:
            st.metric("Severity", assessment.get('severity', 'N/A'))
        with col3:
            confidence = assessment.get('confidence', 0)
            st.metric("Confidence", f"{confidence:.1%}")
        
        # Probabilities
        condition_probs = assessment.get('condition_probabilities') or assessment.get('probabilities') or {}
        if condition_probs:
            st.markdown("#### 📊 Classification Probabilities")
            cols = st.columns(min(4, len(condition_probs)))
            for idx, (label, value) in enumerate(condition_probs.items()):
                safe_label = label.replace('_', ' ').title()
                cols[idx % len(cols)].metric(safe_label, f"{value*100:.1f}%")
        
        # Red flags
        if assessment.get('red_flags'):
            st.markdown("#### ⚠️ Warning Signs")
            for flag in assessment['red_flags']:
                st.warning(f"• {flag}")
        
        # Treatment recommendations
        st.markdown("---")
        st.markdown("### 💊 Treatment Recommendations")
        
        medicines = treatment.get('otc_medicines', [])
        if medicines:
            for med in medicines:
                med_name = med.get('name') or med.get('drug_name') or med.get('sku', 'OTC Option')
                sub_label = med.get('category') or med.get('form') or med.get('indication')
                title = f"💊 {med_name}"
                if sub_label:
                    title += f" ({sub_label})"

                with st.expander(title):
                    col1, col2 = st.columns(2)
                    with col1:
                        dosage = med.get('dosage') or med.get('dose') or "Follow package instructions"
                        st.write(f"**Dosage:** {dosage}")

                        frequency = med.get('frequency')
                        if frequency:
                            st.write(f"**Frequency:** {frequency}")

                        duration = med.get('duration')
                        if duration:
                            st.write(f"**Duration:** {duration}")

                        max_daily = med.get('max_daily')
                        if max_daily:
                            st.write(f"**Max Daily:** {max_daily}")

                    with col2:
                        purpose = med.get('purpose') or med.get('indication')
                        if purpose:
                            st.write(f"**Purpose:** {purpose}")

                        form = med.get('form')
                        if form:
                            st.write(f"**Form:** {form}")

                        price = med.get('price_range') or med.get('price')
                        if price:
                            st.write(f"**Estimated Price:** {price}")

                        warnings = med.get('warnings') or med.get('notes')
                        if warnings:
                            warnings_list = warnings if isinstance(warnings, (list, tuple)) else [warnings]
                            st.warning("⚠️ " + '; '.join(str(item) for item in warnings_list))
        
        # Safety advice
        if treatment.get('safety_advice'):
            st.markdown("#### 💡 Safety Advice")
            for advice in treatment['safety_advice']:
                st.info(f"• {advice}")
        
        # Interaction warnings
        if treatment.get('interaction_warnings'):
            st.markdown("#### ⚠️ Drug Interaction Warnings")
            for warning in treatment['interaction_warnings']:
                st.error(f"• {warning}")
        
        if pharmacy:
            st.markdown("---")
            st.markdown("### 🏥 Matched Pharmacy")

            header_cols = st.columns(4)
            header_cols[0].metric("Pharmacy", pharmacy.get('pharmacy_name', 'N/A'))
            header_cols[1].metric("Distance", f"{pharmacy.get('distance_km', 0):.1f} km")
            header_cols[2].metric("ETA", f"{pharmacy.get('eta_min', 0)} min")
            header_cols[3].metric("Availability", pharmacy.get('availability', 'unknown').replace('_', ' ').title())

            services = pharmacy.get('services') or []
            if services:
                st.caption("Services: " + ", ".join(services))

            location_context = pharmacy.get('location_context', {})
            if location_context:
                with st.expander("📍 Location context used for matching"):
                    st.write({
                        "input": location_context.get('input'),
                        "city": location_context.get('city'),
                        "pincode_used": location_context.get('pincode_used'),
                        "fallback_to_default": location_context.get('fallback_to_default'),
                        "default_coordinates_applied": location_context.get('default_coordinates_applied'),
                    })

            items = pharmacy.get('items', [])
            if items:
                st.markdown("#### 🧾 Reserved Items")
                for item in items:
                    label = item.get('drug_name') or item.get('sku') or "Medicine"
                    reserved_qty = item.get('reserved_quantity', 0)
                    stock_qty = item.get('quantity_available', 0)
                    with st.expander(f"💊 {label} · reserved {reserved_qty} of {stock_qty} available"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Strength:** {item.get('strength', 'N/A')}")
                            st.write(f"**Unit Price:** ₹{item.get('unit_price', 0):.2f}")
                            st.write(f"**Line Total:** ₹{item.get('line_total', 0):.2f}")
                        with col2:
                            therapy_ref = item.get('therapy_reference', {})
                            if therapy_ref:
                                st.write("**Therapy Guidance:**")
                                st.write({k: v for k, v in therapy_ref.items() if v})

            if pharmacy.get('missing_items'):
                st.warning("Missing items: " + ", ".join(pharmacy['missing_items']))

            col_subtotal, col_delivery, col_total = st.columns(3)
            col_subtotal.metric("Subtotal", f"₹{pharmacy.get('subtotal', 0):.2f}")
            col_delivery.metric("Delivery Fee", f"₹{pharmacy.get('delivery_fee', 0):.2f}")
            col_total.metric("Total", f"₹{pharmacy.get('total_price', 0):.2f}")

            reservation_id = pharmacy.get('reservation_id')
            if reservation_id:
                st.caption(
                    f"Reservation {reservation_id} holds {pharmacy.get('reserved_units', 0)} unit(s) until {pharmacy.get('reservation_expires_at')}"
                )
            if pharmacy.get('delivery_note'):
                st.info(pharmacy['delivery_note'])
        
        # Order summary
        if result.get('order'):
            st.markdown("---")
            st.markdown("### 📦 Order Summary")
            order = result['order']
            order_cols = st.columns(3)
            order_cols[0].metric("Order ID", order.get('order_id', 'N/A'))
            order_cols[1].metric("Status", order.get('status', 'N/A'))
            order_cols[2].metric("Reserved Units", order.get('delivery', {}).get('reserved_units', 0))

            pricing = order.get('pricing', {})
            st.write({
                "Subtotal": pricing.get('subtotal'),
                "Delivery Fee": pricing.get('delivery_fee'),
                "Total": pricing.get('total'),
                "Currency": pricing.get('currency'),
            })

            if order.get('items'):
                st.markdown("#### Items")
                for idx, item in enumerate(order['items'], start=1):
                    st.write(f"{idx}. {item.get('drug_name', item.get('sku', 'Medicine'))} — {item.get('reserved_quantity', 0)} unit(s)")

            if order.get('note'):
                st.caption(order['note'])
        
        render_event_log(result)
    
    else:  # FAILED
        st.error("❌ **ANALYSIS FAILED**")
        st.markdown(f"### {result.get('message', 'Unknown error occurred')}")
        if result.get('error'):
            st.code(result['error'])
        if result.get('recommendations'):
            st.markdown("#### 💡 Recommendations")
            for rec in result['recommendations']:
                st.info(f"• {rec}")
        render_event_log(result)
    
    disclaimers = result.get('disclaimers') or []
    if disclaimers:
        st.markdown("---")
        st.markdown("### ⚠️ Disclaimers")
        for text in disclaimers:
            if text:
                st.caption(f"• {text}")

    # Full JSON
    with st.expander("📄 View Full JSON Response"):
        st.json(result)

    st.caption("Outputs are autogenerated by the agent pipeline for demonstration only. Always defer to licensed clinicians.")


def render_event_log(result: dict) -> None:
    """Render observability trace if available."""
    events = result.get("event_log")
    if not events:
        return

    with st.expander("🔍 Processing Log (agent trace)"):
        for event in events:
            timestamp = event.get("timestamp", "")
            agent = event.get("agent", "Agent")
            level = event.get("level", "INFO")
            message = event.get("message", "")
            st.write(f"**{timestamp}** · {agent} · [{level}] {message}")

def main():
    st.set_page_config(
        page_title="Multi-Agent Healthcare",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🏥 Healthcare AI")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Home", "🩻 X-Ray Analysis", "📊 Results"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📡 System Status")
        api_status, _ = check_api_status()
        if api_status:
            st.success("✅ API Online")
        else:
            st.error("❌ API Offline")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            <p>Multi-Agent Healthcare System</p>
            <p>v2.0 - Agent Integrated</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if page == "🏠 Home":
        home_page()
    elif page == "🩻 X-Ray Analysis":
        xray_analysis_page()
    elif page == "📊 Results":
        st.subheader("📊 Analysis Results")
        if st.session_state.analysis_result:
            display_analysis_results(st.session_state.analysis_result)
        else:
            st.info("No analysis results yet. Upload an X-ray to get started!")

if __name__ == "__main__":
    main()
