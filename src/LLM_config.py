import os

from autogen import config_list_from_json
from pydantic import BaseModel
class Component(BaseModel):
        pros: str
        cons: str
        design: str
        details: str

class ComponentsMemory (BaseModel):
        aim: str
        Platform: str
        Components: list[Component]
        output: str

config_list = [
    {
        #"provider": "ollama",
        "model": "llama3.2:latest",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        # "response_format":ComponentsMemory, 
    },
    # {
    #     "model": "claude",
    #     "base_url": "http://localhost:11434/v1",
    #     "api_key": "ollama",
    # },
#     {
#     "model": "qwen2.5-coder:7b",
#     "base_url": "http://localhost:11434/v1",
#     "api_key": "ollama",
#   }
]


llm_config = {
    "timeout": 600,
    "cache_seed": None,
    "config_list": config_list,
    "temperature": 0.02,
}

class CDMemory(BaseModel):
    num_proposals:int|None =0
    num_discussions: int|None =0
    num_consensus: int|None =0
    final_output_obtained: bool|None=False
    output: str

CDA_config_list = [
    {
        #"provider": "ollama",
        "model": "llama3.2:latest",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        # "response_format":CDMemory, 
    }]

llm_CDA_config = {
    "timeout": 600,
    "cache_seed": None,
    "config_list": CDA_config_list,
    "temperature": 0.02,
    # "max_tokens": 80,  # Force brief responses
    # "stop": ["\n\n"],  # Prevent verbose output

}

