"""
Azure DevOps Assistant

This module provides an Azure DevOps assistant to help users interact with Azure DevOps through natural language.
"""

from datetime import datetime
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode

from agents.azure_devops.projects import project_tools
from agents.azure_devops.work_items import work_item_tools
from agents.azure_devops.git import git_tools
from agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment
from core import get_model, settings


class AgentState(MessagesState, total=False):
    """State for the Azure DevOps assistant.

    `total=False` is PEP589 specs.
    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    safety: LlamaGuardOutput
    remaining_steps: RemainingSteps


# Combine all Azure DevOps tools
tools = []
tools.extend(project_tools)
tools.extend(work_item_tools)
tools.extend(git_tools)

current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
    You are a helpful Azure DevOps assistant with the ability to interact with Azure DevOps through its API.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.

    Core guidelines:
    - Use full IDs when referring to work items (e.g., #1234)
    - For work item states, use the exact states configured in the project
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise
    - Always verify project name availability before proceeding with operations as this is required for most Azure DevOps functions

    Work Item handling:
    - Work item types may include: User Story, Bug, Task, Epic, Feature (verify with get_work_item_types)
    - Check work item states with get_work_item_states before updating state
    - Fields starting with "System." are system fields (e.g., System.Title)
    - Fields starting with "Microsoft.VSTS." are standard fields (e.g., Microsoft.VSTS.Common.Priority)
    - Use JSON patch operations when updating work items

    Git operations:
    - Always specify both project name and repository name for Git operations
    - For branch names, provide the branch name with or without the 'refs/heads/' prefix
    - When creating pull requests, make sure source and target branches exist
    - For pull request status, use one of: 'active', 'abandoned', 'completed', 'all'

    For complex requests:
    - Break down multiple tasks and address them systematically
    - Outline your approach before executing operations
    - Process one operation at a time with status updates
    - Verify success before moving to the next step

    Problem solving:
    - If uncertain about configuration, use appropriate tools to look it up
    - For errors, analyze the message carefully and adjust your approach
    - When searching for work items, construct appropriate WIQL queries
    - Use continuation tokens when working with large result sets
    """


def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model  # type: ignore[return-value]


def format_safety_message(safety: LlamaGuardOutput) -> AIMessage:
    content = (
        f"This conversation was flagged for unsafe content: {', '.join(safety.unsafe_categories)}"
    )
    return AIMessage(content=content)


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # Run llama guard check here to avoid returning the message if it's unsafe
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("Agent", state["messages"] + [response])
    if safety_output.safety_assessment == SafetyAssessment.UNSAFE:
        return {"messages": [format_safety_message(safety_output)], "safety": safety_output}

    if state["remaining_steps"] < 2 and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


async def llama_guard_input(state: AgentState, config: RunnableConfig) -> AgentState:
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("User", state["messages"])
    return {"safety": safety_output, "messages": []}


async def block_unsafe_content(state: AgentState, config: RunnableConfig) -> AgentState:
    safety: LlamaGuardOutput = state["safety"]
    return {"messages": [format_safety_message(safety)]}


# Define the graph
agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("guard_input", llama_guard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")


# Check for unsafe input and block further processing if found
def check_safety(state: AgentState) -> Literal["unsafe", "safe"]:
    safety: LlamaGuardOutput = state["safety"]
    match safety.safety_assessment:
        case SafetyAssessment.UNSAFE:
            return "unsafe"
        case _:
            return "safe"


agent.add_conditional_edges(
    "guard_input", check_safety, {"unsafe": "block_unsafe_content", "safe": "model"}
)

# Always END after blocking unsafe content
agent.add_edge("block_unsafe_content", END)

# Always run "model" after "tools"
agent.add_edge("tools", "model")


# After "model", if there are tool calls, run "tools". Otherwise END.
def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})

azure_devops_assistant = agent.compile(checkpointer=MemorySaver())
