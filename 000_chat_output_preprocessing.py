import json
import pandas as pd

def get_pipeline():
    with open("001_all_memory_agent_chat_responses.json", "r", encoding="utf-8") as f:
        assistant_agent_responses_1 = json.load(f)
    with open("002_all_memory_agent_chat_responses.json", "r", encoding="utf-8") as f_2:
        assistant_agent_responses_2 = json.load(f_2)

    # Load last message from each conversation
    assistant_data_pipeline_proposal_answers_1 = [result["result"][-1]["content"] for result in assistant_agent_responses_1]
    assistant_data_pipeline_proposal_answers_2 = [result["result"][-1]["content"] for result in assistant_agent_responses_2]
    

    assistant_data_pipeline_proposal_answers = []
    assistant_data_pipeline_proposal_answers.append([assistant_data_pipeline_proposal_answers_1,assistant_data_pipeline_proposal_answers_2])
    

    with open("all_memory_data_pipeline_proposal_answers_full_clean.json", "w", encoding="utf-8") as f:
        json.dump(assistant_data_pipeline_proposal_answers, f, indent=2, ensure_ascii=False)

"""Function to extract turn_counter from chat responses and save to a JSON file."""

def get_turn_counter():
    with open("001_assistant_agent_chat_responses.json", "r", encoding="utf-8") as f:
        agent_responses_1 = json.load(f)
    with open("002_assistant_agent_chat_responses.json", "r", encoding="utf-8") as f_2:
        agent_responses_2 = json.load(f_2)

    # Load turn_counter values from each conversation
    turn_counters_1 = [result["turn_counter"] for result in agent_responses_1]
    turn_counters_2 = [result["turn_counter"] for result in agent_responses_2]

    chat_turns = []
    chat_turns.append([turn_counters_1 + turn_counters_2])
    print(chat_turns)

    with open("001_assistant_agent_data_pipeline_chat_turns.json", "w", encoding="utf-8") as f:
        json.dump(chat_turns, f, indent=2, ensure_ascii=False)

def get_total_tokens():
    with open("001_all_memory_agent_chat_responses.json", "r", encoding="utf-8") as f:
        agent_responses_1 = json.load(f)
    with open("002_all_memory_agent_chat_responses.json", "r", encoding="utf-8") as f_2:
        agent_responses_2 = json.load(f_2)

    # Load turn_counter values from each conversation
    total_tokens_1 = [result["usage"]["usage_including_cached_inference"]["llama3.2:latest"]["total_tokens"] for result in agent_responses_1]
    total_tokens_2 = [result["usage"]["usage_including_cached_inference"]["llama3.2:latest"]["total_tokens"] for result in agent_responses_2]

    total_tokens = []
    total_tokens.append([total_tokens_1 + total_tokens_2])
    print(total_tokens)

    with open("001_intrinsic_memory_agent_data_pipeline_total_tokens.json", "w", encoding="utf-8") as f:
        json.dump(total_tokens, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    #get_pipeline()
    #get_turn_counter()
    get_total_tokens()
    print("Data preprocessing completed successfully.")