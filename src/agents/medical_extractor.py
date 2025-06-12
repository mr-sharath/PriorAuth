from typing import Dict, List, Any
from transformers import pipeline
import torch

class MedicalExtractorAgent:
    """Lightweight medical information extractor using rule-based NLP"""
    
    def __init__(self):
        # Use a model fine-tuned for medical NER
        self.ner_pipeline = pipeline(
            "ner",
            model="d4data/biomedical-ner-all",
            aggregation_strategy="simple"
        )
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
        # NEW: If clinical note exists, use BERT
        clinical_note = patient_data.get('clinical_note', '')
        if clinical_note:
            entities = self.ner_pipeline(clinical_note)
            diagnosis = [e['word'] for e in entities if e['entity_group'] in ('DISEASE', 'DISORDER')]
            medications = [e['word'] for e in entities if e['entity_group'] in ('CHEMICAL', 'DRUG')]
            extracted_info['bert_entities'] = entities
            extracted_info['diagnosis_bert'] = diagnosis
            extracted_info['medications_bert'] = medications
            # Optionally, merge with main fields if empty
            if not extracted_info['medical_history']['primary_diagnosis'] and diagnosis:
                extracted_info['medical_history']['primary_diagnosis'] = diagnosis[0]
            if not extracted_info['current_request']['medication'] and medications:
                extracted_info['current_request']['medication'] = medications[0]
        return extracted_info
    
    def process(self, state: Dict) -> Dict:
        """Process patient data and extract medical information"""
        patient_data = state.get('patient_data', {})
        extracted_info = self.extract_medical_info(patient_data)
        
        state['extracted_evidence'] = extracted_info
        state['reasoning_chain'] = state.get('reasoning_chain', [])
        state['reasoning_chain'].append("Medical info extracted (BERT applied if clinical note provided)")
        
        return state
        