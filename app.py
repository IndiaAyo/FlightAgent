from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file


try:

    # Get project client
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    project_client = AIProjectClient(            
            credential=AzureCliCredential(),
            endpoint=project_endpoint,
        )
    
    ## List all connections in the project
    connections = project_client.connections
    print("List all connections:")
    for connection in connections.list():
        print(f"{connection.name} ({connection.type})")

# Get a chat client
    chat_client = project_client.get_openai_client(api_version="2024-10-21")
    
    # Get a chat completion based on a user-provided prompt
    user_prompt = input("Enter a question:")
    
    response = chat_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": user_prompt}
        ]
    )
    print(response.choices[0].message.content)


except Exception as ex:
    print(ex)