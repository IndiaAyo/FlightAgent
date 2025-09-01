# FlightAgent

Small prototype: a Semantic Kernel-based CLI agent that uses a SerpAPI plugin to search for flights.

Repository layout
- `app.py` — main CLI entrypoint that builds a Semantic Kernel agent and registers the flight plugin.
- `flight_search_plugin.py` — a Kernel plugin that calls SerpAPI's Google Flights engine and returns JSON results.
- `.env` — (not checked in) environment variables. See `.env.example`.
- `requirements.txt` — Python dependencies.

This README explains how to set up a Python virtual environment, configure credentials, run the agent, and troubleshoot common issues (SSL on macOS, credential errors, Foundry vs Azure OpenAI endpoints).

## Prerequisites

- Python 3.10 or newer (3.13 has been used in development).
- git and a terminal (zsh assumed in examples).
- Optional: Azure CLI if you want to authenticate via `az login` instead of an API key.

## Setup (recommended)

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
# or the minimal set:
# pip install semantic-kernel serpapi certifi python-dotenv
```

3. Create a `.env` file in the project root. You can copy from a local template (not included):

```env
# Azure OpenAI (preferred for Azure users)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=

# OR OpenAI directly
OPENAI_API_KEY=
OPENAI_CHAT_MODEL_ID=

# SerpAPI key (required by the flight plugin)
SERP_API_KEY=

# If you earlier used a Foundry project endpoint, keep it for reference only — it is not
# compatible with Azure OpenAI chat client used in this example.
PROJECT_ENDPOINT=
```

Set the values appropriate for your environment. Do NOT commit your `.env` to source control.

## Run the agent

With the venv active and `.env` configured:

```bash
python app.py
```

You should see a prompt like:

```
Flight Search Assistant is ready! You can start asking about flights.
Example: 'Find me flights from NYC to London next week'
Type 'exit' to quit

You: 
```

Try: `Find flights from ATL to IAH next week`.

Type `exit` to quit.

## Troubleshooting

1) SSL certificate verification errors on macOS (common in venvs)

- Symptom: error mentioning `CERTIFICATE_VERIFY_FAILED` or `SSLCertVerificationError`.
- Fix (temporary):

```bash
pip3 install --upgrade certifi
export SSL_CERT_FILE="$(python -m certifi)"
python app.py
```

- Fix (persistent): add the export above to `~/.zshrc` or your venv activation script so the CA bundle is always available.

2) Authentication / 401 errors

- If you get 401 Unauthorized errors from Azure OpenAI, confirm:
	- `AZURE_OPENAI_ENDPOINT` is your resource endpoint (example: `https://<your-resource>.openai.azure.com`)
	- `AZURE_OPENAI_API_KEY` is correct.
	- If you use Azure CLI auth, run `az login` and ensure your account has rights to the resource.

3) Foundry (PROJECT_ENDPOINT) vs Azure OpenAI endpoint

- If you see errors after configuring `PROJECT_ENDPOINT`, it likely points to an Azure Foundry project endpoint (contains `/api/projects/`). The Azure OpenAI chat client expects a different endpoint (the OpenAI resource host). Use the OpenAI resource endpoint or implement a Foundry-specific client flow.

4) SDK version mismatches

- If you encounter ImportError or type errors mentioning `RequiredMcpToolCall` or similar, the installed `semantic-kernel` and `azure-ai-*` packages may be incompatible. Options:
	- Use the `ChatCompletionAgent` path (current code) to avoid directly instantiating SDK model classes.
	- Pin package versions to a known-compatible set (I can prepare a pinned `requirements.txt` if needed).

## Notes on how this repo is wired

- `app.py` builds a Semantic Kernel `ChatCompletionAgent` and registers `FlightSearchPlugin`.
- `FlightSearchPlugin` uses SerpAPI's `GoogleSearch` to return raw JSON. The agent may summarize those results.

