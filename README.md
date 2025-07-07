PipelineAgent
---

# File Structure
agents.py

assistant-test.ipynb

chat.ipynb

config.yaml

customegroupchat.py

groupchat.py

instruct_last_agent.py

LLM_config.py

memory_agent.py

test.py

utils.py

# Notes
- 

# Changelog of files
- LLM_config.py
    - Changed all models to LLama 3.2, running locally through Ollama
- config.yaml
    - I don't think it's even needed for LLM_config.py? The module autogen.config_list_from_json is being loaded into LLM_config.py, but never actually called or used...
- agents.py
    - Created actual instances of ComponentsMemory() instead of just doing random shit