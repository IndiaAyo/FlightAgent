
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    # Helpful debug note when running interactively
    print(f"Using cert bundle: {os.environ.get('SSL_CERT_FILE')}")
except Exception:
    # If certifi isn't available, continue and let the runtime raise the original SSL error
    pass

import semantic_kernel as sk
from datetime import datetime
from semantic_kernel.agents import AzureAIAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential
import os
from flight_search_plugin import FlightSearchPlugin

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize the kernel
    kernel = sk.Kernel()

    # Configure AI service using Azure OpenAI
    deployment = "gpt-4o"  # or your specific model deployment name
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    chat_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # Add Azure OpenAI chat service
    chat_service = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=chat_endpoint,
        api_key=api_key
    )
    kernel.add_service(chat_service)

    # Create the flight search plugin
    flight_plugin = FlightSearchPlugin()
    
    # Register the plugin with the kernel
    kernel.add_plugin(flight_plugin, plugin_name="FlightSearch")

    # Agent instructions (kept as the original detailed instructions)
    instructions = (
        "You are a helpful flight search assistant. Your goal is to help users find flights by:\n"
        "1. Understanding their travel requirements from natural language\n"
        "2. Extracting departure and arrival cities/airports\n"
        "3. Determining travel dates\n"
        "4. Using the FlightSearch plugin to search for available flights\n"
        "5. Presenting the results in a clear, organized way\n\n"
        "When users provide vague locations, ask for clarification about specific airports.\n"
        f"6. Always make sure the dates are in the future. The current date is {datetime.now().date()}.\n"
        "When dates are unclear, ask for specific dates.\n"
        "Always confirm the search details before executing the search."
    )

    print("\nFlight Search Assistant is ready! You can start asking about flights.")
    print("Example: 'Find me flights from NYC to London next week'")
    print("Type 'exit' to quit\n")

    # Create Azure AI client and agent, then run a single interactive loop that sends terminal input
    async with AzureCliCredential() as creds:
        client = AzureAIAgent.create_client(credential=creds, endpoint=project_endpoint)

        # Create or register the agent on the service
        agent_definition = await client.agents.create_agent(model=deployment, name="FlightAssistant", instructions=instructions)

        # Create a Semantic Kernel wrapper around the Azure AI agent
        agent = AzureAIAgent(client=client, definition=agent_definition, kernel=kernel)

        # Keep a thread to preserve conversation context across turns
        thread: AzureAIAgentThread = None

        try:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() == 'exit':
                    break
                if not user_input:
                    continue

                # Send the user's message to the AzureAIAgent and get a response
                response = await agent.get_response(messages=user_input, thread=thread)
                # Print assistant reply
                print(f"Assistant: {response}")
                # Save thread for continuity
                thread = response.thread

        finally:
            # Cleanup: delete thread and agent on the server
            if thread:
                try:
                    await thread.delete()
                except Exception:
                    pass
            try:
                await client.agents.delete_agent(agent.id)
            except Exception:
                pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())