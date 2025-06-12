from typing import Dict, List, Any

class MedicalExtractorAgent:
    """Lightweight medical information extractor using rule-based NLP"""
    
    def __init__(self):
        self.medical_terms = {
            'conditions': [
                'diabetes', 'hypertension', 'arthritis', 'asthma', 'copd',
                'depression', 'migraine', 'cholesterol'
            ],
            'medications': [
                'metformin', 'insulin', 'lisinopril', 'amlodipine', 'methotrexate',
                'adalimumab', 'albuterol', 'sertraline', 'atorvastatin'
            ],
            'symptoms': [
                'pain', 'fatigue', 'shortness of breath', 'chest pain',
                'headache', 'nausea', 'dizziness', 'swelling'
            ]
        }
    
    def extract_medical_info(self, patient_data: Dict) -> Dict:
        """Extract and structure medical information from patient data"""
        
        extracted_info = {
            'patient_id': patient_data.get('patient_id', ''),
            'demographics': {
                'age': patient_data.get('age', 0),
                'gender': patient_data.get('gender', ''),
            },
            'medical_history': {
                'primary_diagnosis': patient_data.get('diagnosis', ''),
                'icd_code': patient_data.get('icd_code', ''),
                'previous_treatments': patient_data.get('previous_treatments', []),
                'allergies': patient_data.get('allergies', 'None'),
            },
            'current_request': {
                'medication': patient_data.get('requested_medication', ''),
                'dosage': patient_data.get('dosage', ''),
                'duration': patient_data.get('duration', ''),
                'urgency': patient_data.get('urgency', 'Routine'),
            },
            'insurance_info': {
                'tier': patient_data.get('insurance_tier', ''),
                'prior_auth_history': patient_data.get('prior_auth_history', 'None'),
                'estimated_cost': patient_data.get('cost_per_month', 0)
            }
        }
        
        return extracted_info
    
    def process(self, state: Dict) -> Dict:
        """Process patient data and extract medical information"""
        patient_data = state.get('patient_data', {})
        extracted_info = self.extract_medical_info(patient_data)
        
        state['extracted_evidence'] = extracted_info
        state['reasoning_chain'] = state.get('reasoning_chain', [])
        state['reasoning_chain'].append("Medical information extracted and structured")
        
        return state
        