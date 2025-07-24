import os
from typing import Optional, Union
from pydantic import BaseModel

from memory_agent import MemoryAgent
from utils import generate_prompt
from LLM_config import llm_config, llm_CDA_config

from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.user_proxy_agent import UserProxyAgent

print(os.getcwd())


class Component(BaseModel):
    AWS_NAME: Optional[str] = ""
    pros: Optional[str] = ""
    cons: Optional[str] = ""
    design: Optional[str] = ""
    details: Optional[str] = ""


class ComponentsMemory(BaseModel):
    Aim: Optional[str] = ""
    Platform: Optional[str] = ""
    Components: Optional[Union[list[Component], Component]] = [Component()]
    # output: str|None = ""

def create_agents():
    DEA = AssistantAgent(
        "DataEngineerAgent",
        description=generate_prompt("prompts/agents/data-engineer.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/data-engineer.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )

    IA = AssistantAgent(
        "InfrastructureAgent",
        description=generate_prompt("prompts/agents/infrastructure.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/infrastructure.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )


    MLA = AssistantAgent(
        "MachineLearningEngineerAgent",
        description=generate_prompt("prompts/agents/machine-learning.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/machine-learning.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )

    BOA = AssistantAgent(
        "BusinessObjectiveAgent",
        description=generate_prompt("prompts/agents/business-objective.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/business-objective.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )


    class CDMemory(BaseModel):
        PROPOSAL_COUNT: int | None = 0
        DISCUSSION_ROUND: int | None = 0
        CONCENSUS_COUNT: int | None = 0
        final_output_obtained: bool | None = False


    CDA = AssistantAgent(
        "ConversationDelegationAgent",
        description=generate_prompt("prompts/agents/conversation-delegation.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/conversation-delegation.prompt"),
        #structured_output=CDMemory,
        llm_config=llm_CDA_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="NEVER",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
        is_termination_msg=lambda msg: "-----END OF CONVERSATION-----" in msg["content"].lower()

    )


    KIA = AssistantAgent(
        "KownledgeIntergrationAgent",
        description=generate_prompt("prompts/agents/knowledge-integration.prompt"),
        # system_message = '''You are a Kownledge Intergration Engineer.
        # Your are great at summarising important meeting points. You are also working to maintain a shared document that is up-to-date with the design consensus.
        # Your role is critical in ensuring everyone in the discussion has mutual understanding of each other.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Summarise the conversations based on the full history, and update shared and agreed upon design/coding files.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges, and business objectives.
        #     - Output your summarise and document in full.''',
        system_message=generate_prompt("prompts/agents/knowledge-integration.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )

    ERA = AssistantAgent(
        "EveluateRefinementAgent",
        description=generate_prompt("prompts/agents/evaluate-and-refine.prompt"),
        # system_message = """You are a Evaluation and Refinement Analyst, your role is to ensure the integrity and reliability of the data pipeline. You will develop data validation rules, monitor data quality, and implement cleansing processes. Your task is to identify and rectify inconsistencies, ensuring the data is accurate and trustworthy for downstream analytics and decision-making processes.
        # Instructions:**
        #     - Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning or implementing tasks with deadlines.
        #     - Evaluate the design and coding proposed in the score out of 10 in the four criterea: Quality score, Efficiency score, Compliance score, Maintainability score.
        #     - Keep the conversation focused on design choices, technologies, and potential challenges.
        #     - Output your evaluations in. """,
        system_message=generate_prompt("prompts/agents/evaluate-and-refine.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        human_input_mode="TERMINATE",
        default_auto_reply="Conversation Delegation Agent has finished its conversation. ",
        function_map=None,  # No registered functions, by default it is None.
    )

    DJE = AssistantAgent(
        name="DocumentationEngineer",
        description=generate_prompt("prompts/agents/documentation.prompt"),
        system_message=generate_prompt("prompts/agents/documentation.prompt"),
        llm_config=llm_config,
        code_execution_config=False,
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        # llm_config=llm_config,
        code_execution_config=False,
        llm_config=llm_config,
        system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
    Otherwise, reply CONTINUE, and the reason why the task is not solved yet.""",
    )
    return CDA, DEA, MLA, IA, BOA, KIA, ERA, DJE, user_proxy
