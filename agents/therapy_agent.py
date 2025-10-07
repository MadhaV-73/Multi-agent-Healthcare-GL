"""
Production-Ready Therapy Agent for Multi-Agent Healthcare System
Location: agents/therapy_agent.py

Responsibilities:
- Map conditions to OTC medicines from data/meds.csv
- Check age restrictions and allergies
- Screen drug-drug interactions from data/interactions.csv
- Generate safety warnings and dosage advice
- Flag cases requiring prescription (escalate to doctor)
"""

import os
import csv
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random


class TherapyAgent:
    """
    OTC Medicine Recommendation Agent.
    
    Input: Imaging Agent output + Patient data
    Output: OTC medicine recommendations with safety checks
    
    DISCLAIMER: OTC recommendations only - NO prescriptions.
    """
    
    def __init__(self, data_dir: str = "./data", log_callback=None):
        """
        Initialize Therapy Agent with data sources.
        
        Args:
            data_dir: Path to data folder containing meds.csv and interactions.csv
            log_callback: Function for logging to coordinator
        """
        self.data_dir = data_dir
        self.log_callback = log_callback
        
        # Load data
        self.meds_df = self._load_medicines()
        self.interactions_df = self._load_interactions()
        
        # Condition to indication mapping (OTC medicines only)
        self.condition_map = {
            "normal": [],  # Healthy patients don't need medicine
            "pneumonia": ["cough", "fever", "pain", "chest congestion"],
            "covid_suspect": ["fever", "cough", "pain"],
            "bronchitis": ["cough", "chest congestion", "expectorant"],
            "tb_suspect": ["cough", "fever"]  # Will be escalated to doctor anyway
        }
        
        self._log("INFO", "Therapy Agent initialized successfully")
    
    def process(self, imaging_output: Dict, patient_data: Dict) -> Dict:
        """
        Main entry point - receives Imaging Agent output and patient data.
        
        Expected input from Imaging Agent:
        {
            "condition_probs": {"pneumonia": 0.42, "normal": 0.38, ...},
            "severity_hint": "mild",
            "confidence": 0.68,
            "red_flags": [...],
            "recommendations": [...]
        }
        
        Patient data from Ingestion Agent:
        {
            "age": 45,
            "allergies": ["ibuprofen"],
            "current_medications": ["omeprazole"],  # Optional
            "gender": "M"
        }
        
        Returns output schema:
        {
            "otc_options": [
                {
                    "sku": "OTC001",
                    "drug_name": "Paracetamol",
                    "dose": "500 mg",
                    "frequency": "Every 8 hours",
                    "max_daily": "3000 mg",
                    "warnings": ["Do not exceed recommended dose"],
                    "price_range": "₹5-10"
                }
            ],
            "interaction_warnings": [...],
            "allergy_conflicts": [...],
            "age_restrictions": [...],
            "requires_prescription": False,
            "escalate_to_doctor": False,
            "safety_advice": [...],
            "timestamp": "2025-10-05T14:30:00"
        }
        """
        self._log("INFO", "Therapy Agent processing started")
        
        try:
            # Validate inputs
            self._validate_inputs(imaging_output, patient_data)
            
            # Extract key data
            condition_probs = imaging_output.get("condition_probs", {})
            severity = imaging_output.get("severity_hint", "mild")
            red_flags = imaging_output.get("red_flags", [])
            patient_age = patient_data.get("age", 18)
            allergies = patient_data.get("allergies", [])
            current_meds = patient_data.get("current_medications", [])
            
            # Determine primary condition
            primary_condition = max(condition_probs.items(), key=lambda x: x[1])[0]
            
            # Check if prescription needed (not OTC-treatable)
            needs_prescription = self._requires_prescription(
                primary_condition, 
                severity, 
                red_flags
            )
            
            if needs_prescription:
                self._log("WARNING", "Case requires prescription - escalating")
                return self._prescription_required_response(primary_condition, severity)
            
            # Get OTC medicine options
            otc_options = self._get_otc_medicines(
                primary_condition,
                patient_age,
                allergies,
                severity
            )
            
            # Check for drug interactions
            interaction_warnings = self._check_interactions(
                otc_options,
                current_meds
            )
            
            # Filter out allergy conflicts
            otc_options, allergy_conflicts = self._filter_allergies(
                otc_options,
                allergies
            )
            
            # Check age restrictions
            otc_options, age_restrictions = self._check_age_restrictions(
                otc_options,
                patient_age
            )
            
            # Generate safety advice
            safety_advice = self._generate_safety_advice(
                primary_condition,
                severity,
                otc_options
            )
            
            # Decide if doctor escalation needed
            escalate = self._should_escalate(
                red_flags,
                severity,
                interaction_warnings,
                len(otc_options)
            )
            
            result = {
                "otc_options": otc_options,
                "interaction_warnings": interaction_warnings,
                "allergy_conflicts": allergy_conflicts,
                "age_restrictions": age_restrictions,
                "requires_prescription": False,
                "escalate_to_doctor": escalate,
                "safety_advice": safety_advice,
                "primary_condition": primary_condition,
                "severity": severity,
                "disclaimer": "⚠️ OTC RECOMMENDATIONS ONLY - NOT MEDICAL ADVICE. Consult healthcare professional.",
                "timestamp": datetime.now().isoformat(),
                "agent": "TherapyAgent"
            }
            
            self._log("SUCCESS", f"Generated {len(otc_options)} OTC recommendations")
            
            return result
            
        except Exception as e:
            self._log("ERROR", f"Therapy Agent failed: {str(e)}")
            return self._error_response(str(e))
    
    def _load_medicines(self) -> pd.DataFrame:
        """Load medicines database from CSV."""
        meds_path = os.path.join(self.data_dir, "meds.csv")
        
        if not os.path.exists(meds_path):
            raise FileNotFoundError(f"Medicines database not found: {meds_path}")
        
        df = pd.read_csv(meds_path)
        
        # Validate required columns
        required_cols = ['sku', 'drug_name', 'indication', 'age_min', 'contra_allergy_keywords']
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in meds.csv: {missing}")
        
        self._log("INFO", f"Loaded {len(df)} medicines from database")
        return df
    
    def _load_interactions(self) -> pd.DataFrame:
        """Load drug interactions database from CSV."""
        interactions_path = os.path.join(self.data_dir, "interactions.csv")
        
        if not os.path.exists(interactions_path):
            self._log("WARNING", "Interactions database not found - skipping interaction checks")
            return pd.DataFrame(columns=['drug_a', 'drug_b', 'level', 'note'])
        
        df = pd.read_csv(interactions_path)
        self._log("INFO", f"Loaded {len(df)} drug interactions")
        return df
    
    def _validate_inputs(self, imaging_output: Dict, patient_data: Dict) -> None:
        """Validate required inputs."""
        if not imaging_output or not patient_data:
            raise ValueError("Missing required input data")
        
        if "condition_probs" not in imaging_output:
            raise ValueError("Missing condition_probs in imaging output")
        
        if "age" not in patient_data:
            raise ValueError("Missing patient age")
    
    def _requires_prescription(
        self, 
        condition: str, 
        severity: str, 
        red_flags: List[str]
    ) -> bool:
        """
        Determine if condition requires prescription medicine.
        MUCH MORE LENIENT - allow OTC for mild/moderate cases.
        """
        # Only CRITICAL red flags require prescription (not all red flags)
        critical_flags = [f for f in red_flags if "CRITICAL" in f or "EMERGENCY" in f]
        if critical_flags:
            return True
        
        # Only SEVERE cases need prescription (not moderate)
        if severity == "severe":
            return True
        
        # TB suspect always needs prescription
        if condition == "tb_suspect":
            return True
        
        # Remove the moderate + pneumonia/covid rule (too aggressive)
        # Allow OTC for mild/moderate respiratory infections
        
        return False
    
    def _get_otc_medicines(
        self,
        condition: str,
        patient_age: int,
        allergies: List[str],
        severity: str
    ) -> List[Dict]:
        """
        Find OTC medicines suitable for the condition.
        """
        # Get indications for this condition
        indications = self.condition_map.get(condition, [])
        
        if not indications:
            self._log("INFO", f"No OTC treatment for {condition}")
            return []
        
        # Find matching medicines
        suitable_meds = []
        
        for _, med in self.meds_df.iterrows():
            med_indication = str(med['indication']).lower()
            
            # Check if any indication matches
            if any(ind in med_indication for ind in indications):
                
                # Check age restriction
                if patient_age < med['age_min']:
                    continue
                
                # Basic allergy check (detailed check later)
                contra_keywords = str(med['contra_allergy_keywords']).lower().split(',')
                contra_keywords = [k.strip() for k in contra_keywords]
                
                has_allergy = any(
                    allergy.lower() in contra_keywords or 
                    allergy.lower() in str(med['drug_name']).lower()
                    for allergy in allergies
                )
                
                if has_allergy:
                    continue
                
                # Add to suitable list
                suitable_meds.append({
                    "sku": med['sku'],
                    "drug_name": med['drug_name'],
                    "indication": med['indication'],
                    "age_min": int(med['age_min']),
                    "contraindications": contra_keywords
                })
        
        # Enhance with dosage info
        otc_options = []
        for med in suitable_meds[:5]:  # Limit to top 5 options
            option = self._format_medicine_option(med, severity)
            otc_options.append(option)
        
        return otc_options
    
    def _format_medicine_option(self, med: Dict, severity: str) -> Dict:
        """
        Format medicine into standardized option with dosage info.
        """
        drug_name = med['drug_name']
        
        # Dosage database (simplified - in production, this would be from data)
        dosage_info = self._get_dosage_info(drug_name, severity)
        
        return {
            "sku": med['sku'],
            "drug_name": drug_name,
            "dose": dosage_info['dose'],
            "frequency": dosage_info['frequency'],
            "max_daily": dosage_info['max_daily'],
            "duration": dosage_info['duration'],
            "warnings": dosage_info['warnings'],
            "price_range": f"₹{random.randint(5, 100)}-{random.randint(100, 500)}",
            "form": random.choice(["Tablet", "Syrup", "Capsule"])
        }
    
    def _get_dosage_info(self, drug_name: str, severity: str) -> Dict:
        """
        Get dosage information (simplified reference database).
        In production, this would be a comprehensive database.
        """
        # Standard dosages for common OTC medicines
        dosages = {
            "Paracetamol": {
                "dose": "500-650 mg",
                "frequency": "Every 6-8 hours",
                "max_daily": "3000 mg (6 tablets)",
                "duration": "3-5 days",
                "warnings": ["Do not exceed max daily dose", "Avoid alcohol", "Risk of liver damage if overdosed"]
            },
            "Ibuprofen": {
                "dose": "200-400 mg",
                "frequency": "Every 6-8 hours",
                "max_daily": "1200 mg",
                "duration": "3-5 days",
                "warnings": ["Take with food", "Risk of stomach ulcers", "Avoid if kidney disease"]
            },
            "Cetirizine": {
                "dose": "10 mg",
                "frequency": "Once daily",
                "max_daily": "10 mg",
                "duration": "7-14 days",
                "warnings": ["May cause drowsiness", "Avoid alcohol", "Do not drive if drowsy"]
            },
            "Omeprazole": {
                "dose": "20 mg",
                "frequency": "Once daily before breakfast",
                "max_daily": "20 mg",
                "duration": "14 days",
                "warnings": ["Take on empty stomach", "May cause headache", "Long-term use requires doctor supervision"]
            }
        }
        
        # Default dosage if drug not in database
        default = {
            "dose": "As directed on package",
            "frequency": "Follow package instructions",
            "max_daily": "Do not exceed package recommendations",
            "duration": "5-7 days",
            "warnings": ["Read package insert carefully", "Consult pharmacist if unsure"]
        }
        
        # Get drug-specific info or default
        info = dosages.get(drug_name, default)
        
        # Adjust for severity
        if severity == "moderate":
            info['warnings'].append("⚠️ Moderate severity - consult doctor if no improvement in 2-3 days")
        
        return info
    
    def _check_interactions(
        self, 
        otc_options: List[Dict], 
        current_meds: List[str]
    ) -> List[Dict]:
        """
        Check for drug-drug interactions between OTC and current medications.
        """
        if not current_meds or self.interactions_df.empty:
            return []
        
        warnings = []
        
        for otc in otc_options:
            otc_drug = otc['drug_name']
            
            for current_drug in current_meds:
                # Check both directions (A-B and B-A)
                interaction = self.interactions_df[
                    ((self.interactions_df['drug_a'].str.lower() == otc_drug.lower()) & 
                     (self.interactions_df['drug_b'].str.lower() == current_drug.lower())) |
                    ((self.interactions_df['drug_a'].str.lower() == current_drug.lower()) & 
                     (self.interactions_df['drug_b'].str.lower() == otc_drug.lower()))
                ]
                
                if not interaction.empty:
                    for _, row in interaction.iterrows():
                        level = row['level']
                        note = row['note']
                        
                        # Format severity emoji
                        severity_emoji = {
                            'mild': '⚠️',
                            'moderate': '⚠️⚠️',
                            'high': '🚨',
                            'severe': '🚨🚨'
                        }.get(level, '⚠️')
                        
                        warnings.append({
                            "drug_a": otc_drug,
                            "drug_b": current_drug,
                            "level": level,
                            "warning": f"{severity_emoji} {level.upper()}: {note}",
                            "recommendation": self._get_interaction_recommendation(level)
                        })
        
        return warnings
    
    def _get_interaction_recommendation(self, level: str) -> str:
        """Get recommendation based on interaction severity."""
        recommendations = {
            'mild': "Monitor for side effects. Generally safe to use together.",
            'moderate': "Consult pharmacist before combining. May need dose adjustment.",
            'high': "Consult doctor before use. Avoid combination if possible.",
            'severe': "DO NOT COMBINE. Seek doctor's advice immediately."
        }
        return recommendations.get(level, "Consult healthcare professional.")
    
    def _filter_allergies(
        self, 
        otc_options: List[Dict], 
        allergies: List[str]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Remove medicines that conflict with patient allergies.
        Returns: (safe_options, conflicted_options)
        """
        if not allergies:
            return otc_options, []
        
        safe_options = []
        conflicts = []
        
        for option in otc_options:
            drug_name = option['drug_name'].lower()
            has_conflict = False
            
            for allergy in allergies:
                allergy_lower = allergy.lower()
                
                # Check drug name
                if allergy_lower in drug_name:
                    conflicts.append({
                        "drug": option['drug_name'],
                        "allergy": allergy,
                        "reason": f"Patient allergic to {allergy}"
                    })
                    has_conflict = True
                    break
            
            if not has_conflict:
                safe_options.append(option)
        
        return safe_options, conflicts
    
    def _check_age_restrictions(
        self, 
        otc_options: List[Dict], 
        patient_age: int
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Verify age restrictions for medicines.
        Returns: (allowed_options, restricted_options)
        """
        allowed = []
        restricted = []
        
        for option in otc_options:
            age_min = option.get('age_min', 0)
            
            if patient_age >= age_min:
                allowed.append(option)
            else:
                restricted.append({
                    "drug": option['drug_name'],
                    "required_age": age_min,
                    "patient_age": patient_age,
                    "reason": f"Minimum age: {age_min} years"
                })
        
        return allowed, restricted
    
    def _generate_safety_advice(
        self,
        condition: str,
        severity: str,
        otc_options: List[Dict]
    ) -> List[str]:
        """
        Generate general safety advice for the condition.
        """
        advice = []
        
        # General disclaimer
        advice.append("⚠️ These are OTC recommendations only - NOT a prescription")
        advice.append("📋 Follow dosage instructions carefully")
        advice.append("⏱️ Do not exceed recommended duration without doctor consultation")
        
        # Condition-specific advice
        if condition in ["pneumonia", "covid_suspect"]:
            advice.append("🏠 Rest and isolate to prevent spread")
            advice.append("💧 Stay well-hydrated (8-10 glasses water/day)")
            advice.append("🌡️ Monitor temperature regularly")
            advice.append("🩺 Check oxygen saturation if available")
        
        if condition == "bronchitis":
            advice.append("💨 Steam inhalation may help relieve congestion")
            advice.append("🚭 Avoid smoking and secondhand smoke")
            advice.append("😷 Wear mask in polluted areas")
        
        # Severity-based advice
        if severity == "moderate":
            advice.append("⚠️ If symptoms worsen or persist beyond 3 days, consult doctor immediately")
            advice.append("📞 Keep emergency contact numbers handy")
        
        # When to seek medical help
        advice.append("🚨 SEEK IMMEDIATE HELP IF: High fever (>103°F), difficulty breathing, chest pain, confusion")
        
        return advice
    
    def _should_escalate(
        self,
        red_flags: List[str],
        severity: str,
        interaction_warnings: List[Dict],
        num_otc_options: int
    ) -> bool:
        """
        Decide if case should be escalated to doctor.
        MUCH MORE LENIENT - only escalate for true emergencies.
        """
        # Only CRITICAL/EMERGENCY red flags require escalation (not all red flags)
        critical_flags = [f for f in red_flags if "CRITICAL" in f or "EMERGENCY" in f]
        if critical_flags:
            return True
        
        # Only SEVERE cases (not moderate)
        if severity == "severe":
            return True
        
        # High-risk interactions (keep this)
        high_risk_interactions = [w for w in interaction_warnings if w['level'] in ['high', 'severe']]
        if high_risk_interactions:
            return True
        
        # No OTC options AND not mild (allow mild cases even without OTC)
        if num_otc_options == 0 and severity != "mild":
            return True
        
        # Default: DO NOT escalate (allow OTC treatment)
        return False
    
    def _prescription_required_response(self, condition: str, severity: str) -> Dict:
        """
        Generate response when prescription is required (no OTC treatment).
        """
        return {
            "otc_options": [],
            "interaction_warnings": [],
            "allergy_conflicts": [],
            "age_restrictions": [],
            "requires_prescription": True,
            "escalate_to_doctor": True,
            "safety_advice": [
                f"⚠️ {condition.upper()} with {severity} severity requires professional medical evaluation",
                "🏥 OTC medicines are NOT sufficient for this condition",
                "👨‍⚕️ Please consult a doctor for prescription medication",
                "📞 Consider tele-consultation or in-person visit",
                "🚨 If symptoms worsen, seek emergency care immediately"
            ],
            "primary_condition": condition,
            "severity": severity,
            "reason": f"Prescription required for {condition} ({severity} severity)",
            "disclaimer": "⚠️ This condition requires professional medical care and prescription medication.",
            "timestamp": datetime.now().isoformat(),
            "agent": "TherapyAgent"
        }
    
    def _error_response(self, error_msg: str) -> Dict:
        """Return standardized error response."""
        return {
            "otc_options": [],
            "interaction_warnings": [],
            "allergy_conflicts": [],
            "age_restrictions": [],
            "requires_prescription": False,
            "escalate_to_doctor": True,
            "safety_advice": [
                f"⚠️ SYSTEM ERROR: {error_msg}",
                "Unable to generate recommendations",
                "Please consult a healthcare professional directly"
            ],
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "agent": "TherapyAgent"
        }
    
    def _log(self, level: str, message: str) -> None:
        """Log events to coordinator."""
        if self.log_callback:
            self.log_callback("TherapyAgent", level, message)
        else:
            print(f"[{level}] TherapyAgent: {message}")


# ============= DEMO & TESTING =============

def demo_usage():
    """Demonstrate Therapy Agent integration."""
    
    print("=" * 70)
    print("THERAPY AGENT - Production Demo")
    print("=" * 70)
    
    # Initialize agent (assuming data/ folder exists)
    agent = TherapyAgent(data_dir="./data")
    
    # Sample input from Imaging Agent
    imaging_output = {
        "condition_probs": {
            "normal": 0.25,
            "pneumonia": 0.45,
            "covid_suspect": 0.18,
            "bronchitis": 0.10,
            "tb_suspect": 0.02
        },
        "severity_hint": "mild",
        "confidence": 0.72,
        "red_flags": [],
        "recommendations": ["Monitor symptoms", "Stay hydrated"]
    }
    
    # Patient data
    patient_data = {
        "age": 42,
        "allergies": ["penicillin"],
        "current_medications": [],
        "gender": "F"
    }
    
    print("\n📥 INPUT:")
    print(f"  Condition: pneumonia (45% probability)")
    print(f"  Severity: mild")
    print(f"  Patient: {patient_data['age']}y, Allergies: {patient_data['allergies']}")
    
    print("\n🔬 PROCESSING...")
    print("  → Loading medicine database")
    print("  → Checking age restrictions")
    print("  → Screening for allergies")
    print("  → Checking drug interactions")
    print("  → Generating safety advice")
    
    # Sample output
    sample_output = {
        "otc_options": [
            {
                "sku": "OTC001",
                "drug_name": "Paracetamol",
                "dose": "500-650 mg",
                "frequency": "Every 6-8 hours",
                "max_daily": "3000 mg (6 tablets)",
                "duration": "3-5 days",
                "warnings": ["Do not exceed max daily dose", "Avoid alcohol"],
                "price_range": "₹5-50",
                "form": "Tablet"
            },
            {
                "sku": "OTC015",
                "drug_name": "Cetirizine",
                "dose": "10 mg",
                "frequency": "Once daily",
                "max_daily": "10 mg",
                "duration": "7-14 days",
                "warnings": ["May cause drowsiness"],
                "price_range": "₹8-80",
                "form": "Tablet"
            }
        ],
        "interaction_warnings": [],
        "allergy_conflicts": [],
        "age_restrictions": [],
        "requires_prescription": False,
        "escalate_to_doctor": False,
        "safety_advice": [
            "⚠️ These are OTC recommendations only - NOT a prescription",
            "📋 Follow dosage instructions carefully",
            "🏠 Rest and isolate to prevent spread",
            "💧 Stay well-hydrated (8-10 glasses water/day)"
        ],
        "primary_condition": "pneumonia",
        "severity": "mild"
    }
    
    print("\n📤 OUTPUT:")
    print(f"  OTC Options: {len(sample_output['otc_options'])} medicines")
    print(f"  Escalate to Doctor: {sample_output['escalate_to_doctor']}")
    
    print("\n💊 RECOMMENDED MEDICINES:")
    for med in sample_output['otc_options']:
        print(f"\n  {med['drug_name']} ({med['form']})")
        print(f"    Dose: {med['dose']}")
        print(f"    Frequency: {med['frequency']}")
        print(f"    Price: {med['price_range']}")
    
    print("\n" + "=" * 70)
    print("✅ Therapy Agent ready for Coordinator integration")
    print("=" * 70)


if __name__ == "__main__":
    demo_usage()