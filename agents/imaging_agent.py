"""Deterministic rule-based imaging agent for simulation purposes."""

from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np
from PIL import Image

from agents.base_agent import BaseAgent
from config import RED_FLAG_KEYWORDS


class ImagingAgent(BaseAgent):
    """Heuristic classifier that generates safe, interpretable outputs."""

    CONDITIONS = ["normal", "pneumonia", "covid_suspect", "bronchitis", "tb_suspect"]

    def __init__(self, log_callback=None) -> None:
        super().__init__("ImagingAgent", log_callback)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(self, ingestion_output: Dict[str, Any]) -> Dict[str, Any]:
        self._start_processing()
        try:
            self._validate_input(ingestion_output)

            xray_path = Path(ingestion_output["xray_path"])
            patient = ingestion_output.get("patient", {})
            notes = ingestion_output.get("notes", "")
            spo2 = ingestion_output.get("spo2")

            features = self._extract_image_features(xray_path)
            metadata = {
                "age": patient.get("age", 40),
                "spo2": int(spo2) if spo2 is not None else 98,
                "notes": notes.lower(),
            }

            condition_probs = self._compute_probabilities(features, metadata, xray_path)
            severity = self._score_severity(condition_probs, metadata)
            confidence = self._score_confidence(condition_probs)
            red_flags = self._detect_red_flags(metadata, severity)
            recommendations = self._recommendations(severity, red_flags)

            payload = {
                "condition_probs": condition_probs,
                "severity_hint": severity,
                "confidence": round(confidence, 2),
                "red_flags": red_flags,
                "recommendations": recommendations,
                "disclaimer": "⚠️ Educational simulation only – NOT medical advice.",
            }

            self._log("SUCCESS", "Imaging completed", {"severity": severity, "confidence": payload["confidence"]})
            result = self._create_output(payload)
            self._end_processing(success=True)
            return result
        except Exception as exc:  # pragma: no cover - defensive
            self._end_processing(success=False)
            return self._error_response(str(exc), exc)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_input(self, data: Dict[str, Any]) -> None:
        self._validate_required_fields(data, ["xray_path", "patient"])
        path = Path(data["xray_path"])
        if not path.exists():
            raise FileNotFoundError(f"X-ray not found: {path}")
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("Only PNG/JPG images supported for simulation")

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------
    def _extract_image_features(self, path: Path) -> Dict[str, float]:
        with Image.open(path) as img:
            grayscaled = img.convert("L")
            array = np.asarray(grayscaled, dtype=np.float32)

        mean = float(np.mean(array))
        std = float(np.std(array))
        min_val = float(np.min(array))
        max_val = float(np.max(array))
        dark_ratio = float(np.mean(array < 90))
        bright_ratio = float(np.mean(array > 200))

        return {
            "mean": mean,
            "std": std,
            "contrast": max_val - min_val,
            "dark_ratio": dark_ratio,
            "bright_ratio": bright_ratio,
        }

    # ------------------------------------------------------------------
    # Probability generation
    # ------------------------------------------------------------------
    def _compute_probabilities(self, features: Dict[str, float], metadata: Dict[str, Any], path: Path) -> Dict[str, float]:
        seed = int(hashlib.sha1(path.read_bytes()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        weights = {condition: rng.uniform(0.5, 1.5) for condition in self.CONDITIONS}

        # Feature heuristics
        dark = features["dark_ratio"]
        contrast = features["contrast"]
        mean = features["mean"]

        if dark > 0.55:
            weights["pneumonia"] += 0.9
            weights["covid_suspect"] += 0.6
            weights["normal"] -= 0.7
        elif dark > 0.4:
            weights["bronchitis"] += 0.4
            weights["pneumonia"] += 0.25

        if contrast < 120:
            weights["pneumonia"] += 0.5
        elif contrast > 220:
            weights["normal"] += 0.4

        if mean < 100:
            weights["pneumonia"] += 0.3
            weights["tb_suspect"] += 0.2

        # Symptom modifiers
        notes = metadata["notes"]
        if "dry cough" in notes:
            weights["covid_suspect"] += 0.4
        if "productive" in notes or "phlegm" in notes:
            weights["bronchitis"] += 0.4
        if "fever" in notes:
            weights["pneumonia"] += 0.3
            weights["covid_suspect"] += 0.2
        if "shortness of breath" in notes or "breathless" in notes:
            weights["pneumonia"] += 0.5

        # SpO2 adjustments
        spo2 = metadata["spo2"]
        if spo2 < 90:
            weights["pneumonia"] += 0.8
        elif spo2 < 94:
            weights["pneumonia"] += 0.4
        else:
            weights["normal"] += 0.3

        # Age adjustments
        age = metadata["age"]
        if age > 65:
            weights["pneumonia"] += 0.2
        elif age < 5:
            weights["bronchitis"] += 0.3

        # Normalise to probabilities
        min_clip = 0.01
        clipped = {k: max(min_clip, v) for k, v in weights.items()}
        total = sum(clipped.values())
        probs = {k: round(v / total, 3) for k, v in clipped.items()}

        # Ensure sum to 1.0 (floating rounding fix)
        remainder = 1.0 - sum(probs.values())
        top_key = max(probs, key=probs.get)
        probs[top_key] = round(probs[top_key] + remainder, 3)

        return probs

    # ------------------------------------------------------------------
    # Severity & confidence
    # ------------------------------------------------------------------
    def _score_severity(self, probs: Dict[str, float], metadata: Dict[str, Any]) -> str:
        spo2 = metadata["spo2"]
        infection_prob = probs["pneumonia"] + probs["covid_suspect"]

        if spo2 < 90 or infection_prob > 0.75:
            return "severe"
        if spo2 < 94 or infection_prob > 0.55:
            return "moderate"
        if any(token in metadata["notes"] for token in ["worsening", "severe", "acute"]):
            return "moderate"
        return "mild"

    def _score_confidence(self, probs: Dict[str, float]) -> float:
        ordered = sorted(probs.values(), reverse=True)
        margin = ordered[0] - ordered[1]
        confidence = 0.4 + min(0.5, margin)
        return min(0.95, max(0.4, confidence))

    # ------------------------------------------------------------------
    # Safety signals
    # ------------------------------------------------------------------
    def _detect_red_flags(self, metadata: Dict[str, Any], severity: str) -> List[str]:
        flags: List[str] = []
        notes = metadata["notes"]
        spo2 = metadata["spo2"]

        if spo2 < 88:
            flags.append("🚨 CRITICAL: SpO2 < 88% – call emergency services immediately")
        elif spo2 < 92:
            flags.append("⚠️ WARNING: Oxygen saturation is low; urgent doctor review advised")

        for keyword in RED_FLAG_KEYWORDS:
            if keyword.lower() in notes:
                flags.append(f"⚠️ WARNING: Reported symptom '{keyword}' requires prompt medical attention")

        if severity == "severe":
            flags.append("⚠️ WARNING: Severe presentation – direct medical supervision recommended")

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for flag in flags:
            if flag not in seen:
                deduped.append(flag)
                seen.add(flag)
        return deduped

    # ------------------------------------------------------------------
    # User-facing recommendations
    # ------------------------------------------------------------------
    def _recommendations(self, severity: str, red_flags: Iterable[str]) -> List[str]:
        red_flags = list(red_flags)
        if any(flag.startswith("🚨") for flag in red_flags):
            return [
                "Seek emergency medical care immediately",
                "Call local emergency services (911 / 108)",
                "Do not drive yourself; arrange safe transport",
            ]

        guidance = ["This system is a demo – always consult a qualified clinician."]
        if severity == "severe":
            guidance.insert(0, "Urgent in-person evaluation recommended within a few hours.")
        elif severity == "moderate":
            guidance.insert(0, "Arrange a doctor or tele-consultation within 24–48 hours.")
        else:
            guidance.insert(0, "Monitor symptoms closely and use OTC care if previously recommended.")

        if not red_flags:
            guidance.append("If new red-flag symptoms appear, escalate immediately.")
        return guidance


if __name__ == "__main__":  # pragma: no cover - manual sanity check
    agent = ImagingAgent()
    sample = {
        "patient": {"age": 52, "gender": "F"},
        "xray_path": "./uploads/test_xray.png",
        "notes": "persistent dry cough, mild fever",
        "spo2": 95,
    }
    print(json.dumps(agent.process(sample), indent=2))