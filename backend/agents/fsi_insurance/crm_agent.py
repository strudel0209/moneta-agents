# CRM Agent 
from pydantic import BaseModel, Field
import json
import os
import logging
from genai_vanilla_agents.agent import Agent
from agents.fsi_insurance.config import llm
from typing import List, Annotated, Optional
from crm_store import CRMStore
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


crm_agent = Agent(  
    id="CRM",
    system_message="""You are an assistant that interacts with CRM data.
   
    **Your Responsibilities:**
    - **Only respond to user requests that explicitly mention the details of a customer such as national identity card number, passport number, driving license number, policy number, customer name or any forms of identification number.**
    - When the user's request includes the name of a client, retrieve information about the client and their policies, coverages, premiums by using the provided functions.
    - Provide concise and accurate information based on the CRM data.
    - Unless stated otherwise, always return the latest information ONLY
   
    **Important Guidelines:**
    - Do NOT answer queries related to general product information, policies, or terms and conditions unless they pertain to a specific client mentioned by name.
    - Do NOT provide any response if the conditions above are not met.
    - *NEVER* make up an answer if the information was not available
    - **ALWAYS** before giving the Final Answer, try another method. Then reflect on the answers of the two methods you did and ask yourself if it answers correctly the original question.
    If you are not sure, try another method.
    - If the methods tried do not give the same result, reflect and try again until you have two methods that have the same result.
    - If you still cannot arrive to a consistent result, say that you are not sure of the answer.
    - If you are sure of the correct answer, give a straight forward response in a sentence.
    - Always follow the following tone of voice when responding: Sound smart and warm, be positive about what's next, show we are on the customer's side, put the main point first,
    keep it short, break it up, prove your point, write more like you speak, use jargons wisely, be clear about what's in it for customers, help customers make the right step,
    put customers first, explain why.
   
    """,  
    llm=llm,  
    description="""Call this Agent if:
        - You need to retrieve specific client's data identified by a specific customer detail in the user request such as national identity card number, passport number,
        driving license number, policy number, customer name or any forms of identification number
        DO NOT CALL THIS AGENT IF:  
        - You need to fetch generic policies answers
        - When customer name is just given as a context to answer generic questions, for example, my customer XXX want to know what are the terms and conditions of the product
        """,  
)  

key = DefaultAzureCredential()
db = CRMStore(
        url=os.getenv("COSMOSDB_ENDPOINT"),
        key=key,
        database_name=os.getenv("COSMOSDB_DATABASE_NAME"),
        container_name=os.getenv("COSMOSDB_CONTAINER_CLIENT_NAME")
    )

@crm_agent.register_tool(description="Load insured client data from the CRM from the given full name")
def load_from_crm_by_client_fullname(full_name:Annotated[str,"The customer full name to search for"]) -> str:
    """
    Load an insured client data and policies into a pandas DataFrame.

    Parameters:
    full_name (str): full_name of the client to search for

    Returns:
    pd.DataFrame: DataFrame containing the loaded data
    """
    try:
        return db.get_customer_profile_by_full_name(full_name)
           
    except Exception as e:
        print(f"An unexpected error occurred loading client data from the DB: {e}") 

@crm_agent.register_tool(description="Load insured client data from the CRM by client_id")
def load_from_crm_by_client_id(client_id:Annotated[str,"The customer client_id to search for"]) -> str:
    """
    Load insured client data from the CRM by client_id into a pandas DataFrame.

    Parameters:
    client_id (str): the client_id of the client to search for

    Returns:
    pd.DataFrame: DataFrame containing the loaded data
    """
    try:
        return db.get_customer_profile_by_client_id(client_id)
           
    except Exception as e:
        print(f"An unexpected error occurred loading client data from the DB: {e}") 