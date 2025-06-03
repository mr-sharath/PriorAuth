from typing import Dict, List, Any
import random

class RiskAssessorAgent:
    """Assess clinical and financial risks of prior authorization requests"""
    
    def __init__(self):
        self.risk_factors = {
            'age_high_risk': [65, 85],
            'high_cost_threshold': 2000,
            'urgent_conditions': ['Emergency', 'Urgent']
        }
    
    def calculate_clinical_risk(self, patient_info: Dict) -> Dict:
        """Calculate clinical risk score based on patient factors"""
        risk_score = 0
        risk_factors = []
        
        # Age-based risk
        age = patient_info.get('demographics', {}).get('age', 0)
        if age >= 65:
            risk_score += 2
            risk_factors.append("Advanced age (≥65)")
        
        # Urgency-based risk
        urgency = patient_info.get('current_request', {}).get('urgency', 'Routine')
        if urgency in ['Emergency', 'Urgent']:
            risk_score += 3
            risk_factors.append(f"High urgency: {urgency}")
        
        # Allergy considerations
        allergies = patient_info.get('medical_history', {}).get('allergies', 'None')
        if allergies != 'None' and allergies != 'NKDA':
            risk_score += 1
            risk_factors.append(f"Drug allergies: {allergies}")
        
        # Previous authorization history
        prior_auth = patient_info.get('insurance_info', {}).get('prior_auth_history', 'None')
        if prior_auth == 'Denied':
            risk_score += 2
            risk_factors.append("Previous PA denial")
        
        return {
            'clinical_risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'risk_factors': risk_factors
        }
    
    def calculate_financial_risk(self, patient_info: Dict) -> Dict:
        """Calculate financial risk and cost-effectiveness"""
        estimated_cost = patient_info.get('insurance_info', {}).get('estimated_cost', 0)
        tier = patient_info.get('insurance_info', {}).get('tier', 'Tier 1')
        
        # Cost-based risk
        if estimated_cost > 2000:
            cost_risk = "High"
        elif estimated_cost > 500:
            cost_risk = "Moderate"
        else:
            cost_risk = "Low"
        
        # Tier-based considerations
        tier_multiplier = {'Tier 1': 1, 'Tier 2': 1.5, 'Tier 3': 2, 'Tier 4': 3}
        adjusted_cost = estimated_cost * tier_multiplier.get(tier, 1)
        
        return {
            'financial_risk': cost_risk,
            'estimated_monthly_cost': estimated_cost,
            'adjusted_cost': adjusted_cost,
            'tier': tier
        }
    
    def get_risk_level(self, score: int) -> str:
        """Convert risk score to risk level"""
        if score >= 5:
            return "High"
        elif score >= 3:
            return "Moderate"
        else:
            return "Low"
    
    def process(self, state: Dict) -> Dict:
        """Process risk assessment"""
        extracted_info = state.get('extracted_evidence', {})
        
        clinical_risk = self.calculate_clinical_risk(extracted_info)
        financial_risk = self.calculate_financial_risk(extracted_info)
        
        # Overall risk assessment
        overall_risk = "High" if clinical_risk['risk_level'] == "High" or financial_risk['financial_risk'] == "High" else "Moderate" if clinical_risk['risk_level'] == "Moderate" or financial_risk['financial_risk'] == "Moderate" else "Low"
        
        risk_assessment = {
            'clinical_risk': clinical_risk,
            'financial_risk': financial_risk,
            'overall_risk': overall_risk,
            'assessment_summary': f"Clinical: {clinical_risk['risk_level']}, Financial: {financial_risk['financial_risk']}"
        }
        
        state['risk_assessment'] = risk_assessment
        state['reasoning_chain'].append(f"Risk assessment completed: {overall_risk} risk")
        
        return state