# src/utils/text_processor.py

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

class MedicalTextProcessor:
    """Lightweight text processing for medical documents and data"""
    
    def __init__(self):
        # Medical abbreviations and their expansions
        self.medical_abbreviations = {
            'HTN': 'Hypertension',
            'DM': 'Diabetes Mellitus',
            'CAD': 'Coronary Artery Disease',
            'CHF': 'Congestive Heart Failure',
            'COPD': 'Chronic Obstructive Pulmonary Disease',
            'RA': 'Rheumatoid Arthritis',
            'MI': 'Myocardial Infarction',
            'CVA': 'Cerebrovascular Accident',
            'UTI': 'Urinary Tract Infection',
            'URI': 'Upper Respiratory Infection',
            'DVT': 'Deep Vein Thrombosis',
            'PE': 'Pulmonary Embolism',
            'NKDA': 'No Known Drug Allergies',
            'BID': 'Twice daily',
            'TID': 'Three times daily',
            'QID': 'Four times daily',
            'PRN': 'As needed',
            'PO': 'By mouth',
            'IV': 'Intravenous',
            'IM': 'Intramuscular',
            'SC': 'Subcutaneous'
        }
        
        # Common medication patterns
        self.medication_patterns = {
            'dosage': r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?)',
            'frequency': r'(once|twice|three times|four times|daily|weekly|monthly|q\d+h|bid|tid|qid|prn)',
            'route': r'(po|iv|im|sc|topical|inhaled|sublingual)',
            'duration': r'(\d+)\s*(days?|weeks?|months?|years?)'
        }
        
        # ICD-10 code pattern
        self.icd_pattern = r'[A-Z]\d{2}\.?\d*'
        
        # Drug name patterns (common prefixes/suffixes)
        self.drug_suffixes = ['mab', 'nib', 'tide', 'pril', 'sartan', 'olol', 'pine', 'statin']
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize medical text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize common medical abbreviations
        for abbrev, expansion in self.medical_abbreviations.items():
            text = re.sub(rf'\b{abbrev}\b', expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """Extract medication information from text"""
        medications = []
        
        # Simple medication extraction based on patterns
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Look for medication patterns
            dosage_match = re.search(self.medication_patterns['dosage'], sentence, re.IGNORECASE)
            frequency_match = re.search(self.medication_patterns['frequency'], sentence, re.IGNORECASE)
            route_match = re.search(self.medication_patterns['route'], sentence, re.IGNORECASE)
            duration_match = re.search(self.medication_patterns['duration'], sentence, re.IGNORECASE)
            
            # Extract potential drug names (words ending with common drug suffixes)
            drug_candidates = []
            words = sentence.split()
            for word in words:
                word_clean = re.sub(r'[^\w]', '', word.lower())
                if any(word_clean.endswith(suffix) for suffix in self.drug_suffixes):
                    drug_candidates.append(word.title())
            
            if dosage_match or frequency_match or drug_candidates:
                medication = {
                    'raw_text': sentence,
                    'drug_name': drug_candidates[0] if drug_candidates else 'Unknown',
                    'dosage': dosage_match.group() if dosage_match else '',
                    'frequency': frequency_match.group() if frequency_match else '',
                    'route': route_match.group() if route_match else '',
                    'duration': duration_match.group() if duration_match else ''
                }
                medications.append(medication)
        
        return medications
    
    def extract_icd_codes(self, text: str) -> List[str]:
        """Extract ICD-10 codes from text"""
        icd_codes = re.findall(self.icd_pattern, text, re.IGNORECASE)
        return list(set(icd_codes))  # Remove duplicates
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates
    
    def extract_allergies(self, text: str) -> List[str]:
        """Extract allergy information from text"""
        allergy_keywords = ['allergic to', 'allergy', 'allergies', 'adverse reaction', 'nkda', 'no known drug allergies']
        allergies = []
        
        sentences = text.lower().split('.')
        for sentence in sentences:
            if any(keyword in sentence for keyword in allergy_keywords):
                # Extract potential allergens (capitalize first letter of each word)
                words = sentence.split()
                for i, word in enumerate(words):
                    if word in allergy_keywords and i < len(words) - 1:
                        potential_allergen = words[i + 1].strip(',')
                        if potential_allergen not in ['to', 'the', 'a', 'an']:
                            allergies.append(potential_allergen.title())
        
        return list(set(allergies))
    
    def calculate_text_complexity(self, text: str) -> Dict[str, Any]:
        """Calculate basic text complexity metrics"""
        if not text:
            return {'word_count': 0, 'sentence_count': 0, 'avg_words_per_sentence': 0}
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1),
            'medical_terms_count': sum(1 for word in words if word.lower() in [abbrev.lower() for abbrev in self.medical_abbreviations.keys()])
        }
    
    def parse_pa_document(self, document_text: str) -> Dict[str, Any]:
        """Parse a prior authorization document and extract structured information"""
        
        # Clean the text
        clean_text = self.clean_text(document_text)
        
        # Extract various components
        medications = self.extract_medications(clean_text)
        icd_codes = self.extract_icd_codes(clean_text)
        dates = self.extract_dates(clean_text)
        allergies = self.extract_allergies(clean_text)
        complexity = self.calculate_text_complexity(clean_text)
        
        return {
            'original_text': document_text,
            'cleaned_text': clean_text,
            'extracted_medications': medications,
            'icd_codes': icd_codes,
            'dates': dates,
            'allergies': allergies,
            'text_complexity': complexity,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def format_pa_summary(self, parsed_data: Dict[str, Any]) -> str:
        """Format parsed PA data into a readable summary"""
        
        summary_parts = []
        
        # Medications section
        if parsed_data.get('extracted_medications'):
            summary_parts.append("**Medications Identified:**")
            for med in parsed_data['extracted_medications']:
                med_line = f"- {med['drug_name']}"
                if med['dosage']:
                    med_line += f" {med['dosage']}"
                if med['frequency']:
                    med_line += f" {med['frequency']}"
                summary_parts.append(med_line)
        
        # ICD codes section
        if parsed_data.get('icd_codes'):
            summary_parts.append("\n**Diagnosis Codes:**")
            for code in parsed_data['icd_codes']:
                summary_parts.append(f"- {code}")
        
        # Allergies section
        if parsed_data.get('allergies'):
            summary_parts.append("\n**Allergies:**")
            for allergy in parsed_data['allergies']:
                summary_parts.append(f"- {allergy}")
        
        # Dates section
        if parsed_data.get('dates'):
            summary_parts.append("\n**Important Dates:**")
            for date in parsed_data['dates']:
                summary_parts.append(f"- {date}")
        
        return "\n".join(summary_parts) if summary_parts else "No structured information could be extracted from the document."

class PARequestValidator:
    """Validate prior authorization request data"""
    
    def __init__(self):
        self.required_fields = [
            'patient_id', 'diagnosis', 'requested_medication'
        ]
        
        self.optional_fields = [
            'age', 'gender', 'dosage', 'duration', 'previous_treatments',
            'allergies', 'insurance_tier', 'urgency'
        ]
    
    def validate_pa_request(self, pa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PA request data and return validation results"""
        
        validation_results = {
            'is_valid': True,
            'missing_required_fields': [],
            'missing_optional_fields': [],
            'data_quality_issues': [],
            'recommendations': []
        }
        
        # Check required fields
        for field in self.required_fields:
            if field not in pa_data or not pa_data[field]:
                validation_results['missing_required_fields'].append(field)
                validation_results['is_valid'] = False
        
        # Check optional fields
        for field in self.optional_fields:
            if field not in pa_data or not pa_data[field]:
                validation_results['missing_optional_fields'].append(field)
        
        # Data quality checks
        if 'age' in pa_data:
            try:
                age = int(pa_data['age'])
                if age < 0 or age > 120:
                    validation_results['data_quality_issues'].append("Age seems unrealistic")
            except (ValueError, TypeError):
                validation_results['data_quality_issues'].append("Age is not a valid number")
        
        if 'gender' in pa_data and pa_data['gender'] not in ['M', 'F', 'Male', 'Female', 'Other']:
            validation_results['data_quality_issues'].append("Gender field has unexpected value")
        
        # Generate recommendations
        if validation_results['missing_required_fields']:
            validation_results['recommendations'].append("Please provide all required fields before processing")
        
        if len(validation_results['missing_optional_fields']) > 3:
            validation_results['recommendations'].append("Consider providing more patient information for better decision accuracy")
        
        if validation_results['data_quality_issues']:
            validation_results['recommendations'].append("Please review and correct data quality issues")
        
        return validation_results

# Example usage
if __name__ == "__main__":
    processor = MedicalTextProcessor()
    validator = PARequestValidator()
    
    # Test text processing
    sample_text = """
    Patient has HTN and DM. Prescribed Lisinopril 10mg BID and Metformin 500mg twice daily.
    Allergic to Penicillin. ICD-10: I10, E11.9. Started treatment on 01/15/2024.
    """
    
    parsed = processor.parse_pa_document(sample_text)
    print("Parsed document:")
    print(json.dumps(parsed, indent=2))
    
    # Test validation
    sample_pa = {
        'patient_id': 'PT001',
        'diagnosis': 'Hypertension',
        'requested_medication': 'Lisinopril',
        'age': 45
    }
    
    validation = validator.validate_pa_request(sample_pa)
    print("\nValidation results:")
    print(json.dumps(validation, indent=2))
    