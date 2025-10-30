import json
import pandas as pd

with open("002_intrinsic_memory_agent_chat_responses.json", "r", encoding="utf-8") as f:
    intrinsic_memory_agent_responses_1 = json.load(f)
with open("intrinsic_memory_agent_chat_responses.json", "r", encoding="utf-8") as f_2:
    intrinsic_memory_agent_responses_2 = json.load(f_2)

# Load only the responses from businessobjectiveagent
intrinsic_memory_data_pipeline_proposal_answers_1 = [result["result"][-1]["content"] for result in intrinsic_memory_agent_responses_1]
intrinsic_memory_data_pipeline_proposal_answers_2 = [result["result"][-1]["content"] for result in intrinsic_memory_agent_responses_2]
#business_objective_agent_responses = [result for result in intrinsic_memory_agent_responses_1 if result["name"]=="BusinessObjectiveAgent"]  

intrinsic_memory_data_pipeline_proposal_answers = []
intrinsic_memory_data_pipeline_proposal_answers.append([intrinsic_memory_data_pipeline_proposal_answers_1,intrinsic_memory_data_pipeline_proposal_answers_2])
print(intrinsic_memory_data_pipeline_proposal_answers)

with open("intrinsic_memory_data_pipeline_proposal_answers_full_clean.json", "w", encoding="utf-8") as f:
    json.dump(intrinsic_memory_data_pipeline_proposal_answers, f, indent=2, ensure_ascii=False)