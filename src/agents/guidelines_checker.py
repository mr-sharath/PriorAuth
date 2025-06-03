from typing import Dict, List, Any
import json

class GuidelinesCheckerAgent:
    """Check medical requests against clinical guidelines and formulary rules"""
    
    def __init__(self, guidelines_path: str = "data/pa_guidelines.json"):
        self.guidelines = self.load_guidelines(guidelines_path)
    
    def load_guidelines(self, path: str) -> Dict:
        """Load clinical guidelines from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback guidelines if file not found
            return {
                "guidelines": {
                    "Rheumatoid Arthritis": {
                        "first_line": ["Methotrexate"],
                        "second_line": ["Adalimumab", "Etanercept"],
                        "step_therapy_required": True,
                        "duration_limit": "6 months initial"
                    },
                    "Type 2 Diabetes": {
                        "first_line": ["Metformin"],
                        "second_line": ["Insulin", "Semaglutide"],
                        "step_therapy_required": True,
                        "duration_limit": "12 months"
                    }
                },
                "general_rules": {
                    "max_cost_tier_4": 3000,
                    "emergency_override": True
                }
            }
    
    def check_step_therapy(self, diagnosis: str, requested_med: str, previous_treatments: List[str]) -> Dict:
        """Check if step therapy requirements are met"""
        guideline = self.guidelines["guidelines"].get(diagnosis, {})
        
        if not guideline.get("step_therapy_required", False):
            return {"compliant": True, "reason": "Step therapy not required"}
        
        first_line = guideline.get("first_line", [])
        second_line = guideline.get("second_line", [])
        
        # Check if requesting second-line without trying first-line
        if requested_med in second_line:
            first_line_tried = any(med in previous_treatments for med in first_line)
            if not first_line_tried:
                return {
                    "compliant": False,
                    "reason": f"Must try first-line therapy: {', '.join(first_line)}"
                }
        
        return {"compliant": True, "reason": "Step therapy requirements met"}
    
    def check_cost_limits(self, insurance_tier: str, estimated_cost: int) -> Dict:
        """Check if medication cost exceeds tier limits"""
        max_cost = self.guidelines["general_rules"].get("max_cost_tier_4", 3000)
        
        if insurance_tier == "Tier 4" and estimated_cost > max_cost:
            return {
                "compliant": False,
                "reason": f"Cost ${estimated_cost} exceeds Tier 4 limit ${max_cost}"
            }
        
        return {"compliant": True, "reason": "Cost within acceptable limits"}
    
    def process(self, state: Dict) -> Dict:
        """Process guidelines checking"""
        extracted_info = state.get('extracted_evidence', {})
        
        diagnosis = extracted_info.get('medical_history', {}).get('primary_diagnosis', '')
        requested_med = extracted_info.get('current_request', {}).get('medication', '')
        previous_treatments = extracted_info.get('medical_history', {}).get('previous_treatments', [])
        insurance_tier = extracted_info.get('insurance_info', {}).get('tier', '')
        estimated_cost = extracted_info.get('insurance_info', {}).get('estimated_cost', 0)
        
        # Check step therapy
        step_therapy_result = self.check_step_therapy(diagnosis, requested_med, previous_treatments)
        
        # Check cost limits
        cost_result = self.check_cost_limits(insurance_tier, estimated_cost)
        
        guidelines_compliance = {
            'step_therapy': step_therapy_result,
            'cost_limits': cost_result,
            'overall_compliant': step_therapy_result['compliant'] and cost_result['compliant']
        }
        
        state['guideline_compliance'] = guidelines_compliance
        state['reasoning_chain'].append(f"Guidelines check: {'Compliant' if guidelines_compliance['overall_compliant'] else 'Non-compliant'}")
        
        return state