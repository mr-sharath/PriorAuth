from typing import Dict, List, Any
from datetime import datetime, timedelta

class DecisionMakerAgent:
    """Make final prior authorization decisions based on all available information"""
    
    def __init__(self):
        self.decision_criteria = {
            'auto_approve': {
                'guideline_compliant': True,
                'max_risk': 'Moderate',
                'max_cost': 1000
            },
            'auto_deny': {
                'guideline_compliant': False,
                'high_risk_factors': ['Emergency override not applicable']
            }
        }
    
    def make_decision(self, guideline_compliance: Dict, risk_assessment: Dict, extracted_info: Dict) -> Dict:
        """Make final PA decision based on all available information"""
        
        # Get key decision factors
        is_compliant = guideline_compliance.get('overall_compliant', False)
        overall_risk = risk_assessment.get('overall_risk', 'High')
        urgency = extracted_info.get('current_request', {}).get('urgency', 'Routine')
        estimated_cost = extracted_info.get('insurance_info', {}).get('estimated_cost', 0)
        
        # Decision logic
        if urgency == 'Emergency':
            decision = 'APPROVED'
            reason = 'Emergency override - immediate approval for urgent medical need'
            confidence = 0.95
        elif is_compliant and overall_risk in ['Low', 'Moderate'] and estimated_cost <= 2000:
            decision = 'APPROVED'
            reason = 'Meets all clinical guidelines and cost criteria'
            confidence = 0.90
        elif is_compliant and overall_risk == 'High':
            decision = 'APPROVED_WITH_CONDITIONS'
            reason = 'Approved with enhanced monitoring due to high risk factors'
            confidence = 0.75
        elif not is_compliant and urgency == 'Urgent':
            decision = 'PENDING_REVIEW'
            reason = 'Manual review required - urgent case with guideline non-compliance'
            confidence = 0.60
        elif not is_compliant:
            decision = 'DENIED'
            reason = 'Does not meet clinical guidelines - step therapy or cost limits exceeded'
            confidence = 0.85
        else:
            decision = 'PENDING_REVIEW'
            reason = 'Manual review required - complex case requiring clinical expertise'
            confidence = 0.50
        
        return {
            'decision': decision,
            'reason': reason,
            'confidence': confidence,
            'decision_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_recommendations(self, decision_data: Dict, extracted_info: Dict, guideline_compliance: Dict) -> List[str]:
        """Generate actionable recommendations based on decision"""
        recommendations = []
        
        decision = decision_data.get('decision', '')
        
        if decision == 'DENIED':
            # Suggest alternatives
            if not guideline_compliance.get('step_therapy', {}).get('compliant', True):
                recommendations.append("Try first-line therapy as recommended in clinical guidelines")
            
            if not guideline_compliance.get('cost_limits', {}).get('compliant', True):
                recommendations.append("Consider generic alternatives or patient assistance programs")
        
        elif decision == 'APPROVED_WITH_CONDITIONS':
            recommendations.append("Enhanced monitoring required due to risk factors")
            recommendations.append("Schedule follow-up appointment in 30 days")
        
        elif decision == 'PENDING_REVIEW':
            recommendations.append("Submit additional clinical documentation")
            recommendations.append("Expected review time: 24-48 hours")
        
        return recommendations
    
    def process(self, state: Dict) -> Dict:
        """Process final decision making"""
        guideline_compliance = state.get('guideline_compliance', {})
        risk_assessment = state.get('risk_assessment', {})
        extracted_info = state.get('extracted_evidence', {})
        
        # Make decision
        decision_data = self.make_decision(guideline_compliance, risk_assessment, extracted_info)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(decision_data, extracted_info, guideline_compliance)
        
        final_decision = {
            **decision_data,
            'recommendations': recommendations,
            'supporting_evidence': {
                'guideline_compliant': guideline_compliance.get('overall_compliant', False),
                'risk_level': risk_assessment.get('overall_risk', 'Unknown'),
                'key_factors': [
                    f"Diagnosis: {extracted_info.get('medical_history', {}).get('primary_diagnosis', 'Unknown')}",
                    f"Medication: {extracted_info.get('current_request', {}).get('medication', 'Unknown')}",
                    f"Urgency: {extracted_info.get('current_request', {}).get('urgency', 'Unknown')}"
                ]
            }
        }
        
        state['final_decision'] = final_decision
        state['reasoning_chain'].append(f"Final decision: {decision_data['decision']} - {decision_data['reason']}")
        
        return state