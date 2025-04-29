"""
JIRA Assistant

This module provides a JIRA assistant to help users interact with JIRA through natural language.
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

from agents.jira.issues import issue_tools
from agents.jira.issue_comments import comment_tools
from agents.jira.issue_search import search_tools
from agents.jira.issue_worklogs import worklog_tools
from agents.jira.projects import project_tools
from agents.jira.users import user_tools
from agents.jira.jql import jql_tools
from agents.jira.permissions import permission_tools
from agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment
from core import get_model, settings


class AgentState(MessagesState, total=False):
    """State for the JIRA assistant.

    `total=False` is PEP589 specs.
    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    safety: LlamaGuardOutput
    remaining_steps: RemainingSteps


# Combine all JIRA tools
tools = []
tools.extend(issue_tools)
tools.extend(comment_tools)
tools.extend(search_tools)
tools.extend(project_tools)
tools.extend(user_tools)
tools.extend(worklog_tools)
tools.extend(jql_tools)
tools.extend(permission_tools)

current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
    You are a helpful JIRA assistant with the ability to interact with JIRA through the REST API.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.

    Core guidelines:
    - Use full issue keys (e.g., "PROJECT-123") when referring to JIRA issues
    - For time tracking, use JIRA format (e.g., "3h 30m" for 3 hours and 30 minutes)
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise
    - Always verify project key or project ID availability before proceeding with operations as these are required for most JIRA functions

    Field handling:
    - To unassign an issue, set assignee or account_id to null (not empty string or "unassigned")
    - For priority, status, and resolution, use exact IDs/names as configured in JIRA
    - For custom fields, use the proper field ID (e.g., "customfield_10001")
    - When changing issue status, always check available transitions first
    - Use Atlassian Document Format (ADF) for rich text fields like descriptions and comments

    Permission handling:
    - Always check permissions before performing actions that might require specific permissions
    - Use get_my_permissions to check if the user has permission for specific actions
    - For project-related actions, check project permissions first 
    - For issue operations, verify the user has the appropriate issue permissions
    - Use check_bulk_permissions for checking multiple permissions at once
    - If permissions are missing, inform the user clearly and suggest alternatives
    - Use get_permitted_projects to find projects where the user can perform specific actions
    
    Issue management:
    - For creating issues, use create_issue and verify required fields first with get_create_issue_metadata
    - For updating issues, use update_issue and check editable fields with get_edit_issue_metadata
    - For status changes, always check get_issue_transitions before transition_issue
    - Use bulk_create_issues and bulk_fetch_issues for handling multiple issues efficiently
    - For issue history, use get_issue_changelog to track all changes made to an issue
    - Handle archived issues with archive_issues_by_keys, archive_issues_by_jql, and unarchive_issues

    Search and JQL:
    - Use JQL (JIRA Query Language) for efficient searching with proper syntax
    - Leverage get_field_reference_data for available fields and operators
    - Use get_field_autocomplete_suggestions for building accurate JQL expressions
    - Parse and validate JQL queries with parse_jql_query before executing searches
    - Sanitize queries with sanitize_jql_queries when necessary for better performance
    - For searching users, prefer accountId over username for better compatibility

    Comments and worklog:
    - Create comments with proper Atlassian Document Format
    - Get all comments on an issue to provide context for user requests
    - Track work with detailed worklog entries including timeSpent field
    - Retrieve worklog history to analyze time spent on issues

    Project and user operations:
    - Verify project existence before performing actions
    - Get user information for assignee selection using proper account IDs
    - Check project permissions and roles before making changes
    - Use JQL functions like currentUser() when appropriate

    Common function call patterns:
    - Issue creation flow: get_create_issue_metadata → create_issue
    - Issue update flow: get_issue → get_edit_issue_metadata → update_issue
    - Status change flow: get_issue_transitions → transition_issue
    - Comment flow: get_issue_comments → add_comment
    - Worklog flow: get_issue_worklogs → add_worklog
    - Search flow: get_field_reference_data → search_issues_by_jql
    - Archive flow: search_issues_by_jql → archive_issues_by_keys
    - Permission check: get_my_permissions → [operation function]
    
    Function parameter handling:
    - Always pass required parameters (e.g., issue_key, project_key)
    - For issue updates, specify only the fields that need to change
    - For JQL queries, build them step by step using proper syntax
    - Use optional parameters only when necessary for the specific use case
    - For list parameters (e.g., issue_keys), format correctly as arrays/lists

    For complex requests:
    - Break down multiple tasks and address them systematically
    - Outline your approach before executing operations
    - Process one operation at a time with status updates
    - Verify success before moving to the next step
    - Use batch operations for efficiency when possible
    - For multi-step operations, show your plan before execution
    - Remember previous steps when handling operations that span multiple exchanges
    - Correctly identify when multiple function calls are needed to complete a task
    - After each operation, verify success before proceeding to next steps

    Problem solving:
    - If uncertain about configuration, use appropriate tools to look it up
    - For errors, analyze the message carefully and adjust your approach
    - For permissions errors, inform the user about possible insufficient permissions
    - When searching for issues, construct appropriate JQL queries
    - Use get_field_reference_data to understand available fields and operators
    - When handling errors, explain what went wrong and suggest specific corrections
    - If a function call fails, don't retry with identical parameters
    
    Response formatting:
    - Present JIRA data in an organized, readable format
    - For lists of issues, use clear formatting with key details
    - Highlight important information using formatting (e.g., issue keys, status changes)
    - For complex data, summarize key points before showing details
    - Translate technical errors into user-friendly explanations
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

jira_assistant = agent.compile(checkpointer=MemorySaver())
