import requests
from typing import Dict, List, Optional
import streamlit as st

class HealthCareAPIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
    
    def health_check(self) -> Dict:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}{self.api_prefix}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def submit_patient_analysis(self, patient_data: Dict, files: List = None) -> Dict:
        """Submit patient data for analysis"""
        try:
            url = f"{self.base_url}{self.api_prefix}/patient/analysis"
            
            # Prepare files if any
            files_data = []
            if files:
                for file in files:
                    files_data.append(
                        ('files', (file.name, file.getvalue(), file.type))
                    )
            
            # Send request
            if files_data:
                response = requests.post(
                    url,
                    data={'patient_data': str(patient_data)},
                    files=files_data,
                    timeout=30
                )
            else:
                response = requests.post(url, json=patient_data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"API Error: {str(e)}",
                "patient_id": None
            }
    
    def get_patient_info(self, patient_id: int) -> Dict:
        """Get patient information by ID"""
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/patient/{patient_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def upload_documents(self, patient_id: int, files: List) -> Dict:
        """Upload medical documents"""
        try:
            url = f"{self.base_url}{self.api_prefix}/patient/{patient_id}/documents"
            
            files_data = []
            for file in files:
                files_data.append(
                    ('files', (file.name, file.getvalue(), file.type))
                )
            
            response = requests.post(url, files=files_data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_xray_analysis(self, file) -> Dict:
        """Get X-ray analysis"""
        try:
            url = f"{self.base_url}{self.api_prefix}/xray/analyze"
            files = {'file': (file.name, file.getvalue(), file.type)}
            
            response = requests.post(url, files=files, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_therapy_recommendations(self, patient_id: int) -> Dict:
        """Get therapy recommendations"""
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/therapy/recommendations/{patient_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
