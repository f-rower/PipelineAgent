import json

def generate_prompt(prompt_filepath):
    with open(prompt_filepath, "r") as f:
        prompt_template = f.read()
        return prompt_template

# def validate_delegator_message(msg):
#     if ":" in msg and not msg.startswith("ConversationDelegationAgent:"):
#         raise ValueError("Impersonation detected!")
#     return msg

def validate_delegator_message(sender, message, recipient, silent):
    """Ensure delegation agent doesn't speak for others"""
    if not message.startswith("ConversationDelegationAgent:"):
        raise ValueError(f"Invalid speaker format! Got: {message}")
    if any(role.lower() in message.lower() for role in roles):
        raise ValueError("Agent attempted to impersonate other roles!")
    return message


def validate_json_output(sender, message, recipient, silent):
    if "Finalization Step" in message:
        if "PIPELINE_OVERVIEW.json" not in message:
            raise ValueError("JSON output missing!")
        if not any(c.isdigit() for c in message):
            raise ValueError("Difficulty ratings missing!")
    return message

from collections import defaultdict


conversation_steps = [
    "Proposal: Collect initial designs",
    "Discussion: Challenge proposals", 
    "Consensus: Agree on architecture",
    "Finalization: Generate JSON output"  
]

class StateTracker:
    def __init__(self):
        self.state = defaultdict(int)
        self.required_proposals = {
            'MachineLearningEngineer', 
            'InfrastructureEngineer',
            'DataEngineer', 
            'BusinessObjectiveEngineer'
        }
    
    def track_proposals(self, sender, message, recipient, silent):
        print(sender)
        if sender in self.required_proposals:
            self.state['proposals'] += 1
            self.required_proposals.remove(sender)
        
        # Block early phase transitions
        if "Discussion Step" in message and self.state['proposals'] < 4:
            raise ValueError(f"Premature discussion! Only {self.state['proposals']}/4 proposals")
            
        return message

tracker = StateTracker()

def validate_phase_transition(sender, message, recipient, silent):
    current_phase = tracker.state.get('phase', 'proposal')
    
    transition_rules = {
        'proposal': {
            'allowed_triggers': ['Discussion Step'],
            'required_condition': tracker.state['proposals'] == 4
        },
        'discussion': {
            'allowed_triggers': ['Consensus Step'],
            'required_condition': tracker.state['discussion_rounds'] >= 12
        },
        'consensus': {
            'allowed_triggers': ['FINALIZATION'],
            'required_condition': 'agree' in message.lower()
        }
    }
    
    if any(trigger in message for trigger in transition_rules[current_phase]['allowed_triggers']):
        if not transition_rules[current_phase]['required_condition']:
            raise ValueError(f"Premature {current_phase} transition blocked")
    
    return message

def remove_thinking_output(sender, message, recipient, silent):
    return message.split("</think>")[-1]

def enforce_json_output(sender, message, recipient, silent):
    if "FINALIZATION" in message:
        if not message.endswith("DocumentationEngineer generate PIPELINE_OVERVIEW.json"):
            raise ValueError("Invalid finalization command format")
        
        # Queue JSON specialist as next speaker
        group_chat.speaker_selection_queue = ['DocumentationEngineer']
        
    elif sender == 'DocumentationEngineer':
        if not validate_json_structure(message):
            raise ValueError("Invalid JSON structure")
            
    return message

def validate_json_structure(content):
    required_fields = {
        "Platform", "Component 1", "Component 2",
        "Implementation difficulties", "Maintenance difficulties"
    }
    try:
        data = json.loads(content)
        return all(field in data for field in required_fields)
    except:
        return False

