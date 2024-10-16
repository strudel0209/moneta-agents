# CRM Agent 
from pydantic import BaseModel, Field
import json
import os
import logging
from genai_vanilla_agents.agent import Agent
from agents.fsi_banking.config import llm
from typing import List, Annotated, Optional
import requests
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


cio_agent = Agent(  
    id="CIO",
    system_message="""You are an assistant that retrieve investement research and house view from Moneta Bank.
        
        **Your Responsibilities:**
        - 
    
    """,  
    llm=llm,  
    description="""Call this Agent if:
        - You need to retrieve specific retrieve investement research and house view from Moneta Ban
        DO NOT CALL THIS AGENT IF:  
        - You need to fetch generic investments answers about assets or retrieve client's specific data or news from the web""",  
)  



def search(query: str):
    service_endpoint = os.getenv('AI_SEARCH_ENDPOINT')
    index_name = os.getenv('AI_SEARCH_CIO_INDEX_NAME')
    key = os.environ["AI_SEARCH_KEY"]

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    payload = json.dumps(
        {
            "search": query,
            "vectorQueries": [
                {
                "kind": "text",
                "text": query,
                "fields": "text_vector"
                }
            ],
            "queryType": "semantic",
            "semanticConfiguration": os.getenv('AI_SEARCH_CIO_SEMANTIC_CONFIGURATION'),
            "captions": "extractive",
            "answers": "extractive|count-3",
            "queryLanguage": "en-US"
        }
    )

    response = list(search_client.search(payload))

    output = []
    for result in response:
        result.pop("parent_id")
        result.pop("chunk_id")
        result.pop("text_vector")
        output.append(result)

    return output
    
    
@cio_agent.register_tool(description="Search investement overview, in house investment view from Moneta Bank.")
def search_product(query:Annotated[str,"The query to search for"]) -> str:
    """
    Search general insurance product information regarding policies, coverages and terms and conditions by permorming a POST request to an Azure AI Search using the specified search body.

    Parameters:
    query

    Returns:
    dict: The search results in JSON format.
    """
    return search(query)