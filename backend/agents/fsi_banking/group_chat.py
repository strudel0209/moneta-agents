from typing import Dict, List, Tuple
from genai_vanilla_agents.team import Team
from genai_vanilla_agents.planned_team import PlannedTeam
from genai_vanilla_agents.conversation import Conversation, SummarizeMessagesStrategy
from agents.fsi_banking.user_proxy_agent import user_proxy_agent
from agents.fsi_banking.crm_agent import crm_agent
from agents.fsi_banking.product_agent import product_agent
from agents.fsi_banking.planner_agent import planner_agent
from agents.fsi_banking.cio_agent import cio_agent
from agents.fsi_banking.news_agent import news_agent
from agents.fsi_banking.config import llm

import logging
logger = logging.getLogger(__name__)

def create_group_chat_banking(original_inquiry):
    system_message_template = """
    You need to understand if the user inquiry can be responded by 1 agent in particular or if it requires a plan involving multiple agents to fullfill the request in one shot.
    Only respond with 1 word based on your decision and nothing else, also don't include the single quote or any other characters, only 1 word as output.
    'single' or 'multiple' 
    """
    local_messages = []
    local_messages.append({"role": "system", "content": system_message_template})
    local_messages.append({"role": "user", "content": original_inquiry})
    
    response = llm.ask(messages=local_messages)
    strategy = response[0].content
    logger.info(f"agent team strategy decision = {strategy}")

    team = None
    system_message_manager="""
        You are the overall manager of the group chat. 
        You can see all the messages and intervene if necessary. 
        You can also send system messages to the group chat. 
        
        If you need human or user input, you can ask advisor for more information.
        NEVER call advisor immediately after Executor
        """
    
    if 'single' == strategy:

        summarize_system_prompt = """Summarize the conversation so far."""

        team = Team(
            id="group_chat",
            description="A group chat with multiple agents",
            members=[user_proxy_agent, planner_agent, crm_agent, product_agent, cio_agent, news_agent],
            llm=llm, 
            stop_callback=lambda msgs: msgs[-1].get("content", "").strip().lower() == "terminate",
            #system_prompt=system_message_manager,
            #reading_strategy=SummarizeMessagesStrategy(llm, summarize_system_prompt)
        )
    else:
        team = PlannedTeam(
            id="group_chat",
            description="A group chat with multiple agents",
            members=[user_proxy_agent, planner_agent, crm_agent, product_agent, cio_agent, news_agent],
            llm=llm, 
            stop_callback=lambda msgs: len(msgs) > 12,    
        )
    return team