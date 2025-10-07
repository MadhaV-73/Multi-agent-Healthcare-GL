"""
Coordinator Agent for Multi-Agent Healthcare System
Location: agents/coordinator.py

Orchestrates all agents in the pipeline:
1. Ingestion → 2. Imaging → 3. Therapy → 4. Pharmacy/Doctor → 5. Order Generation

Handles:
- Sequential agent execution
- Error handling and fallbacks
- Escalation decision logic
- Event logging for observability
- Final output consolidation
"""

import json
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path

# Import agents
from agents.ingestion_agent import IngestionAgent
from agents.imaging_agent import ImagingAgent
from agents.therapy_agent import TherapyAgent
from agents.pharmacy_agent import PharmacyAgent
from agents.doctor_agent import DoctorAgent


class Coordinator:
    """
    Central orchestrator for the multi-agent healthcare system.
    
    Responsibilities:
    - Execute agent pipeline in correct order
    - Make escalation decisions
    - Handle errors gracefully
    - Log all events for observability
    - Generate final recommendations/orders
    """
    
    def __init__(self, data_dir: str = "./data", upload_dir: str = "./uploads"):
        """
        Initialize coordinator with all agents.
        
        Args:
            data_dir: Path to data folder with CSVs/JSONs
            upload_dir: Path to uploads folder
        """
        # Event log for tracking
        self.event_log: List[Dict] = []
        
        # Initialize agents with logging callback
        self.ingestion_agent = IngestionAgent(
            upload_dir=upload_dir,
            log_callback=self._log_event
        )
        
        self.imaging_agent = ImagingAgent(
            log_callback=self._log_event
        )
        
        self.therapy_agent = TherapyAgent(
            data_dir=data_dir,
            log_callback=self._log_event
        )
        
        # Pharmacy and Doctor agents
        self.pharmacy_agent = PharmacyAgent(
            data_dir=data_dir,
            log_callback=self._log_event
        )
        
        self.doctor_agent = DoctorAgent(
            data_dir=data_dir,
            log_callback=self._log_event
        )
        
        # Pipeline state
        self.current_session = None
        
        self._log_event("Coordinator", "INFO", "Coordinator initialized successfully")
    
    def execute_pipeline(self, upload_data: Dict) -> Dict:
        """
        Main pipeline execution method.
        
        Args:
            upload_data: Raw upload data from UI
            {
                "xray_file": file_object,
                "pdf_file": file_object (optional),
                "patient_info": {...},
                "symptoms": "...",
                "spo2": 94,
                "pincode": "380001"
            }
        
        Returns:
            Dict: Complete pipeline result with recommendations/order
        """
        # Create new session
        session_id = self._create_session()
        
        self._log_event("Coordinator", "INFO", f"Starting pipeline execution - Session: {session_id}")
        
        try:
            # ===== STEP 1: INGESTION =====
            self._log_event("Coordinator", "INFO", "STEP 1: Ingestion Agent")
            ingestion_result = self.ingestion_agent.process(upload_data)
            
            if ingestion_result.get("status") == "error":
                return self._pipeline_failed("Ingestion", ingestion_result.get("error"))
            
            # ===== STEP 2: IMAGING =====
            self._log_event("Coordinator", "INFO", "STEP 2: Imaging Agent")
            imaging_result = self.imaging_agent.process(ingestion_result)
            
            if imaging_result.get("error"):
                return self._pipeline_failed("Imaging", imaging_result.get("error"))
            
            # ===== CRITICAL: CHECK RED FLAGS =====
            red_flags = imaging_result.get("red_flags", [])
            if red_flags:
                self._log_event("Coordinator", "WARNING", f"RED FLAGS DETECTED: {len(red_flags)} warnings")
                
                # Check for critical red flags (emergency)
                if self._has_critical_red_flags(red_flags):
                    self._log_event("Coordinator", "CRITICAL", "EMERGENCY situation detected")
                    return self._emergency_response(ingestion_result, imaging_result)
            
            # ===== STEP 3: THERAPY =====
            self._log_event("Coordinator", "INFO", "STEP 3: Therapy Agent")
            therapy_result = self.therapy_agent.process(
                imaging_output=imaging_result,
                patient_data=ingestion_result.get("patient", {})
            )
            
            if therapy_result.get("error"):
                return self._pipeline_failed("Therapy", therapy_result.get("error"))
            
            # ===== DECISION POINT: ESCALATE OR PROCEED? =====
            should_escalate = self._should_escalate_to_doctor(
                imaging_result,
                therapy_result,
                red_flags
            )
            
            if should_escalate:
                self._log_event("Coordinator", "WARNING", "Case requires doctor consultation")
                
                # Call Doctor Agent for escalation
                doctor_result = self.doctor_agent.process({
                    "imaging_result": imaging_result,
                    "therapy_result": therapy_result,
                    "patient": ingestion_result.get("patient", {}),
                    "escalation_reason": self._get_escalation_reason(imaging_result, therapy_result)
                })
                
                # Return escalation response with doctor recommendations
                return self._doctor_escalation_response(
                    ingestion_result,
                    imaging_result,
                    therapy_result,
                    doctor_result
                )
            
            # ===== STEP 4: PHARMACY (if OTC treatment suitable) =====
            # ===== STEP 4: PHARMACY (if OTC treatment suitable) =====
            # ===== STEP 4: PHARMACY (if OTC treatment suitable) =====
            if therapy_result.get("otc_options"):
                self._log_event("Coordinator", "INFO", "STEP 4: Pharmacy Matching")
                
                # Call Pharmacy Agent
                pharmacy_result = self.pharmacy_agent.process(
                    therapy_result=therapy_result,
                    location=ingestion_result.get("location", {})
                )
                
                # Check pharmacy matching status
                if pharmacy_result.get("status") == "error":
                    self._log_event("Coordinator", "WARNING", 
                        f"Pharmacy matching failed: {pharmacy_result.get('message', 'Unknown error')}")
                    # Could escalate to doctor here if needed
                
                elif pharmacy_result.get("availability") in ["no_pharmacies", "out_of_stock"]:
                    self._log_event("Coordinator", "WARNING", 
                        f"Pharmacy issue: {pharmacy_result.get('message', 'Stock unavailable')}")
                    # Offer alternative: tele-consultation or different location
                
                elif pharmacy_result.get("stock_percentage", 0) < 100:
                    self._log_event("Coordinator", "WARNING", 
                        f"Partial stock available: {pharmacy_result.get('stock_percentage')}%")
                    # Continue but warn user
                
                else:
                    self._log_event("Coordinator", "SUCCESS", 
                        f"Pharmacy matched: {pharmacy_result.get('pharmacy_name')} "
                        f"({pharmacy_result.get('distance_km')}km, ETA: {pharmacy_result.get('eta_min')}min)")
            else:
                pharmacy_result = None
                self._log_event("Coordinator", "INFO", "No pharmacy matching needed (escalation case)")
            
            # ===== STEP 5: CONSOLIDATE & GENERATE FINAL OUTPUT =====
            self._log_event("Coordinator", "INFO", "STEP 5: Generating final recommendations")
            
            final_output = self._consolidate_results(
                session_id=session_id,
                ingestion=ingestion_result,
                imaging=imaging_result,
                therapy=therapy_result,
                pharmacy=pharmacy_result
            )
            
            self._log_event("Coordinator", "SUCCESS", "Pipeline completed successfully")
            
            return final_output
            
        except Exception as e:
            self._log_event("Coordinator", "ERROR", f"Pipeline failed: {str(e)}")
            return self._pipeline_failed("System", str(e))
    
    def _should_escalate_to_doctor(
        self,
        imaging_result: Dict,
        therapy_result: Dict,
        red_flags: List[str]
    ) -> bool:
        """
        Determine if case should be escalated to doctor.
        
        MORE SELECTIVE: Allow OTC treatment for mild/moderate cases.
        Only escalate for true medical necessity.
        """
        # Rule 1: CRITICAL/EMERGENCY red flags = escalate (not all red flags)
        critical_red_flags = [flag for flag in red_flags if "CRITICAL" in flag or "EMERGENCY" in flag]
        if critical_red_flags:
            return True
        
        # Rule 2: Therapy agent explicitly says escalate
        if therapy_result.get("escalate_to_doctor"):
            return True
        
        # Rule 3: Prescription medication explicitly required
        if therapy_result.get("requires_prescription"):
            return True
        
        # Rule 4: Severe severity only (not moderate)
        if imaging_result.get("severity_hint") == "severe":
            return True
        
        # Rule 5: No OTC options AND severe (allow mild/moderate even without OTC)
        if not therapy_result.get("otc_options") and imaging_result.get("severity_hint") == "severe":
            return True
        
        # Rule 6: Very low confidence (< 0.3) AND not normal condition
        confidence = imaging_result.get("confidence", 1.0)
        condition_probs = imaging_result.get("condition_probs", {})
        normal_prob = condition_probs.get("normal", 0)
        if confidence < 0.3 and normal_prob < 0.4:
            return True
        
        # DEFAULT: DO NOT ESCALATE - Allow OTC treatment
        return False
    
    def _has_critical_red_flags(self, red_flags: List[str]) -> bool:
        """
        Check if any red flags are CRITICAL (emergency level).
        """
        critical_keywords = ["CRITICAL", "EMERGENCY", "CALL 911", "CALL 108"]
        
        for flag in red_flags:
            if any(keyword in flag.upper() for keyword in critical_keywords):
                return True
        
        return False
    
    def _emergency_response(
        self,
        ingestion_result: Dict,
        imaging_result: Dict
    ) -> Dict:
        """
        Generate emergency response (bypass normal flow).
        """
        return {
            "status": "EMERGENCY",
            "severity": "CRITICAL",
            "action_required": "IMMEDIATE_MEDICAL_ATTENTION",
            "message": "🚨 EMERGENCY: This case requires IMMEDIATE medical attention. Call emergency services (911/108) now.",
            "red_flags": imaging_result.get("red_flags", []),
            "patient": ingestion_result.get("patient", {}),
            "condition": imaging_result.get("condition_probs", {}),
            "recommendations": [
                "🚨 CALL EMERGENCY SERVICES IMMEDIATELY (911/108)",
                "Do NOT wait or attempt self-treatment",
                "Go to nearest emergency room",
                "If chest pain/breathing difficulty: Call ambulance immediately"
            ],
            "disclaimer": "⚠️ CRITICAL SITUATION - Seek professional emergency care NOW",
            "session_id": self.current_session,
            "timestamp": datetime.now().isoformat(),
            "event_log": self.event_log
        }
    
    def _doctor_escalation_response(
        self,
        ingestion_result: Dict,
        imaging_result: Dict,
        therapy_result: Dict,
        doctor_result: Dict = None
    ) -> Dict:
        """
        Generate doctor escalation response.
        """
        return {
            "status": "ESCALATED",
            "severity": imaging_result.get("severity_hint", "moderate"),
            "action_required": "DOCTOR_CONSULTATION",
            "message": "⚠️ This case requires professional medical consultation",
            "patient": ingestion_result.get("patient", {}),
            "condition": {
                "probs": imaging_result.get("condition_probs", {}),
                "severity": imaging_result.get("severity_hint"),
                "confidence": imaging_result.get("confidence")
            },
            "red_flags": imaging_result.get("red_flags", []),
            "therapy_notes": therapy_result.get("safety_advice", []),
            "recommendations": [
                "👨‍⚕️ Schedule appointment with doctor within 24-48 hours",
                "📋 Bring this report and X-ray to consultation",
                "🩺 Consider tele-consultation for faster access",
                "⚠️ If symptoms worsen, seek immediate care"
            ],
            "escalation_reason": self._get_escalation_reason(imaging_result, therapy_result),
            "next_steps": {
                "immediate": "Book doctor appointment",
                "monitoring": "Track symptoms daily",
                "emergency_triggers": "Worsening symptoms, high fever, breathing difficulty"
            },
            "disclaimer": "⚠️ Professional medical evaluation required - NOT FOR SELF-TREATMENT",
            "session_id": self.current_session,
            "timestamp": datetime.now().isoformat(),
            "event_log": self.event_log,
            
            # Doctor recommendations from DoctorAgent
            "doctor_recommendations": doctor_result if doctor_result else {
                "available_doctors": [],
                "message": "Please contact healthcare provider directly"
            }
        }
    
    def _get_escalation_reason(
        self,
        imaging_result: Dict,
        therapy_result: Dict
    ) -> str:
        """Determine why escalation is needed."""
        reasons = []
        
        if imaging_result.get("red_flags"):
            reasons.append("Red flags detected")
        
        if therapy_result.get("requires_prescription"):
            reasons.append("Prescription medication required")
        
        if imaging_result.get("severity_hint") == "severe":
            reasons.append("Severe condition")
        
        if not therapy_result.get("otc_options"):
            reasons.append("No suitable OTC treatment")
        
        if imaging_result.get("confidence", 1.0) < 0.5:
            reasons.append("Low diagnostic confidence")
        
        return " | ".join(reasons) if reasons else "Medical consultation recommended"
    
    
    def _consolidate_results(
        self,
        session_id: str,
        ingestion: Dict,
        imaging: Dict,
        therapy: Dict,
        pharmacy: Optional[Dict]
    ) -> Dict:
        """
        Consolidate all agent results into final output.
        """
        # Determine overall status
        severity = imaging.get("severity_hint", "mild")
        has_red_flags = len(imaging.get("red_flags", [])) > 0
        
        if has_red_flags:
            status_level = "WARNING"
        elif severity == "severe":
            status_level = "WARNING"
        elif severity == "moderate":
            status_level = "CAUTION"
        else:
            status_level = "OK"
        
        return {
            "status": "SUCCESS",
            "status_level": status_level,
            "session_id": session_id,
            
            # Patient Information
            "patient": ingestion.get("patient", {}),
            
            # Medical Assessment
            "assessment": {
                "condition_probabilities": imaging.get("condition_probs", {}),
                "primary_condition": max(
                    imaging.get("condition_probs", {}).items(),
                    key=lambda x: x[1]
                )[0] if imaging.get("condition_probs") else "unknown",
                "severity": severity,
                "confidence": imaging.get("confidence", 0),
                "red_flags": imaging.get("red_flags", []),
            },
            
            # Treatment Recommendations
            "treatment": {
                "otc_medicines": therapy.get("otc_options", []),
                "interaction_warnings": therapy.get("interaction_warnings", []),
                "allergy_conflicts": therapy.get("allergy_conflicts", []),
                "safety_advice": therapy.get("safety_advice", []),
            },
            
            # Pharmacy Information (if available)
            "pharmacy": pharmacy,
            
            # Order Information
            "order": self._generate_order_summary(therapy, pharmacy) if pharmacy else None,
            
            # Recommendations
            "recommendations": imaging.get("recommendations", []),
            
            # Safety & Disclaimers
            "disclaimers": [
                "⚠️ EDUCATIONAL DEMONSTRATION ONLY - NOT MEDICAL ADVICE",
                "This system does NOT provide medical diagnoses",
                "Always consult qualified healthcare professionals",
                "In emergency, call 911/108 immediately",
                therapy.get("disclaimer", "")
            ],
            
            # Metadata
            "timestamp": datetime.now().isoformat(),
            "processing_summary": {
                "ingestion": "completed",
                "imaging": "completed",
                "therapy": "completed",
                "pharmacy": "completed" if pharmacy and pharmacy.get("status") == "success" else "skipped",
                "pharmacy_status": pharmacy.get("status") if pharmacy else "not_applicable"
            },
            
            # Event log for observability
            "event_log": self.event_log
        }
    
    def _generate_order_summary(
        self,
        therapy_result: Dict,
        pharmacy_result: Dict
    ) -> Dict:
        """
        Generate order summary from pharmacy data.
        """
        import random
        
        order_id = f"ORD{random.randint(10000000, 99999999)}"
        
        # Use REAL data from Pharmacy Agent ✅
        items = pharmacy_result.get("items", [])
        subtotal = pharmacy_result.get("subtotal", 0)
        delivery_fee = pharmacy_result.get("delivery_fee", 25)
        total = pharmacy_result.get("total_price", subtotal + delivery_fee)

        reservation_id = pharmacy_result.get("reservation_id")
        reservation_expires = pharmacy_result.get("reservation_expires_at")
        reserved_units = pharmacy_result.get("reserved_units")

        return {
            "order_id": order_id,
            "status": "PENDING_CONFIRMATION",
            "items": items,
            "pricing": {
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "total": total,
                "currency": "INR"
            },
            "delivery": {
                "pharmacy": pharmacy_result.get("pharmacy_name", ""),
                "eta_minutes": pharmacy_result.get("eta_min", 45),
                "address": "To be provided",
                "reservation_id": reservation_id,
                "reserved_units": reserved_units,
                "reservation_expires_at": reservation_expires
            },
            "note": "This is a MOCK order for demonstration purposes only"
        }
    
    def _pipeline_failed(self, failed_stage: str, error: str) -> Dict:
        """
        Handle pipeline failure gracefully.
        """
        self._log_event("Coordinator", "ERROR", f"Pipeline failed at {failed_stage}: {error}")
        
        return {
            "status": "FAILED",
            "failed_at": failed_stage,
            "error": error,
            "message": f"Unable to complete analysis. Error in {failed_stage} stage.",
            "recommendations": [
                "Please try again with different files",
                "Ensure X-ray image is clear and in PNG/JPG format",
                "If problem persists, consult doctor directly"
            ],
            "disclaimer": "⚠️ System error - Please consult healthcare professional directly",
            "session_id": self.current_session,
            "timestamp": datetime.now().isoformat(),
            "event_log": self.event_log
        }
    
    def _create_session(self) -> str:
        """Create unique session ID."""
        import random
        session_id = f"SES{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        self.current_session = session_id
        return session_id
    
    def _log_event(
        self,
        agent_name: str,
        level: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Log event for observability.
        
        Args:
            agent_name: Name of the agent logging
            level: Log level (INFO, WARNING, ERROR, SUCCESS, CRITICAL)
            message: Log message
            metadata: Optional additional data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "level": level,
            "message": message
        }
        
        if metadata:
            event["metadata"] = metadata
        
        self.event_log.append(event)
        
        # Also print to console for debugging
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }.get(level, "•")
        
        print(f"{prefix} [{level}] {agent_name}: {message}")
    
    def get_event_log(self) -> List[Dict]:
        """Get complete event log for current session."""
        return self.event_log
    
    def clear_event_log(self) -> None:
        """Clear event log (for new session)."""
        self.event_log = []
    
    def export_session(self, output_path: str) -> None:
        """
        Export complete session data to JSON file.
        
        Args:
            output_path: Path to save session JSON
        """
        session_data = {
            "session_id": self.current_session,
            "event_log": self.event_log,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self._log_event("Coordinator", "INFO", f"Session exported to {output_path}")


# ============= DEMO & TESTING =============

def demo_coordinator():
    """Demonstrate Coordinator usage."""
    
    print("=" * 70)
    print("COORDINATOR - Pipeline Orchestration Demo")
    print("=" * 70)
    
    # Initialize coordinator
    coordinator = Coordinator(data_dir="./data", upload_dir="./uploads")
    
    # Mock upload data
    upload_data = {
        "xray_file": "./test_xray.png",
        "pdf_file": None,
        "patient_info": {
            "age": 55,
            "gender": "F",
            "allergies": ["penicillin"]
        },
        "symptoms": "persistent cough for 3 weeks, low-grade fever, chest discomfort",
        "spo2": 93,
        "pincode": "380001"
    }
    
    print("\n📥 INPUT:")
    print(f"  Patient: {upload_data['patient_info']['age']}y {upload_data['patient_info']['gender']}")
    print(f"  Symptoms: {upload_data['symptoms']}")
    print(f"  SpO2: {upload_data['spo2']}%")
    
    print("\n🔄 PIPELINE EXECUTION:")
    print("  → Step 1: Ingestion Agent")
    print("  → Step 2: Imaging Agent")
    print("  → Step 3: Therapy Agent")
    print("  → Step 4: Decision (Pharmacy OR Doctor)")
    print("  → Step 5: Consolidate Results")
    
    # Note: Actual execution would happen here
    # result = coordinator.execute_pipeline(upload_data)
    
    print("\n📊 EVENT LOG:")
    for event in coordinator.get_event_log()[:5]:  # Show first 5 events
        print(f"  [{event['level']}] {event['agent']}: {event['message']}")
    
    print("\n" + "=" * 70)
    print("✅ Coordinator ready for production use")
    print("=" * 70)
    
    print("\n📌 NEXT STEPS:")
    print("  1. Add PharmacyAgent integration (see TODO markers)")
    print("  2. Add DoctorAgent integration (see TODO markers)")
    print("  3. Connect to Streamlit UI")


if __name__ == "__main__":
    demo_coordinator()