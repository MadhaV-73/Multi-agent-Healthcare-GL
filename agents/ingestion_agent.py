"""Simplified ingestion agent aligned with assignment contract."""

from __future__ import annotations

import io
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from PIL import Image

try:  # Optional dependency – degrade gracefully during tests
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None

from agents.base_agent import BaseAgent
from config import DEFAULT_LOCATION

UploadedLike = Union[Path, str, io.BytesIO, Any]


@dataclass
class IngestionPayload:
    """Normalized ingestion payload regardless of caller format."""

    xray: UploadedLike
    documents: List[UploadedLike]
    patient: Dict[str, Any]
    clinical_summary: str
    spo2: Optional[int]
    pincode: Optional[str]
    city: Optional[str]


class IngestionAgent(BaseAgent):
    """First agent in pipeline: validates artifacts and structures patient bundle."""

    def __init__(self, upload_dir: str = "./uploads", log_callback=None) -> None:
        super().__init__("IngestionAgent", log_callback)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.allowed_image_exts = {".png", ".jpg", ".jpeg"}
        self.allowed_doc_exts = {".pdf", ".txt"}
        self.max_file_size_bytes = 10 * 1024 * 1024  # 10 MB

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate uploads, extract optional text, and emit structured bundle."""
        normalized = self._normalise_payload(input_data)
        self._validate_input(normalized.__dict__)

        xray_path = self._persist_file(normalized.xray, prefix="xray")
        document_paths, document_text = self._persist_documents(normalized.documents)

        patient = self._build_patient_profile(normalized.patient, document_text)
        notes = self._compose_notes(normalized.clinical_summary, document_text)

        requested_pincode = normalized.pincode
        extracted_zip = self._sanitize_pincode(patient.get("zip_code"))

        chosen_pincode = (
            self._sanitize_pincode(requested_pincode)
            or extracted_zip
        )

        fallback_used = False
        if not chosen_pincode:
            chosen_pincode = str(DEFAULT_LOCATION["pincode"])
            fallback_used = True

        chosen_city = (
            normalized.city
            or patient.get("city")
            or (DEFAULT_LOCATION["city"] if fallback_used else "")
        ) or DEFAULT_LOCATION["city"]

        payload = {
            "patient": patient,
            "xray_path": str(xray_path),
            "notes": notes,
            "spo2": normalized.spo2 if normalized.spo2 is not None else 97,
            "location": {
                "pincode": chosen_pincode,
                "city": chosen_city,
                "fallback_used": fallback_used,
                "raw": {
                    "provided": requested_pincode,
                    "extracted": extracted_zip,
                },
            },
            "ingested_documents": [str(path) for path in document_paths],
            "document_excerpt": self._excerpt(document_text, 280),
        }

        self._log("SUCCESS", "Ingestion complete", {"xray": payload["xray_path"]})
        return self._create_output(payload)

    def _normalise_payload(self, data: Dict[str, Any]) -> IngestionPayload:
        """Accept legacy ({'xray_file': ...}) or new schema and normalise."""

        if "xray_file" in data:
            xray = data.get("xray_file")
            documents = []
            if doc := data.get("pdf_file"):
                documents.append(doc)
            documents.extend(self._listify(data.get("documents")))
        else:
            files = data.get("files") or {}
            xray = files.get("xray") if isinstance(files, dict) else None
            if xray is None:
                xray = data.get("xray")
            documents = []
            if isinstance(files, dict):
                docs = files.get("documents") or []
                documents.extend(self._listify(docs))
            documents.extend(self._listify(data.get("documents")))
        if xray is None:
            raise ValueError("X-ray file missing from ingestion payload")

        patient = (
            data.get("patient_profile")
            or data.get("patient_info")
            or data.get("patient")
            or {}
        )

        clinical_summary = (
            data.get("clinical_summary")
            or data.get("symptoms")
            or data.get("notes")
            or ""
        )

        spo2 = data.get("spo2")
        try:
            spo2 = int(spo2) if spo2 is not None else None
        except Exception:
            spo2 = None

        pincode = self._sanitize_pincode(
            data.get("pincode")
            or data.get("location", {}).get("pincode")
            or data.get("zip_code")
            or patient.get("zip_code")
            or patient.get("pincode")
        )

        city = (
            data.get("city")
            or data.get("location", {}).get("city")
            or patient.get("city")
        )

        return IngestionPayload(
            xray=xray,
            documents=documents,
            patient=patient,
            clinical_summary=str(clinical_summary).strip(),
            spo2=spo2,
            pincode=pincode,
            city=str(city).strip() if city else None,
        )

    @staticmethod
    def _listify(value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return list(value)
        return [value]

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        if not input_data.get("xray"):
            raise ValueError("X-ray artifact is required")

    def _persist_file(self, upload: UploadedLike, prefix: str) -> Path:
        """Persist an uploaded artifact into the uploads directory."""

        if isinstance(upload, Path):
            source = upload
        elif isinstance(upload, str):
            candidate = Path(upload)
            if candidate.exists():
                source = candidate
            else:
                fallback = self.upload_dir / candidate.name
                source = fallback if fallback.exists() else None
        else:
            source = None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = self._infer_extension(upload) or ""
        destination = self.upload_dir / f"{prefix}_{timestamp}{suffix}"

        if source and source.exists():
            shutil.copy(source, destination)
        else:
            blob = self._read_bytes(upload)
            if len(blob) > self.max_file_size_bytes:
                raise ValueError("Uploaded file exceeds 10MB limit")
            destination.write_bytes(blob)

        if prefix == "xray":
            try:
                with Image.open(destination) as img:
                    img.verify()
            except Exception as error:
                destination.unlink(missing_ok=True)
                raise ValueError(f"Invalid X-ray image: {error}")

        return destination

    def _persist_documents(self, uploads: Iterable[UploadedLike]) -> Tuple[List[Path], str]:
        paths: List[Path] = []
        collected_text: List[str] = []

        for doc in uploads or []:
            path = self._persist_file(doc, prefix="doc")
            paths.append(path)
            text = self._extract_document_text(path)
            if text:
                collected_text.append(text)

        combined = "\n".join(collected_text)
        if combined:
            combined = self._mask_pii(combined)
        return paths, combined

    def _read_bytes(self, upload: UploadedLike) -> bytes:
        if isinstance(upload, io.BytesIO):
            upload.seek(0)
            return upload.read()
        if hasattr(upload, "read"):
            upload.seek(0)
            return upload.read()
        if isinstance(upload, (str, Path)):
            path = Path(upload)
            if path.exists():
                return path.read_bytes()
        raise ValueError("Unsupported upload type; expected file-like or path")

    def _infer_extension(self, upload: UploadedLike) -> str:
        name = None
        if isinstance(upload, Path):
            name = upload.name
        elif isinstance(upload, str):
            name = upload
        elif hasattr(upload, "name"):
            name = getattr(upload, "name")
        if not name:
            return ""
        return Path(name).suffix.lower()

    def _extract_document_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(errors="ignore")
        if suffix == ".pdf" and pdfplumber:
            try:
                with pdfplumber.open(path) as pdf:
                    pages = [page.extract_text() or "" for page in pdf.pages]
                return "\n".join(pages)
            except Exception as error:
                self._log("WARNING", "pdfplumber failed", {"error": str(error)})
        return ""

    def _build_patient_profile(self, raw: Dict[str, Any], extracted_text: str) -> Dict[str, Any]:
        age = self._coerce_int(raw.get("age"), default=0, lower=0, upper=120)
        gender = self._normalise_gender(raw.get("gender"))
        allergies = self._normalise_allergies(raw.get("allergies"))
        city = ""
        zip_code = ""

        if isinstance(raw, dict):
            city = str(
                raw.get("city")
                or raw.get("location", {}).get("city")
                or ""
            ).strip()
            potential_zip = (
                raw.get("zip_code")
                or raw.get("pincode")
                or raw.get("postal_code")
            )
            if potential_zip is not None:
                zip_code = self._sanitize_pincode(potential_zip) or ""

        if age == 0 and extracted_text:
            match = re.search(r"age[:\s]+(\d{1,3})", extracted_text, flags=re.IGNORECASE)
            if match:
                age = self._coerce_int(match.group(1), default=age, lower=0, upper=120)

        return {
            "age": age,
            "gender": gender,
            "allergies": allergies,
            "city": city,
            "zip_code": zip_code,
        }

    @staticmethod
    def _coerce_int(value: Any, default: int, lower: int, upper: int) -> int:
        try:
            ivalue = int(value)
            if lower <= ivalue <= upper:
                return ivalue
        except Exception:
            pass
        return default

    @staticmethod
    def _normalise_gender(value: Any) -> str:
        lookup = {"m": "M", "male": "M", "f": "F", "female": "F"}
        if isinstance(value, str):
            key = value.strip().lower()
            return lookup.get(key, "U")
        return "U"

    @staticmethod
    def _normalise_allergies(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            items = re.split(r"[,;]\s*", value)
        else:
            items = list(value)
        return sorted({item.strip() for item in items if item and item.strip()})

    def _compose_notes(self, user_summary: str, doc_text: str) -> str:
        parts: List[str] = []
        if user_summary:
            parts.append(user_summary.strip())
        if doc_text:
            snippet = self._extract_symptom_section(doc_text)
            if snippet:
                parts.append(snippet)
        if not parts:
            parts.append("No symptoms provided")
        return " | ".join(parts)

    def _extract_symptom_section(self, text: str) -> str:
        patterns = (
            r"chief\s+complaint[s]?[:\s]+([^\n]+)",
            r"presenting\s+complaint[s]?[:\s]+([^\n]+)",
            r"symptom[s]?[:\s]+([^\n]+)",
            r"history[:\s]+([^\n]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return self._excerpt(text, 160)

    @staticmethod
    def _excerpt(text: str, length: int) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= length:
            return cleaned
        return cleaned[: length - 3] + "..."

    @staticmethod
    def _sanitize_pincode(value: Any) -> Optional[str]:
        if value is None:
            return None
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 6:
            return digits
        return None

    def _mask_pii(self, text: str) -> str:
        if not text:
            return text

        replacements = [
            (r"\b\d{10}\b", "**********"),
            (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "***-***-****"),
            (r"\b\d{4}\s?\d{4}\s?\d{4}\b", "**** **** ****"),
            (r"\b[A-Z]{5}\d{4}[A-Z]\b", "*****####*"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "***@***.***"),
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "**** **** **** ****"),
        ]
        masked = text
        for pattern, repl in replacements:
            masked = re.sub(pattern, repl, masked)
        return masked

    def cleanup_old_files(self, hours: int = 24) -> int:
        cutoff = datetime.now().timestamp() - hours * 3600
        deleted = 0
        for path in self.upload_dir.glob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                try:
                    path.unlink()
                    deleted += 1
                except Exception as error:
                    self._log("WARNING", "Cleanup failed", {"file": str(path), "error": str(error)})
        if deleted:
            self._log("INFO", "Removed stale uploads", {"count": deleted})
        return deleted


if __name__ == "__main__":
    agent = IngestionAgent()
    sample = {
        "xray_file": Path("./uploads/test_xray.png"),
        "patient_info": {"age": 44, "gender": "Female", "allergies": ["ibuprofen"]},
        "symptoms": "dry cough, fatigue",
        "spo2": 97,
        "pincode": "400001",
    }
    print(json.dumps(agent.process(sample), indent=2))
