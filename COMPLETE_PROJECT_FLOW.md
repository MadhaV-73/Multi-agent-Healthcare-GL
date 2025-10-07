# 🏥 Multi-Agent Healthcare System - Complete Project Overview

## 📋 Project Requirements (From Assignment)

### Core Objective
Build a **proof-of-concept multi-agent system** for healthcare that demonstrates:
1. **4+ collaborating agents** working together
2. **End-to-end patient flow** from data entry to treatment recommendation
3. **Real-time X-ray classification** using AI
4. **Medicine recommendations** based on diagnosis
5. **Pharmacy matching** with location-based search
6. **Doctor escalation** for cases requiring consultation
7. **Complete order generation** for medicine delivery

---

## 🎯 Complete System Flow (As Per Requirements)

### **Step 1: Patient Data Entry** 📝
**User Input:**
- Full Name
- Date of Birth (to calculate age)
- Gender (M/F/U)
- City & ZIP Code (for pharmacy matching)
- Current Symptoms (free text)
- Medication Allergies (if any)
- SpO2 Level (oxygen saturation)
- **X-Ray Image Upload** (PNG/JPG)

**Agent Involved:** None (Pure data collection)

---

### **Step 2: Data Ingestion & Validation** 🔍
**Agent: Ingestion Agent**

**Tasks:**
- Validate file format (PNG/JPG only)
- Check file size (< 10MB)
- Validate patient age (must be > 0)
- Check ZIP code format
- Preprocess image (resize if needed)
- Extract metadata

**Output:**
```json
{
  "patient": {
    "age": 35,
    "gender": "M",
    "allergies": ["Penicillin"]
  },
  "xray_path": "./uploads/xray_123.png",
  "notes": "mild cough, slight fever",
  "spo2": 96,
  "location": {
    "zipcode": "380001",
    "city": "Ahmedabad"
  }
}
```

---

### **Step 3: X-Ray Classification** 🩻
**Agent: Imaging Agent**

**Tasks:**
- Load and analyze X-ray image
- Extract image features (intensity, contrast, patterns)
- Apply rule-based classification logic
- Calculate condition probabilities:
  - Normal
  - Pneumonia
  - COVID-19 Suspect
  - Bronchitis
  - TB Suspect
- Assess severity (mild/moderate/severe)
- Detect red flags (emergency indicators)
- Calculate confidence score

**Output:**
```json
{
  "condition_probs": {
    "normal": 0.55,
    "pneumonia": 0.20,
    "covid_suspect": 0.12,
    "bronchitis": 0.10,
    "tb_suspect": 0.03
  },
  "severity_hint": "mild",
  "confidence": 0.68,
  "red_flags": [],
  "recommendations": [
    "Rest and stay hydrated",
    "Monitor symptoms closely"
  ]
}
```

---

### **Step 4: Coordinator Decision** 🎯
**Agent: Coordinator**

**Decision Tree:**
```
Is SpO2 < 88% OR Critical Red Flags?
├─ YES → 🚨 EMERGENCY RESPONSE
│         Call 911/108 immediately
│         Skip therapy/pharmacy flow
│
└─ NO → Continue to Therapy
        ↓
        Is Severity = "severe" OR No OTC options?
        ├─ YES → 👨‍⚕️ DOCTOR ESCALATION
        │         Call Doctor Agent
        │         Match specialists
        │         Show booking options
        │
        └─ NO → ✅ OTC TREATMENT PATH
                Continue to Therapy Agent
```

---

### **Step 5: Treatment Recommendations** 💊
**Agent: Therapy Agent**

**Tasks:**
- Map condition to treatable indications
- Find suitable OTC medicines from database (30 medicines)
- Check patient age restrictions
- Screen for allergy conflicts
- Check drug-drug interactions (10 interaction rules)
- Generate dosage recommendations
- Create safety advice

**Output:**
```json
{
  "otc_options": [
    {
      "sku": "OTC001",
      "drug_name": "Paracetamol 500mg",
      "dose": "500-650 mg",
      "frequency": "Every 6-8 hours",
      "max_daily": "3000 mg",
      "duration": "3-5 days",
      "warnings": ["Do not exceed max dose", "Avoid alcohol"],
      "price_range": "₹50-150"
    },
    {
      "sku": "OTC015",
      "drug_name": "Cough Syrup",
      "dose": "10 ml",
      "frequency": "3 times daily",
      "max_daily": "30 ml",
      "duration": "5-7 days",
      "warnings": ["May cause drowsiness"],
      "price_range": "₹80-200"
    }
  ],
  "interaction_warnings": [],
  "safety_advice": [
    "Take with food to avoid stomach upset",
    "Complete full course even if feeling better",
    "Seek doctor if fever persists > 3 days"
  ],
  "escalate_to_doctor": false
}
```

---

### **Step 6: Pharmacy Matching** 🏥
**Agent: Pharmacy Agent**

**Tasks:**
- Get patient ZIP code
- Find nearby pharmacies (within 10km radius)
- Check stock availability for each recommended medicine
- Calculate distances using geolocation (lat/long)
- Estimate delivery time (ETA)
- Calculate total costs
- Rank pharmacies by:
  1. Stock availability (100% preferred)
  2. Distance (nearest first)
  3. Total cost (cheapest first)

**Data Used:**
- `pharmacies.json` - 1500 pharmacy locations
- `inventory.csv` - 1500 stock records
- `zipcodes.csv` - 120 Indian PIN codes with coordinates

**Output:**
```json
{
  "pharmacies": [
    {
      "pharmacy_id": "PH001",
      "name": "Apollo Pharmacy",
      "address": "MG Road, Ahmedabad",
      "distance": 2.3,
      "latitude": 23.0225,
      "longitude": 72.5714,
      "total_cost": 230.00,
      "eta": 15,
      "available_medicines": [
        {
          "medicine": "Paracetamol 500mg",
          "price": 80.00,
          "stock": 150
        },
        {
          "medicine": "Cough Syrup",
          "price": 150.00,
          "stock": 45
        }
      ],
      "stock_percentage": 100
    },
    {
      "pharmacy_id": "PH002",
      "name": "MedPlus",
      "address": "SG Highway, Ahmedabad",
      "distance": 4.1,
      "total_cost": 210.00,
      "eta": 25,
      "stock_percentage": 100
    }
  ],
  "recommended_pharmacy": {
    "pharmacy_id": "PH001",
    "name": "Apollo Pharmacy",
    "reason": "Closest with full stock availability"
  }
}
```

---

### **Step 7: Order Generation** 📦
**Agent: Coordinator (Final Consolidation)**

**Tasks:**
- Combine all agent outputs
- Generate complete order summary
- Create treatment plan
- Add disclaimers and warnings
- Format for user display

**Final Output (SUCCESS Path):**
```json
{
  "status": "SUCCESS",
  "analysis_id": "a1b2c3d4-e5f6-7890",
  "assessment": {
    "condition": "normal",
    "probabilities": {
      "normal": 0.55,
      "pneumonia": 0.20,
      "covid_suspect": 0.12,
      "bronchitis": 0.10,
      "tb_suspect": 0.03
    },
    "severity": "mild",
    "confidence": 0.68,
    "red_flags": []
  },
  "treatment": {
    "otc_medicines": [
      {
        "name": "Paracetamol 500mg",
        "category": "Pain Reliever",
        "dosage": "500-650 mg",
        "frequency": "Every 6-8 hours",
        "duration": "3-5 days",
        "purpose": "Reduce fever and pain",
        "warnings": ["Do not exceed max dose", "Avoid alcohol"]
      },
      {
        "name": "Cough Syrup",
        "category": "Cough Suppressant",
        "dosage": "10 ml",
        "frequency": "3 times daily",
        "duration": "5-7 days",
        "purpose": "Relieve cough",
        "warnings": ["May cause drowsiness"]
      }
    ],
    "safety_advice": [
      "⚠️ These are OTC recommendations only - NOT a prescription",
      "📋 Follow dosage instructions carefully",
      "⏱️ Do not exceed recommended duration",
      "🚨 SEEK IMMEDIATE HELP IF: High fever (>103°F), difficulty breathing"
    ],
    "interaction_warnings": []
  },
  "pharmacy": {
    "pharmacies": [...],  // Top 5 nearest pharmacies
    "recommended": {
      "name": "Apollo Pharmacy",
      "address": "MG Road, Ahmedabad",
      "distance": 2.3,
      "eta": 15,
      "total_cost": 230.00
    }
  },
  "order": {
    "order_id": "ORD-20251007-001",
    "items": [
      {
        "medicine": "Paracetamol 500mg",
        "quantity": 10,
        "price": 80.00
      },
      {
        "medicine": "Cough Syrup",
        "quantity": 1,
        "price": 150.00
      }
    ],
    "subtotal": 230.00,
    "delivery_charge": 30.00,
    "total": 260.00,
    "pharmacy": "Apollo Pharmacy",
    "estimated_delivery": "Today, 6:00 PM",
    "payment_options": ["Cash on Delivery", "UPI", "Card"]
  },
  "recommendations": [
    "✅ Order confirmed - medicines will be delivered",
    "📞 Call pharmacy for any queries: +91-XXXXXXXXXX",
    "🩺 Follow up with doctor if symptoms worsen",
    "💊 Take medicines as prescribed",
    "🏥 Visit ER immediately if emergency symptoms"
  ],
  "disclaimers": [
    "⚠️ This is NOT a medical diagnosis",
    "👨‍⚕️ Consult healthcare professional for proper diagnosis",
    "🚫 Do not rely solely on this for medical decisions",
    "📋 AI recommendations are for educational purposes only"
  ],
  "event_log": [
    {"timestamp": "14:30:00", "agent": "Ingestion", "action": "File validated"},
    {"timestamp": "14:30:02", "agent": "Imaging", "action": "X-ray classified"},
    {"timestamp": "14:30:03", "agent": "Coordinator", "action": "OTC path chosen"},
    {"timestamp": "14:30:04", "agent": "Therapy", "action": "2 medicines recommended"},
    {"timestamp": "14:30:05", "agent": "Pharmacy", "action": "5 pharmacies matched"},
    {"timestamp": "14:30:06", "agent": "Coordinator", "action": "Order generated"}
  ]
}
```

---

## 🔀 Alternative Paths

### Path 2: Doctor Escalation 👨‍⚕️
**When:** Moderate/severe cases requiring professional consultation

**Step 6 (Alternative): Doctor Matching**
**Agent: Doctor Agent**

**Tasks:**
- Identify required specialty (Pulmonologist, Respiratory, General)
- Match doctors from database (20 doctors)
- Calculate match score based on:
  - Specialty match
  - Experience (years)
  - Availability (open slots)
  - Distance from patient
- Calculate urgency level
- Find available time slots

**Output:**
```json
{
  "status": "ESCALATED",
  "message": "⚠️ This case requires professional medical consultation",
  "doctor_recommendations": {
    "recommended_doctors": [
      {
        "doctor_id": "DOC001",
        "name": "Dr. Rajesh Kumar",
        "specialty": "Pulmonologist",
        "hospital": "Apollo Hospital",
        "experience_years": 15,
        "consultation_fee": 800,
        "available_slots": 5,
        "next_available": "Tomorrow, 10:00 AM",
        "match_score": 95.5
      }
    ],
    "urgency_level": "moderate",
    "booking_link": "https://hospital.com/book/DOC001"
  }
}
```

---

### Path 3: Emergency Response 🚨
**When:** Critical red flags detected (SpO2 < 88%, severe symptoms)

**Output:**
```json
{
  "status": "EMERGENCY",
  "severity": "CRITICAL",
  "message": "🚨 EMERGENCY: Immediate medical attention required",
  "action_required": "CALL 911/108 IMMEDIATELY",
  "red_flags": [
    "🚨 CRITICAL: SpO2 < 88% - Life-threatening",
    "🚨 CRITICAL: Severe chest pain detected"
  ],
  "recommendations": [
    "🚨 CALL EMERGENCY SERVICES NOW (911/108)",
    "Do NOT wait or attempt self-treatment",
    "Go to nearest emergency room immediately",
    "If chest pain/breathing difficulty: Call ambulance"
  ],
  "nearest_hospitals": [
    {
      "name": "Apollo Emergency",
      "address": "MG Road",
      "distance": 2.1,
      "phone": "+91-79-XXXX-XXXX",
      "emergency_available": true
    }
  ]
}
```

---

## 📊 Agent Collaboration Summary

| Agent | Input From | Output To | Primary Task |
|-------|-----------|-----------|--------------|
| **Ingestion** | User form | Imaging | Validate & preprocess |
| **Imaging** | Ingestion | Coordinator | Classify X-ray |
| **Coordinator** | Imaging | Therapy/Doctor | Make escalation decision |
| **Therapy** | Imaging + Coordinator | Pharmacy | Recommend medicines |
| **Pharmacy** | Therapy | Coordinator | Match pharmacies |
| **Doctor** | Coordinator | User | Match specialists |
| **Coordinator** | All agents | User | Generate final output |

---

## 🎯 Current Status

✅ **All 6 agents implemented and tested**
✅ **Complete end-to-end flow working**
✅ **Data files populated (3000+ records)**
✅ **API backend functional**
✅ **Simplified frontend (7 fields)**
✅ **Three outcome paths (SUCCESS/ESCALATED/EMERGENCY)**
✅ **Pharmacy matching with distance calculation**
✅ **Doctor escalation with booking**
✅ **Order generation with delivery**

---

## 🚀 Quick Start

```bash
# Start backend
python api/main.py

# Start frontend
streamlit run app_simple.py

# Access
Frontend: http://localhost:8501
API Docs: http://localhost:8000/docs
```

---

## 📝 Note on "Normal" Cases

When X-ray is classified as **"normal"** (healthy):
- **No OTC medicines recommended** (patient is healthy!)
- **General wellness advice provided**
- **No pharmacy matching needed**
- **Status: SUCCESS with health advice**

This is clinically correct - healthy patients don't need medicine prescriptions!

To see the **complete flow with medicines + pharmacy + order**, test with:
- SpO2: 94-96%
- Symptoms: "mild cough" or "slight fever"
- This will trigger mild bronchitis/pneumonia → OTC recommendations

---

## 🎓 Assignment Compliance

✅ **4+ Collaborating Agents** - 6 implemented
✅ **End-to-End Flow** - Upload → Classify → Recommend → Match → Order
✅ **Real Agent Collaboration** - Hand-offs with data transformation
✅ **Decision Making** - Emergency/Escalation/OTC paths
✅ **Location-Based Services** - Pharmacy matching by distance
✅ **Booking System** - Doctor appointment scheduling
✅ **Order Generation** - Complete e-commerce flow
✅ **Professional Output** - Clean UI, proper disclaimers
✅ **Deployment Ready** - Can deploy to Streamlit Cloud/Render

---

**For questions or demo, refer to:**
- `INTEGRATION_COMPLETE.md` - Full integration details
- `ESCALATION_FINAL_FIX.md` - Escalation logic explained
- `SIMPLIFIED_FORM_FIX.md` - Form simplification guide
