from autogen import GroupChat,GroupChatManager
# from customegroupchat import customised_groupchat, customised_groupchatmanager
from list_memory_agents import DEA, MLA, IA, BOA, CDA, KIA, ERA, DJE, user_proxy
from LLM_config import llm_config
from utils import generate_prompt, validate_json_output, StateTracker, validate_phase_transition, remove_thinking_output

"""A multiagent system composed solely of assistant agents without intrinsic memory"""
tracker = StateTracker()

# DEA.register_hook(hookable_method="process_message_before_send",hook=validate_delegator_message)
DEA.register_hook(hook = remove_thinking_output, hookable_method = "process_message_before_send")
DEA.register_hook(hook=tracker.track_proposals, hookable_method="process_message_before_send")
DEA.register_hook(hook=validate_phase_transition, hookable_method="process_message_before_send")
DJE.register_hook(hook = validate_json_output, hookable_method = "process_message_before_send")

worker_counter = 0
turn_counter = 1
# turn_counter = -1
def custom_speaker_selection_func(last_speaker, groupchat: GroupChat):
    workers = [BOA, DEA, MLA, IA]
    # if "final" groupchat.last_message
    global turn_counter
    turn_counter += 1
    print(turn_counter)
    print(f'groupchat.messages[-1]: {groupchat.messages[-1]}')
    if "FINALIZATION" in groupchat.messages[-1]['content']:
        print("FINALIZATION found in the last message.")
        return DJE
    if last_speaker is user_proxy: 
        return CDA
    if last_speaker is CDA: 
        global worker_counter
        w = workers[worker_counter%4]
        worker_counter += 1
        return w
    elif last_speaker in workers:
        if worker_counter %4 == 0:
            return KIA
        else: 
            return CDA
    elif last_speaker is KIA:
            return ERA
    elif last_speaker is ERA:
            return CDA

    

group_chat = GroupChat(
    [CDA]+[DEA, MLA, IA, BOA, KIA, ERA, DJE, user_proxy],
    messages=[],
    select_speaker_message_template=generate_prompt("prompts/select_speaker_message_template.prompt"),
    select_speaker_prompt_template=generate_prompt("prompts/select_speaker_prompt_template.prompt"),
    select_speaker_auto_multiple_template=generate_prompt("prompts/select_speaker_auto_multiple_template.prompt"),
    select_speaker_auto_none_template=generate_prompt("prompts/select_speaker_auto_none_template.prompt"),
    speaker_selection_method=custom_speaker_selection_func,
    # speaker_selection_method=lambda **kwargs: (
    #     # Force proposal order
    #     ['MachineLearningEngineer', 'InfrastructureEngineer',
    #      'DataEngineer', 'BusinessObjectiveEngineer'] if tracker.state['proposals'] < 4 
    #     else kwargs['agents']  # Release control after 4 proposals
    # ),
    # phase_lock={
    #     'proposal': {'min_messages': 4, 'max_messages': 4},
    #     'discussion': {'min_messages': 12, 'max_messages': 12},
    #     'consensus': {'min_messages': 4}
    # },
    max_round=80,
    allow_repeat_speaker=False,

    #termination_condition=lambda x: "PIPELINE_OVERVIEW.json" in x[-1]["content"]
)
group_chat.reset()


chat_manager = GroupChatManager(groupchat=group_chat)

generated_request = """This discussion session is set up to discuss the best data pipeline for a real time data intensive machine learning training and inference self driving application. The goal is to discuss and find consensus on how to set up the data pipeline, including each component in the datapipeline. 
You can assume that we have access to aws. 

**Data Description:**
Real-time data of cars driving in street. 
There are 6 camera sources with data in .jpg format; 1 lidar source in .pcd.bin format; and 5 radar sources with data in .pcd format. 

**Discussion and Design:**
- Emphasise comprehensive understanding of the data sources, processing requirements, and desired outcomes.
- Encourage each other to engage in an open discussion on potential technologies, components, and architectures that can handle the diverse data streams and real-time nature of the data.
- Keep the conversation on design and evaluating the pros and cons of different design choices, considering scalability, maintainability, and cost-effectiveness.
- The team should agrees on a final architectural design, justifying the choices made.
- The team should produce the required the document PIPELINE_OVERVIEW.json.

**Final Output:**
- Produce a concise summary of the agreed-upon pipeline architecture, highlighting its key components and connections.
- Provide a high-level plan and rationale for the design, explaining why it is well-suited for the given data and use case.
- Estimate the cloud resources, implementation efforts, and associated costs, providing a rough breakdown and complexity rating.
- Generate a `PIPELINE_OVERVIEW.json` file, detailing the proposed complete architecture in JSON format with the following fields: 
 - “Platform“: A cloud service provider’s name if the cloud solution is the best, or “local server” if locally hosted servers are preferred. 
 - “Component 1”: The first component in the pipeline framework. 
 - “Component 2”: The second component in the pipeline framework. Continue until all required components are listed. 
 - “Implementation difficulties": A rating from 1 to 10 (lowest to highest). 
 - “Maintainess difficulties”: A rating from 1 to 10 (lowest to highest). 

**Instructions:**
- Remember, this is a collaborative design discussion, not a project execution. Refrain from assigning tasks with deadlines.
- Keep the conversation focused on architectural choices, technologies, and potential challenges.
- Emphasize the importance of a well-thought-out design.
"""

groupchat_result = user_proxy.initiate_chat(
    chat_manager, message=generated_request
)