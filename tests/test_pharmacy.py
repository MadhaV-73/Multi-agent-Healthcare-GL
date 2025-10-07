import math
from datetime import datetime

import pytest

from agents.pharmacy_agent import PharmacyAgent


DATA_DIR = "./data"


@pytest.fixture()
def pharmacy_agent(monkeypatch):
    agent = PharmacyAgent(data_dir=DATA_DIR)

    # Force coordinates to align with a known pharmacy so stock is available
    known_pharmacy_coords = (19.00185, 73.057978)  # ph0003
    monkeypatch.setattr(agent, "_get_coordinates", lambda _pincode: known_pharmacy_coords)

    # Widen search radius for deterministic tests
    agent.max_search_radius_km = 100
    return agent


def test_pharmacy_process_returns_reservation_details(pharmacy_agent):
    therapy_result = {
        "otc_options": [
            {
                "sku": "OTC001",
                "drug_name": "Paracetamol",
                "frequency": "Every 6 hours",
                "duration": "3 days",
                "warnings": []
            },
            {
                "sku": "OTC015",
                "drug_name": "Phenylephrine",
                "frequency": "Once daily",
                "duration": "5 days",
                "warnings": []
            },
        ]
    }
    location = {
        "zip_code": "400011",
        "city": "Mumbai",
        "fallback_used": False,
    }

    result = pharmacy_agent.process(therapy_result, location)

    assert result["status"] == "success"
    assert result["items"], "Expected at least one reserved item"
    assert result["reservation_id"].startswith("RSV")

    # Validate reserved quantities and pricing
    reserved_units = sum(item["reserved_quantity"] for item in result["items"])
    assert reserved_units == result["reserved_units"]

    for item in result["items"]:
        assert item["reserved_quantity"] > 0
        assert item["reserved_quantity"] <= item["quantity_available"]
        assert math.isclose(
            item["reserved_quantity"] * item["unit_price"],
            item["line_total"],
            rel_tol=1e-6,
        )
        assert set(item["therapy_reference"].keys()) == {"dose", "frequency", "duration", "warnings"}

    subtotal = sum(item["line_total"] for item in result["items"])
    assert math.isclose(result["subtotal"], subtotal, rel_tol=1e-6)
    assert math.isclose(
        result["total_price"],
        result["subtotal"] + result["delivery_fee"],
        rel_tol=1e-6,
    )

    location_context = result.get("location_context", {})
    assert location_context.get("pincode_used") == "400011"
    assert location_context.get("fallback_to_default") is False
    assert location_context.get("city") == "Mumbai"

    # Ensure reservation expiry is ISO formatted
    datetime.fromisoformat(result["reservation_expires_at"])
    datetime.fromisoformat(result["estimated_delivery"])
