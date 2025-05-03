# 🤖 Agent Service Toolkit

A flexible toolkit for building AI agents with specialized capabilities, currently featuring assistants for Agile development workflows. Built with LangGraph, FastAPI, and Streamlit, this toolkit provides a foundation for creating, deploying, and interacting with AI agents through natural language.

It includes [LangGraph](https://langchain-ai.github.io/langgraph/) for constructing agent workflows, a [FastAPI](https://fastapi.tiangolo.com/) service to serve them, a client to interact with the service, and a [Streamlit](https://streamlit.io/) app that provides a chat interface. Data structures and settings are built with [Pydantic](https://github.com/pydantic/pydantic).

The toolkit currently demonstrates its capabilities through specialized agents for JIRA and Azure DevOps platforms, making project management more accessible and efficient through natural language interactions.

> **Credits**: This project is based on [agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit), created by Joshua Cholewka.

## Overview

### Quickstart

Run directly in python

```sh
# At least one LLM API key is required
echo 'OPENAI_API_KEY=your_openai_api_key' >> .env

# uv is recommended but "pip install ." also works
pip install uv
uv sync --frozen
# "uv sync" creates .venv automatically
source .venv/bin/activate
python src/run_service.py

# In another shell
source .venv/bin/activate
streamlit run src/streamlit_app.py
```

Run with docker

```sh
echo 'OPENAI_API_KEY=your_openai_api_key' >> .env
docker compose watch
```

### Key Features

1. **Extensible Agent Architecture**: A flexible framework that allows creating specialized agents for different domains and use cases.
2. **Pre-built Specialized Agents**: Ready-to-use agents for JIRA and Azure DevOps that understand the specific workflows and APIs of these platforms.
3. **Natural Language Interface**: Interact with tools and services using natural language queries and commands.
4. **LangGraph Integration**: Built using LangGraph v0.3 features including human-in-the-loop interactions and checkpointing.
5. **Multiple Model Support**: Compatible with various LLM providers including OpenAI, Anthropic, Google, Groq, AWS Bedrock, Azure OpenAI, and more.
6. **Full API Service**: FastAPI service with both streaming and non-streaming endpoints.
7. **Advanced Streaming**: Support for both token-by-token and message-level streaming.
8. **Streamlit UI**: Ready-to-use chat interface for interacting with agents.
9. **Content Moderation**: Optional content filtering with LlamaGuard (requires Groq API key).
10. **Feedback System**: Star-based feedback mechanism integrated with LangSmith.
11. **Persistent Memory**: Database-backed state management using SQLite or PostgreSQL.
12. **Docker Support**: Production-ready Dockerfiles and compose configuration with development mode.

### Key Files and Directory Structure

The repository is structured as follows:

- `src/agents/`: Contains specialized agent implementations
  - `src/agents/jira/`: JIRA API integration modules (boards, issues, sprints, etc.)
  - `src/agents/azure_devops/`: Azure DevOps API integration modules
  - `src/agents/jira_assistant.py`: The main JIRA assistant implementation
  - `src/agents/jira_supervisor_assistant.py`: JIRA supervisor for specialized sub-agents
  - `src/agents/azure_devops_assistant.py`: The main Azure DevOps assistant
  - `src/agents/tools.py`: Shared tools and utilities for agents
- `src/schema/`: Data model definitions using Pydantic
  - `src/schema/models.py`: Core data models
  - `src/schema/schema.py`: API schema definitions
- `src/core/`: Core modules for the service
  - `src/core/llm.py`: LLM provider integrations
  - `src/core/settings.py`: Configuration settings using Pydantic
- `src/memory/`: Persistent state storage implementations
  - `src/memory/postgres.py`: PostgreSQL-based state storage
  - `src/memory/sqlite.py`: SQLite-based state storage
- `src/service/`: The FastAPI service implementation
  - `src/service/service.py`: Main service with API endpoints
  - `src/service/utils.py`: Utilities for the service
- `src/client/`: Client library for interacting with the service
  - `src/client/client.py`: AgentClient implementation
- `src/run_service.py`: Entry point for running the FastAPI service
- `src/streamlit_app.py`: Streamlit chat interface implementation

## Prerequisites

- Python 3.12 or newer
- Docker (optional, for containerized deployment)
- Docker Compose v2.23.0+ (optional, for development with `docker compose watch`)
- API access to at least one of the supported LLM providers:
  - OpenAI
  - Anthropic
  - Google AI (Gemini)
  - Groq
  - AWS Bedrock
  - Azure OpenAI
  - Deepseek
  - Ollama (for local models)
- For JIRA integration: JIRA API token with appropriate permissions
- For Azure DevOps integration: Azure DevOps Personal Access Token (PAT)

## Setup and Usage

1. Clone the repository:

   ```sh
   git clone https://github.com/langchain-ai/agent-service-toolkit.git
   cd agent-service-toolkit
   ```

2. Set up environment variables:
   Create a `.env` file in the root directory. At least one LLM API key is required. The toolkit supports multiple LLM providers:

   ```sh
   # Required: At least one of these LLM API keys
   OPENAI_API_KEY=your_openai_api_key
   # ANTHROPIC_API_KEY=your_anthropic_api_key
   # GOOGLE_API_KEY=your_google_api_key
   # GROQ_API_KEY=your_groq_api_key
   # DEEPSEEK_API_KEY=your_deepseek_api_key
   # USE_AWS_BEDROCK=true  # Uses AWS credentials from your environment
   
   # For JIRA integration
   # JIRA_URL=https://your-domain.atlassian.net
   # JIRA_EMAIL=your_email@example.com
   # JIRA_API_TOKEN=your_jira_api_token
   
   # For Azure DevOps integration
   # AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-organization
   # AZURE_DEVOPS_PAT=your_personal_access_token
   
   # Optional: For authentication to the API
   # AUTH_SECRET=your_secret_key
   
   # Optional: For LangSmith tracing
   # LANGCHAIN_TRACING_V2=true
   # LANGCHAIN_API_KEY=your_langsmith_api_key
   # LANGCHAIN_PROJECT=your_project_name
   ```

3. Choose a deployment option:
   - Use Docker (recommended for development)
   - Run locally with Python

### Available Assistants

The Agent Service Toolkit currently includes the following specialized agents:

1. **JIRA Assistant**: A comprehensive assistant for JIRA management that can:
   - Create, update, and manage issues
   - Plan and manage sprints
   - Configure and query boards
   - Create and manage projects
   - Execute JQL queries
   - Handle comments, worklogs, and more

2. **Azure DevOps Assistant**: A specialized assistant for Azure DevOps that can:
   - Manage work items, including creation, updates, and queries
   - Configure and interact with boards and backlogs
   - Handle iterations, sprints, and team management
   - Create and manage projects and repositories
   - Work with delivery plans and process templates
   - Execute Git operations

Each assistant can be accessed via their dedicated endpoints (e.g., `/jira-assistant/invoke`, `/jira-assistant/stream`, `/azure-devops-assistant/invoke`, or `/azure-devops-assistant/stream`).

### API Endpoints

The service provides the following endpoints:

- **GET** `/info`: Returns information about available agents and models
- **POST** `/{agent_id}/invoke`: Makes a non-streaming call to a specific agent
- **POST** `/invoke`: Makes a non-streaming call to the default agent
- **POST** `/{agent_id}/stream`: Makes a streaming call to a specific agent (returns SSE)
- **POST** `/stream`: Makes a streaming call to the default agent (returns SSE)
- **POST** `/feedback`: Records user feedback with an optional rating
- **POST** `/history`: Retrieves chat history for a specific thread ID
- **GET** `/health`: Basic health check endpoint

You can view the complete API documentation at `http://0.0.0.0:8080/redoc` when the service is running.

### Building or customizing your own agent

To customize the assistant for your own use case:

1. Add your new agent to the `src/agents` directory. You can copy one of the existing assistants and modify it to change the agent's behavior and tools.
2. Import and add your new agent to the `agents` dictionary in `src/agents/agents.py`. Your agent can be called by `/<your_agent_name>/invoke` or `/<your_agent_name>/stream`.
3. Adjust the Streamlit interface in `src/streamlit_app.py` to match your agent's capabilities.

### Database Configuration

The Agent Service Toolkit supports two database options for agent state persistence:

1. **SQLite** (default): No additional configuration needed. The service will create a `checkpoints.db` file in the root directory.

2. **PostgreSQL**: For production deployments, you can use PostgreSQL by setting these environment variables:

   ```sh
   DATABASE_TYPE=postgres
   POSTGRES_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Docker Setup

This project includes a Docker setup for easy development and deployment. The `compose.yaml` file defines two services: `agent_service` and `streamlit_app`. The `Dockerfile` for each is in their respective directories.

For local development, we recommend using [docker compose watch](https://docs.docker.com/compose/file-watch/). This feature allows for a smoother development experience by automatically updating your containers when changes are detected in your source code.

1. Make sure you have Docker and Docker Compose (>=[2.23.0](https://docs.docker.com/compose/release-notes/#2230)) installed on your system.

2. Build and launch the services in watch mode:

   ```sh
   docker compose watch
   ```

3. The services will now automatically update when you make changes to your code:
   - Changes in the relevant python files and directories will trigger updates for the relevant services.
   - NOTE: If you make changes to the `pyproject.toml` or `uv.lock` files, you will need to rebuild the services by running `docker compose up --build`.

4. Access the Streamlit app by navigating to `http://localhost:8501` in your web browser.

5. The agent service API will be available at `http://0.0.0.0:8080`. You can also use the OpenAPI docs at `http://0.0.0.0:8080/redoc`.

6. Use `docker compose down` to stop the services.

### Building other apps with the AgentClient

The repo includes a generic `src/client/client.AgentClient` that can be used to interact with the agent service. This client is designed to be flexible and can be used to build other apps on top of the agent. It supports both synchronous and asynchronous invocations, and streaming and non-streaming requests.

See the `src/run_client.py` file for full examples of how to use the `AgentClient`. A quick example:

```python
from client import AgentClient
client = AgentClient()

# Specify the JIRA assistant
response = client.invoke("Create a new task for implementing user authentication", agent_id="jira-assistant")
response.pretty_print()
```

### Development with LangGraph Studio

The agent supports [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio), a new IDE for developing agents in LangGraph.

You can simply install LangGraph Studio, add your `.env` file to the root directory as described above, and then launch LangGraph studio pointed at the root directory. Customize `langgraph.json` as needed.

### Local development without Docker

You can also run the agent service and the Streamlit app locally without Docker, just using a Python virtual environment.

1. Create a virtual environment and install dependencies:

   ```sh
   pip install uv
   uv sync --frozen
   source .venv/bin/activate
   ```

2. Run the FastAPI server:

   ```sh
   python src/run_service.py
   ```

3. In a separate terminal, run the Streamlit app:

   ```sh
   streamlit run src/streamlit_app.py
   ```

4. Open your browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

## Contributing

Contributions are welcome! You can contribute by:

1. Adding new specialized agents
2. Enhancing existing agents with more capabilities
3. Improving the core service functionality
4. Adding new LLM provider integrations
5. Contributing to documentation or examples

## License

This project is licensed under the terms of the license provided in the repository.

---

Built with ❤️ using [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
