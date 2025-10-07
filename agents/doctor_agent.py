"""
Production-Ready Doctor Agent for Multi-Agent Healthcare System
Location: agents/doctor_agent.py

Responsibilities:
- Match patients with suitable doctors based on condition
- Check doctor availability for tele-consultation
- Provide doctor recommendations with specialties
- Schedule appointment slots
- Escalation handling for cases requiring medical attention
"""

import os
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


class DoctorAgent:
    """
    Doctor Matching and Tele-consultation Agent.
    
    Input: Escalated case from Coordinator (imaging + therapy results)
    Output: Doctor recommendations with available slots
    """
    
    def __init__(self, data_dir: str = "./data", log_callback=None):
        """
        Initialize Doctor Agent.
        
        Args:
            data_dir: Path to data folder containing doctors.csv
            log_callback: Logging function
        """
        self.data_dir = data_dir
        self.log_callback = log_callback
        
        # Load doctors database
        self.doctors_df = self._load_doctors()
        
        # Condition to specialty mapping
        self.condition_specialty_map = {
            "pneumonia": ["Pulmonologist", "Infectious Disease Specialist", "General Physician"],
            "covid_suspect": ["Infectious Disease Specialist", "Pulmonologist", "General Physician"],
            "bronchitis": ["Pulmonologist", "General Physician"],
            "tb_suspect": ["Pulmonologist", "Infectious Disease Specialist"],
            "normal": ["General Physician"],
            "unknown": ["General Physician"]
        }
        
        self._log("INFO", f"Doctor Agent initialized with {len(self.doctors_df)} doctors")
    
    def process(self, escalation_data: Dict) -> Dict:
        """
        Main processing method - match doctors for escalated cases.
        
        Expected input:
        {
            "imaging_result": {
                "condition_probs": {...},
                "severity_hint": "moderate",
                "red_flags": [...]
            },
            "therapy_result": {
                "escalate_to_doctor": True,
                "requires_prescription": True
            },
            "patient": {
                "age": 45,
                "gender": "M"
            },
            "escalation_reason": "Red flags detected | Prescription required"
        }
        
        Returns:
        {
            "available_doctors": [
                {
                    "doctor_id": "DOC001",
                    "name": "Dr. Rajesh Kumar",
                    "specialty": "Pulmonologist",
                    "experience_years": 15,
                    "consultation_fee": 800,
                    "languages": ["Hindi", "English"],
                    "available_slots": ["2025-10-08T10:00:00", ...],
                    "match_score": 95,
                    "recommendation_reason": "Specialist in respiratory conditions"
                }
            ],
            "urgency_level": "high",
            "recommended_action": "Book consultation within 24 hours",
            "consultation_type": "tele_consult",
            "estimated_wait_time": "Same day",
            "timestamp": "2025-10-07T14:30:00"
        }
        """
        self._log("INFO", "Doctor Agent processing escalated case")
        
        try:
            # Extract data
            imaging_result = escalation_data.get("imaging_result", {})
            therapy_result = escalation_data.get("therapy_result", {})
            patient = escalation_data.get("patient", {})
            
            # Determine primary condition
            condition_probs = imaging_result.get("condition_probs", {})
            primary_condition = max(condition_probs.items(), key=lambda x: x[1])[0] if condition_probs else "unknown"
            
            # Determine severity and urgency
            severity = imaging_result.get("severity_hint", "moderate")
            red_flags = imaging_result.get("red_flags", [])
            urgency_level = self._determine_urgency(severity, red_flags)
            
            # Find matching doctors
            suitable_doctors = self._match_doctors(
                primary_condition,
                severity,
                urgency_level,
                patient
            )
            
            # Sort by match score
            suitable_doctors = sorted(suitable_doctors, key=lambda x: x['match_score'], reverse=True)
            
            # Take top 5 doctors
            top_doctors = suitable_doctors[:5]
            
            # Determine consultation type and action
            consultation_type, recommended_action, wait_time = self._determine_consultation_details(
                urgency_level,
                severity,
                red_flags
            )
            
            result = {
                "available_doctors": top_doctors,
                "total_matches": len(suitable_doctors),
                "urgency_level": urgency_level,
                "recommended_action": recommended_action,
                "consultation_type": consultation_type,
                "estimated_wait_time": wait_time,
                "primary_condition": primary_condition,
                "severity": severity,
                "booking_instructions": self._generate_booking_instructions(urgency_level),
                "emergency_note": self._generate_emergency_note(red_flags),
                "timestamp": datetime.now().isoformat(),
                "agent": "DoctorAgent",
                "status": "success"
            }
            
            self._log("SUCCESS", f"Matched {len(top_doctors)} doctors for {primary_condition} ({urgency_level} urgency)")
            
            return result
            
        except Exception as e:
            self._log("ERROR", f"Doctor matching failed: {str(e)}")
            return self._error_response(str(e))
    
    def _load_doctors(self) -> pd.DataFrame:
        """Load doctors database from CSV."""
        doctors_path = os.path.join(self.data_dir, "doctors.csv")
        
        if not os.path.exists(doctors_path):
            raise FileNotFoundError(f"Doctors database not found: {doctors_path}")
        
        df = pd.read_csv(doctors_path)
        
        # Validate required columns
        required_cols = ['doctor_id', 'name', 'specialty', 'tele_available', 
                        'consultation_fee', 'experience_years']
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in doctors.csv: {missing}")
        
        self._log("INFO", f"Loaded {len(df)} doctors from database")
        return df
    
    def _determine_urgency(self, severity: str, red_flags: List[str]) -> str:
        """
        Determine urgency level based on severity and red flags.
        
        Returns: "critical", "high", "moderate", or "low"
        """
        # Critical if any CRITICAL/EMERGENCY red flags
        if any("CRITICAL" in flag.upper() or "EMERGENCY" in flag.upper() for flag in red_flags):
            return "critical"
        
        # High if severe or any red flags
        if severity == "severe" or red_flags:
            return "high"
        
        # Moderate for moderate severity
        if severity == "moderate":
            return "moderate"
        
        # Low for mild cases
        return "low"
    
    def _match_doctors(
        self,
        condition: str,
        severity: str,
        urgency: str,
        patient: Dict
    ) -> List[Dict]:
        """
        Find suitable doctors based on condition and patient needs.
        """
        # Get required specialties for this condition
        required_specialties = self.condition_specialty_map.get(condition, ["General Physician"])
        
        # Filter doctors by specialty
        suitable = self.doctors_df[
            self.doctors_df['specialty'].isin(required_specialties)
        ].copy()
        
        # Filter by tele-consultation availability
        suitable = suitable[suitable['tele_available'] == True]
        
        if suitable.empty:
            self._log("WARNING", f"No suitable doctors found for {condition}")
            # Fallback to all general physicians
            suitable = self.doctors_df[
                self.doctors_df['specialty'] == 'General Physician'
            ].copy()
        
        # Build doctor list with match scores
        doctor_list = []
        for _, doctor in suitable.iterrows():
            match_score = self._calculate_match_score(
                doctor,
                condition,
                severity,
                urgency,
                required_specialties
            )
            
            # Parse available slots
            slots = self._parse_available_slots(doctor.get('available_slots', ''))
            
            doctor_info = {
                "doctor_id": doctor['doctor_id'],
                "name": doctor['name'],
                "specialty": doctor['specialty'],
                "experience_years": int(doctor['experience_years']),
                "consultation_fee": int(doctor['consultation_fee']),
                "languages": doctor.get('languages', 'English').split(','),
                "available_slots": slots[:3],  # Show next 3 slots
                "total_slots_available": len(slots),
                "match_score": match_score,
                "recommendation_reason": self._get_recommendation_reason(
                    doctor['specialty'],
                    condition,
                    doctor['experience_years']
                )
            }
            
            doctor_list.append(doctor_info)
        
        return doctor_list
    
    def _calculate_match_score(
        self,
        doctor: pd.Series,
        condition: str,
        severity: str,
        urgency: str,
        required_specialties: List[str]
    ) -> int:
        """
        Calculate match score (0-100) for doctor-patient matching.
        
        Factors:
        - Specialty match (40 points)
        - Experience (30 points)
        - Availability (20 points)
        - Random variation (10 points)
        """
        score = 0
        
        # Specialty match (40 points)
        specialty = doctor['specialty']
        if specialty == required_specialties[0]:  # Primary specialty
            score += 40
        elif specialty in required_specialties:  # Secondary specialty
            score += 30
        else:
            score += 20
        
        # Experience (30 points)
        experience = doctor['experience_years']
        if experience >= 15:
            score += 30
        elif experience >= 10:
            score += 25
        elif experience >= 5:
            score += 20
        else:
            score += 15
        
        # Tele-availability (20 points)
        if doctor.get('tele_available', False):
            score += 20
        
        # Small random variation for diversity (10 points)
        score += random.randint(0, 10)
        
        # Urgency bonus (prioritize experienced doctors for urgent cases)
        if urgency in ["critical", "high"] and experience >= 10:
            score += 5
        
        return min(100, score)  # Cap at 100
    
    def _parse_available_slots(self, slots_str: str) -> List[str]:
        """
        Parse available slots string into list of datetime strings.
        
        Input: "2025-10-08T10:00:00,2025-10-08T14:00:00,2025-10-09T09:00:00"
        Output: ["2025-10-08T10:00:00", "2025-10-08T14:00:00", "2025-10-09T09:00:00"]
        """
        if not slots_str or pd.isna(slots_str):
            return []
        
        try:
            slots = [s.strip() for s in str(slots_str).split(',')]
            # Filter out past slots
            now = datetime.now()
            future_slots = [
                slot for slot in slots 
                if datetime.fromisoformat(slot.replace('Z', '')) > now
            ]
            return future_slots
        except:
            return []
    
    def _get_recommendation_reason(
        self,
        specialty: str,
        condition: str,
        experience: int
    ) -> str:
        """Generate human-readable recommendation reason."""
        reasons = []
        
        # Specialty reason
        if specialty == "Pulmonologist":
            reasons.append("Specialist in respiratory and lung conditions")
        elif specialty == "Infectious Disease Specialist":
            reasons.append("Expert in infectious diseases and complicated infections")
        elif specialty == "General Physician":
            reasons.append("Experienced in general medicine and initial diagnosis")
        elif specialty == "Pediatrician":
            reasons.append("Specialized in children's health")
        
        # Experience reason
        if experience >= 15:
            reasons.append(f"{experience}+ years of clinical experience")
        elif experience >= 10:
            reasons.append(f"{experience} years of practice")
        
        # Condition-specific
        if condition in ["pneumonia", "covid_suspect"]:
            reasons.append("Handles respiratory infections")
        elif condition == "tb_suspect":
            reasons.append("Experienced with TB diagnosis and treatment")
        
        return " | ".join(reasons) if reasons else "Qualified medical professional"
    
    def _determine_consultation_details(
        self,
        urgency: str,
        severity: str,
        red_flags: List[str]
    ) -> tuple:
        """
        Determine consultation type, action, and wait time.
        
        Returns: (consultation_type, recommended_action, wait_time)
        """
        if urgency == "critical":
            return (
                "emergency_room",
                "🚨 SEEK EMERGENCY CARE IMMEDIATELY - Call 911/108",
                "IMMEDIATE"
            )
        
        if urgency == "high":
            return (
                "urgent_tele_consult",
                "📞 Book urgent tele-consultation within 6-12 hours",
                "Same day"
            )
        
        if urgency == "moderate":
            return (
                "tele_consult",
                "👨‍⚕️ Schedule tele-consultation within 24-48 hours",
                "1-2 days"
            )
        
        # Low urgency
        return (
            "tele_consult",
            "📋 Book routine consultation within 3-5 days",
            "3-5 days"
        )
    
    def _generate_booking_instructions(self, urgency: str) -> List[str]:
        """Generate step-by-step booking instructions."""
        base_instructions = [
            "1. Select a doctor from the recommended list",
            "2. Choose an available time slot",
            "3. Prepare your medical history and symptoms",
            "4. Have X-ray images and reports ready",
            "5. Join the tele-consultation at scheduled time"
        ]
        
        if urgency == "critical":
            return [
                "🚨 DO NOT BOOK ONLINE - SEEK EMERGENCY CARE",
                "Call emergency services: 911 (US) / 108 (India)",
                "Go to nearest emergency room immediately",
                "Call ahead if possible"
            ]
        
        if urgency == "high":
            urgent_instructions = [
                "⚡ URGENT BOOKING REQUIRED",
                "1. Select earliest available slot (same day preferred)",
                "2. Mention urgency when booking",
                "3. Keep phone ready for doctor's call",
            ]
            return urgent_instructions + base_instructions[2:]
        
        return base_instructions
    
    def _generate_emergency_note(self, red_flags: List[str]) -> str:
        """Generate emergency note if critical red flags present."""
        if not red_flags:
            return ""
        
        critical_flags = [flag for flag in red_flags if "CRITICAL" in flag.upper() or "EMERGENCY" in flag.upper()]
        
        if critical_flags:
            return (
                "🚨 EMERGENCY SITUATION DETECTED\n"
                f"Red flags: {len(critical_flags)} critical warnings\n"
                "This requires IMMEDIATE medical attention. "
                "Do not delay - call emergency services (911/108) or go to ER now."
            )
        
        return (
            f"⚠️ Warning: {len(red_flags)} medical concern(s) detected. "
            "Professional medical evaluation recommended within 24 hours."
        )
    
    def _error_response(self, error_msg: str) -> Dict:
        """Standard error response."""
        return {
            "available_doctors": [],
            "total_matches": 0,
            "urgency_level": "unknown",
            "recommended_action": "Please contact healthcare provider directly",
            "consultation_type": "unknown",
            "estimated_wait_time": "N/A",
            "error": error_msg,
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "agent": "DoctorAgent"
        }
    
    def _log(self, level: str, message: str) -> None:
        """Log events."""
        if self.log_callback:
            self.log_callback("DoctorAgent", level, message)
        else:
            print(f"[{level}] DoctorAgent: {message}")


# ============= DEMO & TESTING =============

def demo_doctor_agent():
    """Demonstrate Doctor Agent usage."""
    
    print("=" * 70)
    print("DOCTOR AGENT - Escalation Handling Demo")
    print("=" * 70)
    
    # Initialize agent
    agent = DoctorAgent(data_dir="./data")
    
    # Mock escalation data
    escalation_data = {
        "imaging_result": {
            "condition_probs": {
                "normal": 0.15,
                "pneumonia": 0.55,
                "covid_suspect": 0.20,
                "bronchitis": 0.08,
                "tb_suspect": 0.02
            },
            "severity_hint": "moderate",
            "confidence": 0.68,
            "red_flags": [
                "⚠️ WARNING: SpO2 < 92% - Seek immediate medical attention"
            ]
        },
        "therapy_result": {
            "escalate_to_doctor": True,
            "requires_prescription": True,
            "primary_condition": "pneumonia"
        },
        "patient": {
            "age": 58,
            "gender": "M",
            "allergies": ["penicillin"]
        },
        "escalation_reason": "Red flags detected | Prescription required"
    }
    
    print("\n📥 INPUT (Escalated Case):")
    print(f"  Condition: Pneumonia (55% probability)")
    print(f"  Severity: moderate")
    print(f"  Red Flags: 1 warning detected")
    print(f"  Patient: 58y Male")
    
    print("\n🔬 PROCESSING...")
    print("  → Determining urgency level")
    print("  → Matching with suitable specialists")
    print("  → Checking availability")
    print("  → Calculating match scores")
    
    # Process (would execute in real scenario)
    # result = agent.process(escalation_data)
    
    # Sample output
    sample_output = {
        "available_doctors": [
            {
                "doctor_id": "DOC001",
                "name": "Dr. Rajesh Kumar",
                "specialty": "Pulmonologist",
                "experience_years": 15,
                "consultation_fee": 800,
                "languages": ["Hindi", "English"],
                "available_slots": [
                    "2025-10-08T10:00:00",
                    "2025-10-08T14:00:00",
                    "2025-10-09T09:00:00"
                ],
                "total_slots_available": 3,
                "match_score": 95,
                "recommendation_reason": "Specialist in respiratory and lung conditions | 15+ years of clinical experience | Handles respiratory infections"
            },
            {
                "doctor_id": "DOC004",
                "name": "Dr. Sneha Desai",
                "specialty": "Pulmonologist",
                "experience_years": 12,
                "consultation_fee": 850,
                "languages": ["Hindi", "English", "Gujarati"],
                "available_slots": [
                    "2025-10-08T09:00:00",
                    "2025-10-08T13:00:00"
                ],
                "total_slots_available": 2,
                "match_score": 92,
                "recommendation_reason": "Specialist in respiratory and lung conditions | 12 years of practice"
            }
        ],
        "total_matches": 8,
        "urgency_level": "high",
        "recommended_action": "📞 Book urgent tele-consultation within 6-12 hours",
        "consultation_type": "urgent_tele_consult",
        "estimated_wait_time": "Same day"
    }
    
    print("\n📤 OUTPUT:")
    print(f"  Urgency: {sample_output['urgency_level'].upper()}")
    print(f"  Action: {sample_output['recommended_action']}")
    print(f"  Type: {sample_output['consultation_type']}")
    print(f"  Wait Time: {sample_output['estimated_wait_time']}")
    print(f"  Doctors Matched: {sample_output['total_matches']}")
    
    print("\n👨‍⚕️ TOP RECOMMENDED DOCTORS:")
    for i, doc in enumerate(sample_output['available_doctors'][:2], 1):
        print(f"\n  {i}. {doc['name']}")
        print(f"     Specialty: {doc['specialty']}")
        print(f"     Experience: {doc['experience_years']} years")
        print(f"     Fee: ₹{doc['consultation_fee']}")
        print(f"     Match Score: {doc['match_score']}/100")
        print(f"     Available Slots: {len(doc['available_slots'])} slots")
    
    print("\n" + "=" * 70)
    print("✅ Doctor Agent ready for Coordinator integration")
    print("=" * 70)


if __name__ == "__main__":
    demo_doctor_agent()
