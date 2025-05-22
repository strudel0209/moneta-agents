"""
Utility for managing Azure AI Foundry agents using the azure-ai-projects SDK.
Handles authentication, agent creation/loading, and provides helper functions for orchestration.
"""
import os
import logging
import yaml
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AzureAISearchTool, FunctionTool, ToolSet
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from sk.skills.crm_facade import crm_functions
from sk.skills.news_facade import news_functions

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class FoundryAgentUtils:
    def __init__(self, project_client: AIProjectClient = None):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("AI Foundry FoundryAgentUtils init")
        if project_client:
            self.project_client = project_client
        else:
            project_endpoint = os.environ["AI_PROJECT_CONNECTION_STRING"]
            self.project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=DefaultAzureCredential(),
                api_version="latest",
            )

    def load_yaml(self, yaml_filename: str):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        absolute_path = os.path.join(
            script_dir,
            "..",
            "sk",
            "agents",
            "banking",
            yaml_filename
        )
        absolute_path = os.path.normpath(absolute_path)
        self.logger.info(f"YAML abs path: {absolute_path}")
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"File not found: {absolute_path}")
        with open(absolute_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def create_agent_cio(self, agent_definition: dict):
        self.logger.info("AI Foundry create_agent_cio init")
        conn_list = self.project_client.connections.list()
        conn_id = ""
        for conn in conn_list:
            if conn.connection_type == "AZURE_AI_SEARCH":
                conn_id = conn.id
        ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name="cio-index")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        agent = self.project_client.agents.create_agent(
            model=deployment_name,
            name=agent_definition["name"],
            description=agent_definition["description"],
            instructions=agent_definition["instructions"],
            temperature=agent_definition["temperature"],
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
        self.logger.debug(f"Created agent, ID: {agent.id}")
        return agent

    def create_agent_crm(self, agent_definition: dict):
        self.logger.info("AI Foundry create_agent_crm init")
        functions = FunctionTool(functions=crm_functions)
        toolset = ToolSet()
        toolset.add(functions)
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        agent = self.project_client.agents.create_agent(
            model=deployment_name,
            name=agent_definition["name"],
            description=agent_definition["description"],
            instructions=agent_definition["instructions"],
            temperature=agent_definition["temperature"],
            toolset=toolset,
        )
        self.logger.info(f"Created agent, ID: {agent.id}")
        return agent

    def create_agent_funds(self, agent_definition: dict):
        self.logger.info("AI Foundry create_agent_funds init")
        conn_list = self.project_client.connections.list()
        conn_id = ""
        for conn in conn_list:
            if conn.connection_type == "AZURE_AI_SEARCH":
                conn_id = conn.id
        ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name="funds-index")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        agent = self.project_client.agents.create_agent(
            model=deployment_name,
            name=agent_definition["name"],
            description=agent_definition["description"],
            instructions=agent_definition["instructions"],
            temperature=agent_definition["temperature"],
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
        self.logger.debug(f"Created agent, ID: {agent.id}")
        return agent

    def create_agent_news(self, agent_definition: dict):
        self.logger.info("AI Foundry create_agent_news init")
        functions = FunctionTool(functions=news_functions)
        toolset = ToolSet()
        toolset.add(functions)
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        agent = self.project_client.agents.create_agent(
            model=deployment_name,
            name=agent_definition["name"],
            description=agent_definition["description"],
            instructions=agent_definition["instructions"],
            temperature=agent_definition["temperature"],
            toolset=toolset,
        )
        self.logger.debug(f"Created agent, ID: {agent.id}")
        return agent

    def create_agent_responder(self, agent_definition: dict):
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        agent = self.project_client.agents.create_agent(
            model=deployment_name,
            name=agent_definition["name"],
            description=agent_definition["description"],
            instructions=agent_definition["instructions"],
        )
        self.logger.debug(f"Created agent, ID: {agent.id}")
        return agent

    def create_agent(self, agent_type: str):
        self.logger.info("AI Foundry create_agent")
        agent_definition = self.load_yaml(agent_type + ".yaml")
        try:
            self.logger.info("Listing all agents from Project...")
            agents_list = self.project_client.agents.list_agents()
            self.logger.info("Checking if agent already exists...")
            for agent in agents_list.data:
                if agent.name == agent_definition["name"]:
                    return self.project_client.agents.get_agent(agent.id)
        except HttpResponseError as e:
            self.logger.error(f"create_agent: failed to list available agents: {e.status_code} ({e.reason})")
            self.logger.error(e.message)
        self.logger.info("Creating agents...")
        if agent_type == "cio":
            return self.create_agent_cio(agent_definition)
        elif agent_type == "crm":
            return self.create_agent_crm(agent_definition)
        elif agent_type == "funds":
            return self.create_agent_funds(agent_definition)
        elif agent_type == "news":
            return self.create_agent_news(agent_definition)
        elif agent_type == "responder":
            return self.create_agent_responder(agent_definition)
