# 🤖 Agile AI Chat Assistant

A specialized AI assistant for Agile development workflows, built with LangGraph, FastAPI, and Streamlit. This tool integrates directly with JIRA and Azure DevOps to help manage your Agile development process.

It includes [LangGraph](https://langchain-ai.github.io/langgraph/) agents for each platform, a [FastAPI](https://fastapi.tiangolo.com/) service to serve them, a client to interact with the service, and a [Streamlit](https://streamlit.io/) app that provides a chat interface. Data structures and settings are built with [Pydantic](https://github.com/pydantic/pydantic).

This project allows you to interact with your Agile tools through natural language, making project management more accessible and efficient.

> **Credits**: This project is based on or extends [agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit), created by Joshua Cholewka. We acknowledge and appreciate the foundation provided by this toolkit for building specialized AI assistants.

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

1. **Specialized Agile Assistants**: Dedicated agents for JIRA and Azure DevOps that understand the specific workflows and concepts of these platforms.
2. **Natural Language Interface**: Interact with your Agile tools using natural language queries and commands.
3. **LangGraph Agent Framework**: Built using the latest LangGraph v0.3 features including human-in-the-loop interactions.
4. **FastAPI Service**: Serves the agents with both streaming and non-streaming endpoints.
5. **Advanced Streaming**: Supports both token-based and message-based streaming.
6. **Streamlit Interface**: Provides a user-friendly chat interface for interacting with the agents.
7. **Multiple Agent Support**: Easily switch between JIRA and Azure DevOps assistants. Available agents and models are described in `/info`.
8. **Asynchronous Design**: Utilizes async/await for efficient handling of concurrent requests.
9. **Content Moderation**: Implements LlamaGuard for content moderation (requires Groq API key).
10. **Feedback Mechanism**: Includes a star-based feedback system integrated with LangSmith.
11. **Docker Support**: Includes Dockerfiles and a docker compose file for easy development and deployment.

### Key Files

The repository is structured as follows:

- `src/agents/`: Defines specialized agents for JIRA and Azure DevOps
- `src/schema/`: Defines the protocol schema
- `src/core/`: Core modules including LLM definition and settings
- `src/service/service.py`: FastAPI service to serve the agents
- `src/client/client.py`: Client to interact with the agent service
- `src/streamlit_app.py`: Streamlit app providing a chat interface

## Setup and Usage

1. Clone the repository:

   ```sh
   git clone https://github.com/YourUsername/agile-ai-chat-assistant.git
   cd agile-ai-chat-assistant
   ```

2. Set up environment variables:
   Create a `.env` file in the root directory. At least one LLM API key or configuration is required. See the [`.env.example` file](./.env.example) for a full list of available environment variables, including a variety of model provider API keys, header-based authentication, LangSmith tracing, testing and development modes.

3. You can now run the agent service and the Streamlit app locally, either with Docker or just using Python. The Docker setup is recommended for simpler environment setup and immediate reloading of the services when you make changes to your code.

### Available Assistants

The Agile AI Chat Assistant currently includes the following specialized agents:

1. **JIRA Assistant**: Helps you manage your JIRA board, create and update issues, track sprints, and more.
2. **Azure DevOps Assistant**: Assists with managing Azure DevOps resources, work items, pipelines, and repositories.

Each assistant can be accessed via their dedicated endpoint (e.g., `/jira-assistant/invoke` or `/azure-devops-assistant/stream`).

### Building or customizing your own agent

To customize the assistant for your own use case:

1. Add your new agent to the `src/agents` directory. You can copy one of the existing assistants and modify it to change the agent's behavior and tools.
2. Import and add your new agent to the `agents` dictionary in `src/agents/agents.py`. Your agent can be called by `/<your_agent_name>/invoke` or `/<your_agent_name>/stream`.
3. Adjust the Streamlit interface in `src/streamlit_app.py` to match your agent's capabilities.

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
