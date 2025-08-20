# src/langgraph_workflow.py

from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import END
from agents.medical_extractor import MedicalExtractorAgent
from agents.guidelines_checker import GuidelinesCheckerAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.decision_maker import DecisionMakerAgent

class PAState(TypedDict):
    """State definition for Prior Authorization workflow"""
    patient_data: Dict[str, Any]
    extracted_evidence: Dict[str, Any]
    guideline_compliance: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    final_decision: Dict[str, Any]
    reasoning_chain: List[str]
    workflow_status: str
    error_message: str

class PriorAuthWorkflow:
    """LangGraph workflow for Prior Authorization processing"""
    
    def __init__(self):
        self.medical_extractor = MedicalExtractorAgent()
        self.guidelines_checker = GuidelinesCheckerAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.decision_maker = DecisionMakerAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define the workflow graph
        workflow = StateGraph(PAState)
        
        # Add nodes
        workflow.add_node("extract_medical_info", self._extract_medical_info_node)
        workflow.add_node("check_guidelines", self._check_guidelines_node)
        workflow.add_node("assess_risk", self._assess_risk_node)
        workflow.add_node("make_decision", self._make_decision_node)
        
        # Define the workflow edges
        workflow.add_edge("extract_medical_info", "check_guidelines")
        workflow.add_edge("check_guidelines", "assess_risk")
        workflow.add_edge("assess_risk", "make_decision")
        workflow.add_edge("make_decision", END)
        
        # Set entry point
        workflow.set_entry_point("extract_medical_info")
        
        return workflow.compile()
    
    def _extract_medical_info_node(self, state: PAState) -> PAState:
        """Node for medical information extraction"""
        try:
            state['workflow_status'] = "Extracting medical information..."
            updated_state = self.medical_extractor.process(dict(state))
            state.update(updated_state)
            return state
        except Exception as e:
            state['error_message'] = f"Error in medical extraction: {str(e)}"
            state['workflow_status'] = "Error"
            return state
    
    def _check_guidelines_node(self, state: PAState) -> PAState:
        """Node for guidelines compliance checking"""
        try:
            state['workflow_status'] = "Checking clinical guidelines..."
            updated_state = self.guidelines_checker.process(dict(state))
            state.update(updated_state)
            return state
        except Exception as e:
            state['error_message'] = f"Error in guidelines check: {str(e)}"
            state['workflow_status'] = "Error"
            return state
    
    def _assess_risk_node(self, state: PAState) -> PAState:
        """Node for risk assessment"""
        try:
            state['workflow_status'] = "Assessing clinical and financial risks..."
            updated_state = self.risk_assessor.process(dict(state))
            state.update(updated_state)
            return state
        except Exception as e:
            state['error_message'] = f"Error in risk assessment: {str(e)}"
            state['workflow_status'] = "Error"
            return state
    
    def _make_decision_node(self, state: PAState) -> PAState:
        """Node for final decision making"""
        try:
            state['workflow_status'] = "Making final decision..."
            updated_state = self.decision_maker.process(dict(state))
            state.update(updated_state)
            state['workflow_status'] = "Completed"
            return state
        except Exception as e:
            state['error_message'] = f"Error in decision making: {str(e)}"
            state['workflow_status'] = "Error"
            return state
    
    def process_pa_request(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a prior authorization request through the workflow"""
        
        # Initialize state
        initial_state = PAState(
            patient_data=patient_data,
            extracted_evidence={},
            guideline_compliance={},
            risk_assessment={},
            final_decision={},
            reasoning_chain=[],
            workflow_status="Starting workflow...",
            error_message=""
        )
        
        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            return dict(final_state)
        except Exception as e:
            return {
                **initial_state,
                'error_message': f"Workflow execution error: {str(e)}",
                'workflow_status': "Failed"
            }
    
    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow"""
        return """
        Prior Authorization Workflow:
        
        1. Extract Medical Info
           ↓
        2. Check Guidelines
           ↓
        3. Assess Risk
           ↓
        4. Make Decision
           ↓
        5. Generate Report
        """

# Example usage and testing
if __name__ == "__main__":
    # Test the workflow with sample data
    workflow = PriorAuthWorkflow()
    
    sample_patient = {
        'patient_id': 'PT000001',
        'name': 'John Doe',
        'age': 45,
        'gender': 'M',
        'diagnosis': 'Rheumatoid Arthritis',
        'icd_code': 'M05.9',
        'requested_medication': 'Adalimumab',
        'dosage': '40mg bi-weekly',
        'duration': '6 months',
        'previous_treatments': ['Methotrexate'],
        'allergies': 'NKDA',
        'insurance_tier': 'Tier 3',
        'prior_auth_history': 'None',
        'cost_per_month': 2500,
        'urgency': 'Routine'
    }
    
    # Process the request
    result = workflow.process_pa_request(sample_patient)
    
    # Print results
    print("Workflow Status:", result.get('workflow_status'))
    print("Final Decision:", result.get('final_decision', {}).get('decision'))
    print("Reasoning Chain:", result.get('reasoning_chain'))