# Target Architecture – Multi-Agent Healthcare Assistant

## System Overview
- **UI Layer:** Single Streamlit app (`app.py`) executing the full triage pipeline locally. No external API dependency for the demo build. The UI collects patient metadata, uploads artifacts, displays an event timeline, and serves the consolidated care plan.
- **Orchestration Layer:** `Coordinator` agent sequences the specialist agents, captures structured events, manages safety checks, and handles escalation logic.
- **Specialist Agents:**
  - `IngestionAgent` → file validation, optional OCR stub, PII masking, structured patient bundle.
  - `ImagingAgent` → deterministic image feature extraction stub returning `{condition_probs, severity_hint, confidence, red_flags}`.
  - `TherapyAgent` → condition-to-OTC mapping (from `/data/meds.csv`), allergy & interaction screens, OTC advisories, escalation flags.
  - `PharmacyAgent` → nearest pharmacy match (from `/data/pharmacies.json`, `/data/inventory.csv`, `/data/zipcodes.csv`), ETA + delivery fee estimation, mock reservation payload.
  - `DoctorAgent` → tele-consult escalation for low confidence / red flags using `/data/doctors.csv`.
- **Artifacts:** Minimal curated datasets under `/data`, sample order JSON under `/sample_outputs`, and UX screenshots under `/sample_outputs/screenshots/`.
- **Observability:** `Coordinator` aggregates timestamped events, surfaced both in API responses and Streamlit log widget. Events include agent start/finish, warnings, and escalation notes.

## Agent Contracts
### Ingestion Agent
**Input:**
```json
{
  "patient_profile": {"age": 45, "gender": "F", "allergies": ["ibuprofen"]},
  "files": {"xray": "<UploadedFile>", "documents": ["<UploadedFile>"]},
  "clinical_summary": "cough, low-grade fever",
  "pincode": "400001"
}
```
**Output:**
```json
{
  "patient": {"age": 45, "gender": "F", "allergies": ["ibuprofen"]},
  "xray_path": "uploads/xray_20251007_101530.png",
  "notes": "cough, low-grade fever",
  "spo2": 97,
  "location": {"pincode": "400001"},
  "status": "success"
}
```

### Imaging Agent
Produces normalized condition probability vector and severity hint using deterministic heuristics on pixel statistics + symptom priors. Also flags life-threatening red flags.

### Therapy Agent
Consumes imaging output + patient profile, filters OTC options, surfaces interaction/allergy conflicts, adds safety advice, and sets `escalate_to_doctor` / `requires_prescription` booleans.

### Pharmacy Agent
Given therapy plan + patient location, calculates nearest deliverable pharmacy, assembles availability, ETA, delivery fee, and mock reservation payload. Returns graceful fallbacks (`no_pharmacies`, `out_of_stock`).

### Doctor Agent
Triggered when:
- Imaging severity = `severe`
- Red flags contain emergency keywords
- Therapy requires prescription or no safe OTC path
- Coordinator confidence below threshold

Returns top-N suitable doctors with slots, consultation type, and urgency guidance.

## Data Refresh
- Replace oversized datasets with curated fixtures (~5 pharmacies, ~10 inventory rows, ~6 doctors) to keep tests fast and repo lightweight.
- Ensure CSV schemas follow assignment spec exactly:
  - `inventory.csv`: `pharmacy_id,sku,drug_name,form,strength,price,qty`
  - `meds.csv`: `sku,drug_name,indication,age_min,contra_allergy_keywords`
  - `interactions.csv`: `drug_a,drug_b,level,note`
  - `doctors.csv`: `doctor_id,name,specialty,tele_available,consultation_fee,experience_years,languages,available_slots`
  - `zipcodes.csv`: `pincode,lat,lon`

## UI Experience
1. Upload chest X-ray (+ optional PDF/ID).
2. Provide minimal patient info (age, allergies, symptoms, pincode).
3. Run pipeline from Streamlit button.
4. Show:
   - Summary banner with severity and escalation flag.
   - Tabs for Assessment, OTC options, Pharmacy match, Doctor escalation (if triggered).
   - Downloadable mock order JSON + event log expander.
   - Persistent “Educational demo, not medical advice” disclaimer.

## Testing Strategy
- `tests/test_pipeline.py` → happy-path execution verifies end-to-end JSON contract.
- `tests/test_therapy_agent.py` → allergy + interaction edge cases.
- `tests/test_pharmacy_agent.py` → nearest store calculation & stock fallbacks.

## Deliverables Checklist
- ✅ Streamlit app integrated with agents & event log.
- ✅ FastAPI wrapper optional but aligned with same coordinator for API demos.
- ✅ Updated README with setup, safety, architecture diagram reference, deployment steps.
- ✅ Sample order JSON + screenshots.
- ✅ 3+ automated tests.
- ✅ Slide deck outline (existing `docs/presentation.pptx` to refresh).

This design keeps the project faithful to the assignment brief while staying lightweight, reproducible, and safe for demonstration deployments.
