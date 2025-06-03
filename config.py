# config.py

import os
from typing import Dict, Any

class Config:
    """Configuration settings for the Prior Authorization Assistant"""
    
    # Application Settings
    APP_NAME = "Intelligent Prior Authorization Assistant"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "AI-powered prior authorization processing for healthcare providers"
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    # Data Files
    SYNTHETIC_PATIENTS_FILE = os.path.join(DATA_DIR, "synthetic_patients.csv")
    PA_GUIDELINES_FILE = os.path.join(DATA_DIR, "pa_guidelines.json")
    DRUG_FORMULARY_FILE = os.path.join(DATA_DIR, "drug_formulary.csv")
    
    # Workflow Settings
    MAX_PROCESSING_TIME = 300  # seconds
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    EMERGENCY_OVERRIDE_ENABLED = True
    
    # UI Settings
    STREAMLIT_CONFIG = {
        "page_title": APP_NAME,
        "page_icon": "🏥",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Color Scheme
    COLORS = {
        "primary": "#1f77b4",
        "success": "#2ca02c", 
        "warning": "#ff7f0e",
        "danger": "#d62728",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40"
    }
    
    # Decision Categories
    DECISION_TYPES = {
        "APPROVED": {
            "color": COLORS["success"],
            "icon": "✓",
            "description": "Prior authorization approved"
        },
        "DENIED": {
            "color": COLORS["danger"], 
            "icon": "✗",
            "description": "Prior authorization denied"
        },
        "PENDING_REVIEW": {
            "color": COLORS["warning"],
            "icon": "⏳",
            "description": "Manual review required"
        },
        "APPROVED_WITH_CONDITIONS": {
            "color": COLORS["info"],
            "icon": "⚠",
            "description": "Approved with conditions"
        }
    }
    
    # Risk Levels
    RISK_LEVELS = {
        "Low": {"color": COLORS["success"], "threshold": 0.3},
        "Moderate": {"color": COLORS["warning"], "threshold": 0.6},
        "High": {"color": COLORS["danger"], "threshold": 1.0}
    }
    
    # Sample Data for Demo
    SAMPLE_PATIENTS = [
        {
            "patient_id": "PT000001",
            "name": "John Doe",
            "age": 45,
            "gender": "M",
            "diagnosis": "Rheumatoid Arthritis",
            "icd_code": "M05.9",
            "requested_medication": "Adalimumab",
            "dosage": "40mg bi-weekly",
            "duration": "6 months",
            "previous_treatments": ["Methotrexate"],
            "allergies": "NKDA",
            "insurance_tier": "Tier 4",
            "prior_auth_history": "None",
            "cost_per_month": 2500,
            "urgency": "Routine"
        },
        {
            "patient_id": "PT000002", 
            "name": "Jane Smith",
            "age": 67,
            "gender": "F",
            "diagnosis": "Type 2 Diabetes",
            "icd_code": "E11.9",
            "requested_medication": "Semaglutide",
            "dosage": "1mg weekly",
            "duration": "12 months",
            "previous_treatments": ["Metformin", "Insulin"],
            "allergies": "Sulfa",
            "insurance_tier": "Tier 3",
            "prior_auth_history": "Approved",
            "cost_per_month": 850,
            "urgency": "Urgent"
        },
        {
            "patient_id": "PT000003",
            "name": "Mike Johnson", 
            "age": 32,
            "gender": "M",
            "diagnosis": "Asthma",
            "icd_code": "J45.9",
            "requested_medication": "Dupilumab",
            "dosage": "300mg bi-weekly",
            "duration": "6 months",
            "previous_treatments": ["Albuterol", "Fluticasone"],
            "allergies": "None",
            "insurance_tier": "Tier 4", 
            "prior_auth_history": "Denied",
            "cost_per_month": 3200,
            "urgency": "Emergency"
        }
    ]
    
    # API Settings (for future use)
    API_SETTINGS = {
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": 100  # requests per minute
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/pa_assistant.log"
    }
    
    # Performance Metrics
    PERFORMANCE_TARGETS = {
        "processing_time_seconds": 15,
        "accuracy_threshold": 0.95,
        "uptime_percentage": 99.9
    }
    
    @classmethod
    def get_decision_color(cls, decision: str) -> str:
        """Get color for decision type"""
        return cls.DECISION_TYPES.get(decision, {}).get("color", cls.COLORS["dark"])
    
    @classmethod
    def get_risk_color(cls, risk_level: str) -> str:
        """Get color for risk level"""
        return cls.RISK_LEVELS.get(risk_level, {}).get("color", cls.COLORS["dark"])
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs("logs", exist_ok=True)

# Initialize directories on import
Config.create_directories()