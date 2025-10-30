import sys
import logging
import json 
from typing import Optional, Literal, Union, Dict, List, Tuple
from dataclasses import dataclass
from autogen import GroupChat, GroupChatManager, ConversableAgent, Agent
from autogen.exception_utils import NoEligibleSpeaker
from autogen.formatting_utils import colored
from autogen.io.base import IOStream

logger = logging.getLogger(__name__)

@dataclass
class customised_groupchat(GroupChat):
    def select_speaker_msg(self, agents: Optional[List[Agent]] = None) -> str:
        return_msg = self.select_speaker_message_template
        return return_msg
    def select_speaker_prompt(self, agents: Optional[List[Agent]] = None) -> str:
        return_prompt = self.select_speaker_prompt_template
        return return_prompt
    def _validate_speaker_name(
        self, recipient, messages, sender, config, attempts_left, attempt, agents
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Validates the speaker response for each round in the internal 2-agent
        chat within the  auto select speaker method.

        Used by auto_select_speaker and a_auto_select_speaker.
        """

        # Output the query and requery results
        if self.select_speaker_auto_verbose:
            iostream = IOStream.get_default()

        # Validate the speaker name selected
        select_name = messages[-1]["content"].strip()

        mentions = self._mentioned_agents(select_name, agents)

        if len(mentions) == 1:
            # Success on retry, we have just one name mentioned
            selected_agent_name = next(iter(mentions))

            # Add the selected agent to the response so we can return it
            messages.append({"role": "user", "content": f"[AGENT SELECTED]{selected_agent_name}"})

            if self.select_speaker_auto_verbose:
                iostream.print(
                    colored(
                        f">>>>>>>> Select speaker attempt {attempt} of {attempt + attempts_left} successfully selected: {selected_agent_name}",
                        "green",
                    ),
                    flush=True,
                )

        elif len(mentions) > 1:
            # More than one name on requery so add additional reminder prompt for next retry

            if self.select_speaker_auto_verbose:
                iostream.print(
                    colored(
                        f">>>>>>>> Select speaker attempt {attempt} of {attempt + attempts_left} failed as it included multiple agent names.",
                        "red",
                    ),
                    flush=True,
                )

            if attempts_left:
                # Message to return to the chat for the next attempt
                # agentlist = [agent.name for agent in agents]

                return True, {
                    "content": self.select_speaker_auto_multiple_template,
                    "name": "checking_agent",
                    "override_role": self.role_for_select_speaker_messages,
                }
            else:
                # Final failure, no attempts left
                messages.append(
                    {
                        "role": "user",
                        "content": f"[AGENT SELECTION FAILED]Select speaker attempt #{attempt} of {attempt + attempts_left} failed as it returned multiple names.",
                    }
                )

        else:
            # No names at all on requery so add additional reminder prompt for next retry

            if self.select_speaker_auto_verbose:
                iostream.print(
                    colored(
                        f">>>>>>>> Select speaker attempt #{attempt} failed as it did not include any agent names.",
                        "red",
                    ),
                    flush=True,
                )

            if attempts_left:
                # Message to return to the chat for the next attempt

                return True, {
                    "content": self.select_speaker_auto_none_template,
                    "name": "checking_agent",
                    "override_role": self.role_for_select_speaker_messages,
                }
            else:
                # Final failure, no attempts left
                messages.append(
                    {
                        "role": "user",
                        "content": f"[AGENT SELECTION FAILED]Select speaker attempt #{attempt} of {attempt + attempts_left} failed as it did not include any agent names.",
                    }
                )
        return True, None
    
    def _process_speaker_selection_result(self, result, last_speaker: ConversableAgent, agents: Optional[List[Agent]]):
        """Checks the result of the auto_select_speaker function, returning the
        agent to speak.
        Used by auto_select_speaker and a_auto_select_speaker."""
        if len(result.chat_history) > 0:
            # Use the final message, which will have the selected agent or reason for failure
            final_message = result.chat_history[-1]["content"]
            iostream = IOStream.get_default()
            iostream.print(final_message)
            final_message = json.load(final_message)
            speaker = final_message["speaker"]
            instruction_message = final_message["instruction"]

            if speaker:
                # Have successfully selected an agent, return it
                return self.agent_by_name(speaker),instruction_message

            else:  # "[AGENT SELECTION FAILED]"
                # Failed to select an agent, so we'll select the next agent in the list
                next_agent = self.next_agent(last_speaker, agents)

                # No agent, return the failed reason
                return next_agent, None
            
    def _create_internal_agents(
        self, agents, max_attempts, messages, validate_speaker_name, selector: Optional[ConversableAgent] = None
    ):
        checking_agent = ConversableAgent("checking_agent", default_auto_reply=max_attempts)

        # Register the speaker validation function with the checking agent
        checking_agent.register_reply(
            trigger=[ConversableAgent, None],
            reply_func=validate_speaker_name,  # Validate each response
            remove_other_reply_funcs=True,
        )
        # Agent for selecting a single agent name from the response
        speaker_selection_agent = self.agent_by_name("CDA")


        # Register any custom model passed in select_speaker_auto_llm_config with the speaker_selection_agent
        self._register_custom_model_clients(speaker_selection_agent)

        return checking_agent, speaker_selection_agent
            
    
class customised_groupchatmanager(GroupChatManager):
    def __init__(
        self,
        groupchat: customised_groupchat,
        name: Optional[str] = "chat_manager",
        # unlimited consecutive auto reply by default
        max_consecutive_auto_reply: Optional[int] = 4,
        human_input_mode: Literal["ALWAYS", "NEVER", "TERMINATE"] = "TERMINATE",
        system_message: Optional[Union[str, List]] = "Group chat manager.",
        silent: bool = False,
        **kwargs,
    ):
        super().__init__(
            groupchat,
            name,
            max_consecutive_auto_reply,
            human_input_mode,
            system_message,
            silent,
            **kwargs,
        )


    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[customised_groupchat] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Run a group chat."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)

        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache
        for i in range(groupchat.max_round):
            self._last_speaker = speaker
            groupchat.append(message, speaker)
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            if self._is_termination_msg(message) or i == groupchat.max_round - 1:
                # The conversation is over or it's the last round
                break
            try:
                # select the next speaker
                speaker, instruction = groupchat.select_speaker(speaker, self)
                if not silent:
                    iostream = IOStream.get_default()
                    iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)
                # let the speaker speak
                self.send(instruction, speaker, request_reply=False, silent=True)
                reply = speaker.generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = speaker.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            except NoEligibleSpeaker:
                # No eligible speaker, terminate the conversation
                logger.warning("No eligible speaker found. Terminating the conversation.")
                break

            if reply is None:
                # no reply is generated, exit the chat
                break

            # check for "clear history" phrase in reply and activate clear history function if found
            if (
                groupchat.enable_clear_history
                and isinstance(reply, dict)
                and reply["content"]
                and "CLEAR HISTORY" in reply["content"].upper()
            ):
                reply["content"] = self.clear_agents_history(reply, groupchat)

            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False, silent=silent)
            message = self.last_message(speaker)
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None


    async def a_run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[customised_groupchat] = None,
    ):
        """Run a group chat asynchronously."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)

        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                await self.a_send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache
        for i in range(groupchat.max_round):
            groupchat.append(message, speaker)

            if self._is_termination_msg(message):
                # The conversation is over
                break

            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    await self.a_send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break
            try:
                # select the next speaker
                speaker = await groupchat.a_select_speaker(speaker, self)
                try:
                    speaker = speaker["speaker"]
                    instruction_message = speaker["instruction"]
                    await self.a_send(instruction_message, speaker, request_reply=False, silent=silent)
                except:
                    pass
                # let the speaker speak
                reply = await speaker.a_generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = await speaker.a_generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            except NoEligibleSpeaker:
                # No eligible speaker, terminate the conversation
                logger.warning("No eligible speaker found. Terminating the conversation.")
                break

            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            await speaker.a_send(reply, self, request_reply=False, silent=silent)
            message = self.last_message(speaker)
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None