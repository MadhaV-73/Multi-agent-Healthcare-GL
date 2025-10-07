"""Quick end-to-end test to verify pharmacy matching works."""

from agents.coordinator import Coordinator

# Initialize coordinator
coordinator = Coordinator(data_dir="./data", upload_dir="./uploads")

# Mock upload with Mumbai pincode
upload_data = {
    "xray_file": "./uploads/test_xray.png",
    "pdf_file": None,
    "patient_info": {
        "age": 45,
        "gender": "M",
        "allergies": ["penicillin"],
        "city": "Mumbai",
        "zip_code": "400001"
    },
    "symptoms": "mild dry cough for 2 days, slight throat irritation",
    "spo2": 97,
    "pincode": "400001",
    "city": "Mumbai"
}

print("=" * 70)
print("RUNNING END-TO-END TEST")
print("=" * 70)
print(f"\nPatient Location: {upload_data['city']}, PIN {upload_data['pincode']}")
print(f"Patient Profile: {upload_data['patient_info']['age']}y {upload_data['patient_info']['gender']}")
print(f"Symptoms: {upload_data['symptoms']}")
print(f"SpO2: {upload_data['spo2']}%")

print("\n" + "=" * 70)
print("EXECUTING PIPELINE...")
print("=" * 70)

# Execute pipeline
result = coordinator.execute_pipeline(upload_data)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

print(f"\nStatus: {result.get('status')}")
print(f"Status Level: {result.get('status_level')}")

if result.get('assessment'):
    assessment = result['assessment']
    print(f"\nAssessment:")
    print(f"  Primary Condition: {assessment.get('primary_condition')}")
    print(f"  Severity: {assessment.get('severity')}")
    print(f"  Confidence: {assessment.get('confidence'):.2%}")

if result.get('treatment'):
    treatment = result['treatment']
    print(f"\nTreatment:")
    print(f"  OTC Medicines: {len(treatment.get('otc_medicines', []))}")
    for med in treatment.get('otc_medicines', [])[:3]:
        print(f"    - {med.get('drug_name')} ({med.get('sku')})")

if result.get('pharmacy'):
    pharmacy = result['pharmacy']
    print(f"\nPharmacy Match:")
    print(f"  Status: {pharmacy.get('status')}")
    print(f"  Pharmacy: {pharmacy.get('pharmacy_name')}")
    print(f"  Distance: {pharmacy.get('distance_km', 0):.1f} km")
    print(f"  ETA: {pharmacy.get('eta_min', 0)} min")
    print(f"  Availability: {pharmacy.get('availability')}")
    print(f"  Items Reserved: {len(pharmacy.get('items', []))}")
    print(f"  Total Price: ₹{pharmacy.get('total_price', 0):.2f}")
    
    if pharmacy.get('location_context'):
        loc = pharmacy['location_context']
        print(f"\n  Location Context:")
        print(f"    City: {loc.get('city')}")
        print(f"    Pincode: {loc.get('pincode_used')}")
        print(f"    Fallback: {loc.get('fallback_to_default')}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

# Validate key requirements
pharmacy = result.get('pharmacy')
checks = {
    "Pipeline executed": result.get('status') is not None,
    "Pharmacy matched": pharmacy and pharmacy.get('pharmacy_name') is not None,
    "Distance calculated": pharmacy and pharmacy.get('distance_km', 0) > 0,
    "ETA calculated": pharmacy and pharmacy.get('eta_min', 0) > 0,
    "Items found": pharmacy and len(pharmacy.get('items', [])) > 0,
    "Location tracked": pharmacy and pharmacy.get('location_context') is not None,
}

print("\nValidation Checks:")
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {check}")

all_passed = all(checks.values())
print(f"\nOverall: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}")
