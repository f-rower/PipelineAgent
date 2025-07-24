import json
import pandas as pd

with open("001_assistant_agent_chat_responses.json", "r", encoding="utf-8") as f:
    assistant_agent_responses_1 = json.load(f)
with open("002_assistant_agent_chat_responses.json", "r", encoding="utf-8") as f_2:
    assistant_agent_responses_2 = json.load(f_2)

# Load only the responses from businessobjectiveagent
assistant_data_pipeline_proposal_answers_1 = [result["result"][-1]["content"] for result in assistant_agent_responses_1]
assistant_data_pipeline_proposal_answers_2 = [result["result"][-1]["content"] for result in assistant_agent_responses_2]
#business_objective_agent_responses = [result for result in assistant_agent_responses_1 if result["name"]=="BusinessObjectiveAgent"]  

assistant_data_pipeline_proposal_answers = []
assistant_data_pipeline_proposal_answers.append([assistant_data_pipeline_proposal_answers_1,assistant_data_pipeline_proposal_answers_2])
print(assistant_data_pipeline_proposal_answers)

with open("assistant_data_pipeline_proposal_answers_full_clean.json", "w", encoding="utf-8") as f:
    json.dump(assistant_data_pipeline_proposal_answers, f, indent=2, ensure_ascii=False)