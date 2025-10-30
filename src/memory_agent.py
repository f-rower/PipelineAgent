import asyncio
import contextvars
import json
from pyexpat.errors import messages
import regex

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from pydantic import BaseModel


from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.agent import Agent
from autogen.oai.client import OpenAIWrapper
from autogen.io.base import IOStream
from autogen.formatting_utils import colored


class MemoryAgent(AssistantAgent):

    DEFAULT_MEMORY_UPDATE_PROMPT = """Use the entire history of the groupchat (presented before this message) to 
    populate and update the current memory json with factual imformation. 

    *** OUTPUT SHOULD ONLY BE VALID JSON.  
    Be very careful to not include anything that renders the output not directly loadable with json.loads(). *** 
    
    For context, current memory: {memory}. 

    Newest response by yourself: {new_response}
    
    Updated memory in JSON format: """

    DEFAULT_MEMORY_REPLY_PROMPT = """Using the above instruction, group chat history, and memory json with important information from the chat history, to solve the conversation delegation agent's task. 

    Respond according to the ***last instruction from Conversation delegation agent***. 

    For context, current memory from chat based on your own outputs: {memory}. 
    
    Newest instruction: {instruction}. 
    
    Output: """

    def __init__(
        self,
        structured_output: BaseModel,
        memory_update_prompt: Optional[str] = None,
        memory_reply_prompt: Optional[str] = None,

        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.strucutred_output = structured_output
        #self.memory_json = self.strucutred_output.model_dump(mode='json')
        self.memory_json = self.strucutred_output().model_dump()
        self.memory_update_prompt = (
            memory_update_prompt
            if memory_update_prompt != None
            else self.DEFAULT_MEMORY_UPDATE_PROMPT
        )
        self.memory_reply_prompt = (
            memory_reply_prompt
            if memory_reply_prompt != None
            else self.DEFAULT_MEMORY_REPLY_PROMPT
        )
        self.replace_reply_func(
            ConversableAgent.generate_oai_reply, MemoryAgent.generate_oai_reply
        )
        strucutred_output_config = self.llm_config.copy()
        strucutred_output_config['config_list'][0].response_format = self.strucutred_output

        self.client_memory = OpenAIWrapper(**strucutred_output_config)



    def memory_to_structured_output(self) -> BaseModel:
        from pydantic import create_model
        def dict_model(name:str,dict_def:dict):
            fields = {}
            for field_name,value in dict_def.items():
                if isinstance(value,tuple):
                    fields[field_name]=value
                elif isinstance(value,dict):
                    fields[field_name]=(dict_model(f'{name}_{field_name}',value),...)
                else:
                    raise ValueError(f"Field {field_name}:{value} has invalid syntax")
            return create_model(name,**fields)

        model = dict_model("memory",self.memory)
        return model

    @property
    def memory(self) -> dict:
        """Return the system message."""
        return self.memory_json

    @property
    def memory_prompt(self) -> str:
        """Return the system message."""
        return self.memory_prompt


    def generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        import pdb

        """Generate a reply using autogen.oai."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
            
        memory_instruction = self.memory_reply_prompt.format(
            memory=self.memory_json, instruction=messages[-1]['content']
        )
        memory_instruction = [{"content": memory_instruction, "role": "user"}]
        iostream = IOStream.get_default()

        iostream.print(f'memory response: {memory_instruction}')
        #iostream.print(f'messages: {messages}')

        extracted_response = self._generate_oai_reply_from_client(
            client,
            self._oai_system_message + messages[:-1] + memory_instruction,
            self.client_cache,
            
        )
        #iostream.print(f'extracted_response: {extracted_response}')
        instruction = [
            {
                "content": self.memory_update_prompt.format(
                    memory=self.memory_json, new_response=extracted_response
                ),
                "name": self.name,
                "role": "user",
            }
        ]
        memory_response = self._generate_oai_reply_from_client(
            self.client_memory, messages + instruction, self.client_cache
        )
        #iostream.print(f'instruction: {instruction}')

        iostream.print(colored("***** raw Memory *****", "green"), flush=True)
        iostream.print(memory_response, flush=True)

        # pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
        # a = pattern.findall(memory_response.strip())
    
        try:
            self.memory_json = json.loads(memory_response)
        # print the message received
        except:
            iostream.print(colored("***** loaded Memory *****", "green"), flush=True)
            iostream.print("illegal format", flush=True)
        else:
            iostream.print(colored("***** loaded Memory *****", "green"), flush=True)
            iostream.print(self.memory_json, flush=True)

        return (
            (False, None) if extracted_response is None else (True, extracted_response)
        )
    async def a_generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai asynchronously."""
        iostream = IOStream.get_default()
        parent_context = contextvars.copy_context()

        def _generate_oai_reply(
            self, iostream: IOStream, *args: Any, **kwargs: Any
        ) -> Tuple[bool, Union[str, Dict, None]]:
            with IOStream.set_default(iostream):
                return self.generate_oai_reply(*args, **kwargs)

        memory_instruction = self.memory_reply_prompt.format(memory=self.memory_json)

        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: parent_context.run(
                _generate_oai_reply,
                self=self,
                iostream=iostream,
                messages=messages + memory_instruction,
                sender=sender,
                config=config,
            ),
        )

    # def send(
    #     self,
    #     message: Union[Dict, str],
    #     recipient: Agent,
    #     request_reply: Optional[bool] = None,
    #     silent: Optional[bool] = False,
    # ):
    #     """Send a message to another agent.

    #     Args:
    #         message (dict or str): message to be sent.
    #             The message could contain the following fields:
    #             - content (str or List): Required, the content of the message. (Can be None)
    #             - function_call (str): the name of the function to be called.
    #             - name (str): the name of the function to be called.
    #             - role (str): the role of the message, any role that is not "function"
    #                 will be modified to "assistant".
    #             - context (dict): the context of the message, which will be passed to
    #                 [OpenAIWrapper.create](../oai/client#create).
    #                 For example, one agent can send a message A as:
    #     ```python
    #     {
    #         "content": lambda context: context["use_tool_msg"],
    #         "context": {
    #             "use_tool_msg": "Use tool X if they are relevant."
    #         }
    #     }
    #     ```
    #                 Next time, one agent can send a message B with a different "use_tool_msg".
    #                 Then the content of message A will be refreshed to the new "use_tool_msg".
    #                 So effectively, this provides a way for an agent to send a "link" and modify
    #                 the content of the "link" later.
    #         recipient (Agent): the recipient of the message.
    #         request_reply (bool or None): whether to request a reply from the recipient.
    #         silent (bool or None): (Experimental) whether to print the message sent.

    #     Raises:
    #         ValueError: if the message can't be converted into a valid ChatCompletion message.
    #     """
    #     memory = self._update_memory(messages=[message], sender=self)
    #     iostream = IOStream.get_default()
    #     # print the message received
    #     iostream.print(colored("***** Memory *****", "green"), flush=True)
    #     iostream.print(self.memory_json, flush=True)

    #     message = self._process_message_before_send(message, recipient, ConversableAgent._is_silent(self, silent))
    #     # When the agent composes and sends the message, the role of the message is "assistant"
    #     # unless it's "function".
    #     valid = self._append_oai_message(message, "assistant", recipient, is_sending=True)
    #     if valid:
    #         recipient.receive(message, self, request_reply, silent)
    #     else:
    #         raise ValueError(
    #             "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
    #         )

    # async def a_send(
    #     self,
    #     message: Union[Dict, str],
    #     recipient: Agent,
    #     request_reply: Optional[bool] = None,
    #     silent: Optional[bool] = False,
    # ):
    #     """(async) Send a message to another agent.

    #     Args:
    #         message (dict or str): message to be sent.
    #             The message could contain the following fields:
    #             - content (str or List): Required, the content of the message. (Can be None)
    #             - function_call (str): the name of the function to be called.
    #             - name (str): the name of the function to be called.
    #             - role (str): the role of the message, any role that is not "function"
    #                 will be modified to "assistant".
    #             - context (dict): the context of the message, which will be passed to
    #                 [OpenAIWrapper.create](../oai/client#create).
    #                 For example, one agent can send a message A as:
    #     ```python
    #     {
    #         "content": lambda context: context["use_tool_msg"],
    #         "context": {
    #             "use_tool_msg": "Use tool X if they are relevant."
    #         }
    #     }
    #     ```
    #                 Next time, one agent can send a message B with a different "use_tool_msg".
    #                 Then the content of message A will be refreshed to the new "use_tool_msg".
    #                 So effectively, this provides a way for an agent to send a "link" and modify
    #                 the content of the "link" later.
    #         recipient (Agent): the recipient of the message.
    #         request_reply (bool or None): whether to request a reply from the recipient.
    #         silent (bool or None): (Experimental) whether to print the message sent.

    #     Raises:
    #         ValueError: if the message can't be converted into a valid ChatCompletion message.
    #     """
    #     message = await self._a_process_message_before_send(
    #         message, recipient, self._is_silent(self, silent)
    #     )
    #     # When the agent composes and sends the message, the role of the message is "assistant"
    #     # unless it's "function".
    #     valid = self._append_oai_message(message, "assistant", recipient, is_sending=True)
    #     if valid:
    #         await recipient.a_receive(message, self, request_reply, silent)
    #     else:
    #         raise ValueError(
    #             "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
    #         )
