from typing import Dict, List, Tuple
from genai_vanilla_agents.team import Team
from agents.fsi_banking.user_proxy_agent import user_proxy_agent
from agents.fsi_banking.crm_agent import crm_agent
from agents.fsi_banking.product_agent import product_agent
from agents.fsi_banking.planner_agent import planner_agent
from agents.fsi_banking.cio_agent import cio_agent
from agents.fsi_banking.news_agent import news_agent
from agents.fsi_banking.config import llm

def create_group_chat_banking():
    system_message_manager="""
    You are the overall manager of the group chat. 
    You can see all the messages and intervene if necessary. 
    You can also send system messages to the group chat. 
    
    If you need human or user input, you can ask advisor for more information.
    NEVER call advisor immediately after Executor
    """
    team = Team(
        id="group_chat",
        description="A group chat with multiple agents",
        members=[user_proxy_agent, planner_agent, crm_agent, product_agent, cio_agent, news_agent],
        llm=llm, 
        stop_callback=lambda msgs: msgs[-1].get("content", "").strip().lower() == "terminate",
    )
    
    return team