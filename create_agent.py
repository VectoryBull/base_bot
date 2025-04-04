
from coinbase_agentkit_openai_agents_sdk import get_openai_agents_sdk_tools
from agents.agent import Agent
from prepare_agentkit import prepare_agentkit

"""
Agent Framework Integration

This file bridges your AgentKit configuration with your chosen AI framework 
(Langchain or OpenAI Assistants). It handles:

1. LLM Configuration:
   - Select and configure your Language Model

2. Tool Integration:
   - Convert AgentKit tools to framework-compatible format
   - Configure tool availability and permissions

3. Agent Creation:
   - Initialize the agent with tools and instructions
   - Set up memory and conversation management

The create_agent() function returns a configured agent ready for use in your application.
"""

# Shared agent instructions
AGENT_INSTRUCTIONS = (
    "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
    "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
    "them from the faucet if you are on network ID 'base-sepolia' or 'solana-devnet'. If not, you can provide your wallet "
    "details and request funds from the user. Before executing your first action, get the wallet details "
    "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
    "again later. If someone asks you to do something you can't do with your currently available tools, "
    "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
    "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
    "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
)

def create_agent():
    """Initialize the agent with tools from AgentKit."""
    # Get AgentKit instance
    agentkit = prepare_agentkit()

    
    # Get OpenAI Agents SDK tools
    tools = get_openai_agents_sdk_tools(agentkit)

    # Create Agent using the OpenAI Agents SDK
    agent = Agent(
        name="CDP Agent",
        instructions=AGENT_INSTRUCTIONS,
        tools=tools
    )

    return agent, {}  # Return empty config to match Langchain interface
     