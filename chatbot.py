import sys
import time

import asyncio
from agents.run import Runner

from dotenv import load_dotenv

from create_agent import create_agent

"""
AgentKit Chatbot Interface

This file provides a command-line interface for interacting with your AgentKit-powered AI agent.
It supports two modes of operation:

1. Chat Mode:
   - Interactive conversations with the agent
   - Direct user input and agent responses

2. Autonomous Mode:
   - Agent operates independently
   - Performs periodic blockchain interactions
   - Useful for automated tasks or monitoring

Use this as a starting point for building your own agent interface or integrate
the agent into your existing applications.

# Want to contribute?
Join us in shaping AgentKit! Check out the contribution guide:  
- https://github.com/coinbase/agentkit/blob/main/CONTRIBUTING.md
- https://discord.gg/CDP
"""
from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from a .env file into os.environ

# Optional: manually set it again, but usually not needed
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Autonomous Mode
async def run_autonomous_mode(agent, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            # Run agent in autonomous mode
            output = await Runner.run(agent, thought)
            print(output.final_output)
            print("-------------------")

            # Wait before the next action
            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)

# Chat Mode
async def run_chat_mode(agent, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            output = await Runner.run(agent, user_input)
            print(output.final_output)
            print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)



# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


async def main():

    """Start the chatbot agent."""
    agent_executor, config = create_agent()

    mode = choose_mode()
    if mode == "chat":
        
        await run_chat_mode(agent=agent_executor, config=config)
        
    elif mode == "auto":
        
        await run_autonomous_mode(agent=agent_executor, config=config)
        

if __name__ == "__main__":
    print("Starting Agent...")
    
    asyncio.run(main())
    
