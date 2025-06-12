# src/utils/data_loader.py

import pandas as pd
import json
import os
from typing import Dict, List, Optional, Union
import streamlit as st
from datetime import datetime, timedelta
import random

class DataLoader:
    """Utility class for loading and managing data sources"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patients_df = None
        self.guidelines_data = None
        self._ensure_data_exists()
    
    def _ensure_data_exists(self):
        """Ensure all required data files exist, create if missing"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Generate synthetic data if files don't exist
        if not os.path.exists(f"{self.data_dir}/synthetic_patients.csv"):
            self._generate_synthetic_patients()
        
        if not os.path.exists(f"{self.data_dir}/pa_guidelines.json"):
            self._generate_pa_guidelines()
        
        if not os.path.exists(f"{self.data_dir}/drug_formulary.csv"):
            self._generate_drug_formulary()
    
    def _generate_synthetic_patients(self):
        """Generate synthetic patient data for testing"""
        
        # Medical conditions with realistic treatment patterns
        medical_scenarios = [
            {
                'diagnosis': 'Rheumatoid Arthritis',
                'icd_code': 'M05.9',
                'medications': ['Methotrexate', 'Adalimumab', 'Etanercept', 'Rituximab'],
                'typical_age_range': (25, 70),
                'common_allergies': ['None', 'Penicillin', 'Sulfa']
            },
            {
                'diagnosis': 'Type 2 Diabetes',
                'icd_code': 'E11.9',
                'medications': ['Metformin', 'Insulin', 'Semaglutide', 'Liraglutide'],
                'typical_age_range': (35, 80),
                'common_allergies': ['None', 'NKDA']
            },
            {
                'diagnosis': 'Hypertension',
                'icd_code': 'I10',
                'medications': ['Lisinopril', 'Amlodipine', 'Losartan', 'Metoprolol'],
                'typical_age_range': (40, 85),
                'common_allergies': ['None', 'ACE inhibitor allergy']
            },
            {
                'diagnosis': 'Asthma',
                'icd_code': 'J45.9',
                'medications': ['Albuterol', 'Fluticasone', 'Montelukast', 'Budesonide'],
                'typical_age_range': (5, 75),
                'common_allergies': ['None', 'Aspirin', 'Beta-blocker allergy']
            },
            {
                'diagnosis': 'Depression',
                'icd_code': 'F32.9',
                'medications': ['Sertraline', 'Escitalopram', 'Bupropion', 'Venlafaxine'],
                'typical_age_range': (18, 80),
                'common_allergies': ['None', 'SSRI intolerance']
            },
            {
                'diagnosis': 'COPD',
                'icd_code': 'J44.1',
                'medications': ['Tiotropium', 'Budesonide/Formoterol', 'Albuterol', 'Roflumilast'],
                'typical_age_range': (45, 85),
                'common_allergies': ['None', 'Beta-agonist allergy']
            },
            {
                'diagnosis': 'Migraine',
                'icd_code': 'G43.9',
                'medications': ['Sumatriptan', 'Topiramate', 'Propranolol', 'Botox'],
                'typical_age_range': (15, 65),
                'common_allergies': ['None', 'Triptan allergy']
            },
            {
                'diagnosis': 'High Cholesterol',
                'icd_code': 'E78.5',
                'medications': ['Atorvastatin', 'Simvastatin', 'Rosuvastatin', 'Ezetimibe'],
                'typical_age_range': (30, 80),
                'common_allergies': ['None', 'Statin intolerance']
            }
        ]
        
        patients = []
        for i in range(1000):
            scenario = random.choice(medical_scenarios)
            age_min, age_max = scenario['typical_age_range']
            
            # Create realistic patient profile
            patient = {
                'patient_id': f'PT{i+1:06d}',
                'name': f'Patient {i+1}',
                'age': random.randint(age_min, age_max),
                'gender': random.choice(['M', 'F']),
                'diagnosis': scenario['diagnosis'],
                'icd_code': scenario['icd_code'],
                'requested_medication': random.choice(scenario['medications']),
                'dosage': self._get_realistic_dosage(scenario['medications'][0]),
                'duration': random.choice(['3 months', '6 months', '12 months', '18 months']),
                'previous_treatments': random.sample(scenario['medications'], 
                                                   min(random.randint(0, 3), len(scenario['medications']))),
                'allergies': random.choice(scenario['common_allergies']),
                'insurance_tier': random.choices(['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'], 
                                               weights=[40, 30, 20, 10])[0],
                'prior_auth_history': random.choices(['None', 'Approved', 'Denied', 'Pending'], 
                                                   weights=[50, 30, 15, 5])[0],
                'cost_per_month': self._get_realistic_cost(scenario['medications'][0]),
                'urgency': random.choices(['Routine', 'Urgent', 'Emergency'], 
                                        weights=[80, 15, 5])[0],
                'provider_name': f'Dr. {random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"])}',
                'submission_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'member_id': f'MBR{random.randint(100000, 999999)}',
                # Add a clinical note (simple or patterned)
                'clinical_note': f"Patient with {scenario['diagnosis']} on {random.choice(scenario['medications'])}. Prior treatments: {', '.join(random.sample(scenario['medications'], min(2, len(scenario['medications']))))}. Allergies: {random.choice(scenario['common_allergies'])}."
            }
            patients.append(patient)
        
        # Save to CSV
        df = pd.DataFrame(patients)
        df.to_csv(f"{self.data_dir}/synthetic_patients.csv", index=False)
        print(f"Generated {len(patients)} synthetic patient records")
    
    def _generate_pa_guidelines(self):
        """Generate comprehensive PA guidelines"""
        guidelines = {
            "guidelines": {
                "Rheumatoid Arthritis": {
                    "first_line": ["Methotrexate", "Sulfasalazine", "Hydroxychloroquine"],
                    "second_line": ["Adalimumab", "Etanercept", "Infliximab", "Rituximab"],
                    "step_therapy_required": True,
                    "duration_limit": "6 months initial, renewable",
                    "lab_requirements": ["CBC", "LFT", "CRP", "ESR"],
                    "contraindications": ["Active infection", "Pregnancy", "Severe liver disease", "Immunodeficiency"],
                    "monitoring": "CBC and LFT every 3 months",
                    "max_cost_per_month": 3000
                },
                "Type 2 Diabetes": {
                    "first_line": ["Metformin"],
                    "second_line": ["Insulin", "Semaglutide", "Liraglutide", "Dulaglutide"],
                    "step_therapy_required": True,
                    "duration_limit": "12 months initial",
                    "lab_requirements": ["HbA1c", "Creatinine", "eGFR"],
                    "contraindications": ["eGFR <30", "DKA history", "Type 1 diabetes"],
                    "monitoring": "HbA1c every 3 months",
                    "max_cost_per_month": 2500
                },
                "Hypertension": {
                    "first_line": ["Lisinopril", "Amlodipine", "HCTZ"],
                    "second_line": ["Losartan", "Metoprolol", "Atenolol"],
                    "step_therapy_required": False,
                    "duration_limit": "12 months",
                    "lab_requirements": ["Basic metabolic panel", "Creatinine"],
                    "contraindications": ["Angioedema history", "Pregnancy", "Hyperkalemia"],
                    "monitoring": "BP monitoring, annual labs",
                    "max_cost_per_month": 500
                },
                "Asthma": {
                    "first_line": ["Albuterol", "Fluticasone", "Budesonide"],
                    "second_line": ["Montelukast", "Formoterol", "Salmeterol"],
                    "step_therapy_required": True,
                    "duration_limit": "12 months",
                    "lab_requirements": ["None routine"],
                    "contraindications": ["Beta-blocker allergy", "Aspirin allergy"],
                    "monitoring": "Peak flow monitoring, annual spirometry",
                    "max_cost_per_month": 800
                },
                "Depression": {
                    "first_line": ["Sertraline", "Escitalopram", "Fluoxetine"],
                    "second_line": ["Bupropion", "Venlafaxine", "Duloxetine"],
                    "step_therapy_required": True,
                    "duration_limit": "6 months initial",
                    "lab_requirements": ["None routine"],
                    "contraindications": ["MAOI use", "Uncontrolled mania", "Seizure disorder (for bupropion)"],
                    "monitoring": "Suicidal ideation assessment",
                    "max_cost_per_month": 600
                },
                "COPD": {
                    "first_line": ["Tiotropium", "Albuterol"],
                    "second_line": ["Budesonide/Formoterol", "Roflumilast"],
                    "step_therapy_required": True,
                    "duration_limit": "12 months",
                    "lab_requirements": ["Alpha-1 antitrypsin", "ABG if severe"],
                    "contraindications": ["Milk protein allergy", "Severe cardiac disease"],
                    "monitoring": "Spirometry every 6 months",
                    "max_cost_per_month": 1200
                },
                "Migraine": {
                    "first_line": ["Sumatriptan", "Ibuprofen", "Acetaminophen"],
                    "second_line": ["Topiramate", "Propranolol", "Botox"],
                    "step_therapy_required": False,
                    "duration_limit": "6 months for preventive",
                    "lab_requirements": ["None routine"],
                    "contraindications": ["Cardiovascular disease", "Uncontrolled hypertension"],
                    "monitoring": "Headache diary, frequency assessment",
                    "max_cost_per_month": 1500
                },
                "High Cholesterol": {
                    "first_line": ["Atorvastatin", "Simvastatin"],
                    "second_line": ["Rosuvastatin", "Ezetimibe", "PCSK9 inhibitors"],
                    "step_therapy_required": True,
                    "duration_limit": "12 months",
                    "lab_requirements": ["Lipid panel", "LFT"],
                    "contraindications": ["Active liver disease", "Pregnancy", "Myopathy"],
                    "monitoring": "LFT at 3 months, lipid panel every 6 months",
                    "max_cost_per_month": 2000
                }
            },
            "general_rules": {
                "emergency_override": True,
                "appeal_process_days": 30,
                "documentation_required": ["Diagnosis confirmation", "Treatment history", "Lab results"],
                "max_processing_time_hours": 72,
                "urgent_processing_time_hours": 24,
                "emergency_processing_time_hours": 4,
                "tier_4_special_approval": True,
                "generic_substitution_required": True,
                "quantity_limits": {
                    "specialty_drugs": "30 days supply",
                    "controlled_substances": "30 days supply",
                    "standard_medications": "90 days supply"
                }
            }
        }
        
        # Save guidelines
        with open(f"{self.data_dir}/pa_guidelines.json", 'w') as f:
            json.dump(guidelines, f, indent=2)
        print("Generated PA guidelines")
    
    def _generate_drug_formulary(self):
        """Generate drug formulary with pricing information"""
        formulary_data = [
            # Rheumatoid Arthritis
            {'drug_name': 'Methotrexate', 'tier': 'Tier 1', 'cost': 25, 'generic_available': True},
            {'drug_name': 'Adalimumab', 'tier': 'Tier 4', 'cost': 2500, 'generic_available': False},
            {'drug_name': 'Etanercept', 'tier': 'Tier 4', 'cost': 2800, 'generic_available': False},
            {'drug_name': 'Rituximab', 'tier': 'Tier 4', 'cost': 3200, 'generic_available': False},
            
            # Diabetes
            {'drug_name': 'Metformin', 'tier': 'Tier 1', 'cost': 15, 'generic_available': True},
            {'drug_name': 'Insulin', 'tier': 'Tier 2', 'cost': 200, 'generic_available': True},
            {'drug_name': 'Semaglutide', 'tier': 'Tier 3', 'cost': 800, 'generic_available': False},
            {'drug_name': 'Liraglutide', 'tier': 'Tier 3', 'cost': 750, 'generic_available': False},
            
            # Hypertension
            {'drug_name': 'Lisinopril', 'tier': 'Tier 1', 'cost': 10, 'generic_available': True},
            {'drug_name': 'Amlodipine', 'tier': 'Tier 1', 'cost': 12, 'generic_available': True},
            {'drug_name': 'Losartan', 'tier': 'Tier 2', 'cost': 35, 'generic_available': True},
            
            # Continue with other drugs...
            {'drug_name': 'Albuterol', 'tier': 'Tier 1', 'cost': 30, 'generic_available': True},
            {'drug_name': 'Fluticasone', 'tier': 'Tier 2', 'cost': 65, 'generic_available': True},
            {'drug_name': 'Montelukast', 'tier': 'Tier 2', 'cost': 85, 'generic_available': True},
            {'drug_name': 'Sertraline', 'tier': 'Tier 1', 'cost': 20, 'generic_available': True},
            {'drug_name': 'Escitalopram', 'tier': 'Tier 2', 'cost': 45, 'generic_available': True},
            {'drug_name': 'Atorvastatin', 'tier': 'Tier 1', 'cost': 18, 'generic_available': True},
            {'drug_name': 'Rosuvastatin', 'tier': 'Tier 2', 'cost': 55, 'generic_available': True}
        ]
        
        df = pd.DataFrame(formulary_data)
        df.to_csv(f"{self.data_dir}/drug_formulary.csv", index=False)
        print("Generated drug formulary")
    
    def _get_realistic_dosage(self, medication: str) -> str:
        """Get realistic dosage for medication"""
        dosage_map = {
            'Methotrexate': '15mg weekly',
            'Adalimumab': '40mg subcutaneous bi-weekly',
            'Metformin': '500mg twice daily',
            'Insulin': '20 units subcutaneous daily',
            'Semaglutide': '1mg subcutaneous weekly',
            'Lisinopril': '10mg daily',
            'Amlodipine': '5mg daily',
            'Albuterol': '2 puffs every 4-6 hours as needed',
            'Sertraline': '50mg daily',
            'Atorvastatin': '20mg daily'
        }
        return dosage_map.get(medication, '1 tablet daily')
    
    def _get_realistic_cost(self, medication: str) -> int:
        """Get realistic monthly cost for medication"""
        cost_map = {
            'Methotrexate': 25,
            'Adalimumab': 2500,
            'Metformin': 15,
            'Insulin': 200,
            'Semaglutide': 800,
            'Lisinopril': 10,
            'Amlodipine': 12,
            'Albuterol': 30,
            'Sertraline': 20,
            'Atorvastatin': 18
        }
        return cost_map.get(medication, random.randint(20, 500))
    
    def load_patients(self) -> pd.DataFrame:
        """Load patient data"""
        if self.patients_df is None:
            self.patients_df = pd.read_csv(f"{self.data_dir}/synthetic_patients.csv")
        return self.patients_df
    
    def load_guidelines(self) -> Dict:
        """Load PA guidelines"""
        if self.guidelines_data is None:
            with open(f"{self.data_dir}/pa_guidelines.json", 'r') as f:
                self.guidelines_data = json.load(f)
        return self.guidelines_data
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient data by ID"""
        df = self.load_patients()
        patient_row = df[df['patient_id'] == patient_id]
        if not patient_row.empty:
            return patient_row.iloc[0].to_dict()
        return None
    
    def get_random_patients(self, n: int = 10) -> List[Dict]:
        """Get random patient samples for testing"""
        df = self.load_patients()
        sample_df = df.sample(n=min(n, len(df)))
        return sample_df.to_dict('records')
    
    def search_patients(self, **criteria) -> List[Dict]:
        """Search patients by criteria"""
        df = self.load_patients()
        
        for key, value in criteria.items():
            if key in df.columns:
                if isinstance(value, str):
                    df = df[df[key].str.contains(value, case=False, na=False)]
                else:
                    df = df[df[key] == value]
        
        return df.to_dict('records')
    
    @st.cache_data
    def get_summary_statistics(_self) -> Dict:
        """Get summary statistics for dashboard"""
        df = _self.load_patients()
        
        stats = {
            'total_patients': len(df),
            'diagnosis_distribution': df['diagnosis'].value_counts().to_dict(),
            'urgency_distribution': df['urgency'].value_counts().to_dict(),
            'tier_distribution': df['insurance_tier'].value_counts().to_dict(),
            'avg_monthly_cost': df['cost_per_month'].mean(),
            'total_monthly_cost': df['cost_per_month'].sum(),
            'high_cost_cases': len(df[df['cost_per_month'] > 1000]),
            'urgent_cases': len(df[df['urgency'].isin(['Urgent', 'Emergency'])])
        }
        
        return stats

# Example usage
if __name__ == "__main__":
    loader = DataLoader()
    
    # Test data loading
    patients = loader.load_patients()
    print(f"Loaded {len(patients)} patients")
    
    # Test patient search
    diabetes_patients = loader.search_patients(diagnosis="Type 2 Diabetes")
    print(f"Found {len(diabetes_patients)} diabetes patients")
    
    # Test statistics
    stats = loader.get_summary_statistics()
    print("Summary statistics:", stats)