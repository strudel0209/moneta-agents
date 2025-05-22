import logging
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions import KernelPlugin, KernelFunctionFromPrompt

from sk.skills.crm_facade import CRMFacade
from sk.skills.policies_facade import PoliciesFacade
from sk.orchestrators.semantic_orchestrator import SemanticOrchastrator
from foundry_agent_utils import FoundryAgentUtils

class InsuranceOrchestrator(SemanticOrchastrator):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Insurance Orchestrator init")

        crm = CRMFacade(
                key=DefaultAzureCredential(),
                cosmosdb_endpoint=os.getenv("COSMOSDB_ENDPOINT"),
                crm_database_name=os.getenv("COSMOSDB_DATABASE_NAME"),
                crm_container_name=os.getenv("COSMOSDB_CONTAINER_CLIENT_NAME"))

        product = PoliciesFacade(
            credential=DefaultAzureCredential(),
            service_endpoint = os.getenv('AI_SEARCH_ENDPOINT'),
            index_name = os.getenv('AI_SEARCH_INS_INDEX_NAME'),
            semantic_configuration_name = 'default')

        self.kernel = Kernel(
            services=[self.gpt4o_service],
            plugins=[
                KernelPlugin.from_object(plugin_instance=crm, plugin_name="crm"),
                KernelPlugin.from_object(plugin_instance=product, plugin_name="product"),
            ]
        )
        self.foundry_utils = FoundryAgentUtils()

    # --------------------------------------------
    # Selection Strategy
    # --------------------------------------------
    def create_selection_strategy(self, agents, default_agent):
        """Speaker selection strategy for the agent group chat."""
        definitions = "\n".join([f"{agent.name}: {agent.description}" for agent in agents])
        selection_function = KernelFunctionFromPrompt(
                function_name="SpeakerSelector",
                prompt_execution_settings=AzureChatPromptExecutionSettings(
                    temperature=0),
                prompt=fr"""
                    You are the next speaker selector.

                    - You MUST return ONLY agent name from the list of available agents below.
                    - You MUST return the agent name and nothing else.
                    - Check the history, if any, and decide WHAT agent is the best next speaker
                    - The names are case-sensitive and should not be abbreviated or changed.
                    - YOU MUST OBSERVE AGENT USAGE INSTRUCTIONS.

# AVAILABLE AGENTS

{definitions}

# CHAT HISTORY

{{{{$history}}}}
""")

        # Could be lambda. Keeping as function for clarity
        def parse_selection_output(output):
            self.logger.debug(f"Parsing selection: {output}")
            if output.value is not None:
                return output.value[0].content
            return default_agent.name

        return KernelFunctionSelectionStrategy(
                    kernel=self.kernel,
                    function=selection_function,
                    result_parser=parse_selection_output,
                    agent_variable_name="agents",
                    history_variable_name="history")

    # --------------------------------------------
    # Termination Strategy
    # --------------------------------------------
    def create_termination_strategy(self, agents, final_agent, maximum_iterations):
        """
        Create a chat termination strategy that terminates when the final agent is reached.
        params:
            agents: List of agents to trigger termination evaluation
            final_agent: The agent that should trigger termination
            maximum_iterations: Maximum number of iterations before termination
        """
        class CompletionTerminationStrategy(TerminationStrategy):
            async def should_agent_terminate(self, agent, history):
                """Terminate if the last actor is the Responder Agent."""
                logging.getLogger(__name__).debug(history[-1])
                return (agent.name == final_agent.name)

        return CompletionTerminationStrategy(agents=agents,
                                             maximum_iterations=maximum_iterations)

    # --------------------------------------------
    # Create Agent Group Chat
    # --------------------------------------------
    def create_agent_group_chat(self):
        """
        Create an agent group chat using agents loaded from Azure AI Foundry.
        Agents are retrieved or created in Foundry using FoundryAgentUtils.ensure_agent.
        If the agent does not exist in Foundry, it is created from the fallback YAML definition in sk/agents/insurance/.
        The group chat is orchestrated using Semantic Kernel's AgentGroupChat.
        """
        self.logger.debug("Creating insurance chat (Foundry)")

        # Agents are loaded from Foundry, falling back to YAML if not present in Foundry
        query_agent = self.foundry_utils.ensure_agent(
            agent_name="QueryAgent",
            kernel=self.kernel,
            foundry_project_name=os.getenv("AI_PROJECT_CONNECTION_STRING"),
            fallback_yaml_path="sk/agents/insurance/query.yaml"
        )
        responder_agent = self.foundry_utils.ensure_agent(
            agent_name="SummariserAgent",
            kernel=self.kernel,
            foundry_project_name=os.getenv("AI_PROJECT_CONNECTION_STRING"),
            fallback_yaml_path="sk/agents/insurance/responder.yaml"
        )

        agents = [query_agent, responder_agent]

        agent_group_chat = AgentGroupChat(
                agents=agents,
                selection_strategy=self.create_selection_strategy(agents, responder_agent),
                termination_strategy = self.create_termination_strategy(
                                         agents=agents,
                                         final_agent=responder_agent,
                                         maximum_iterations=8))

        return agent_group_chat
