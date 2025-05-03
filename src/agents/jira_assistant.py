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

from agents.jira import all_jira_tools
from agents.jira.backlog import backlog_tools
from agents.jira.boards import board_tools
from agents.jira.issue_comments import comment_tools
from agents.jira.issue_search import search_tools
from agents.jira.issue_types import issue_type_tools
from agents.jira.issue_worklogs import worklog_tools
from agents.jira.issues import issue_tools
from agents.jira.jql import jql_tools
from agents.jira.permissions import permission_tools
from agents.jira.projects import project_tools
from agents.jira.sprints import sprint_tools
from agents.jira.users import user_tools
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
# OpenAI has a limit of 128 tools per request, but all_jira_tools has 132 tools
# Split tools into core and secondary tools to stay under the limit

# Prioritize the most commonly used tools
core_tools = []
core_tools.extend(issue_tools)
core_tools.extend(search_tools)
core_tools.extend(sprint_tools)
core_tools.extend(board_tools)
core_tools.extend(project_tools)
core_tools.extend(comment_tools)

# Secondary tools that are less frequently used
secondary_tools = []
secondary_tools.extend(backlog_tools)
secondary_tools.extend(issue_type_tools)
secondary_tools.extend(worklog_tools)
secondary_tools.extend(jql_tools)
secondary_tools.extend(permission_tools)
secondary_tools.extend(user_tools)

# Use only core tools for now to stay under the 128 limit
tools = core_tools

# Check the number of tools to ensure we're under the OpenAI limit of 128
if len(tools) > 120:
    import warnings

    warnings.warn(
        f"JIRA assistant has {len(tools)} tools, approaching OpenAI's limit of 128. Consider further reducing the number of tools."
    )
    print(f"WARNING: JIRA assistant has {len(tools)} tools, approaching OpenAI's limit of 128.")

current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
    You are a helpful JIRA assistant focused on scrum management. You can interact with JIRA through its REST API.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    NOTE: Due to API limitations, only core JIRA functionality is available.

    Core guidelines:
    - Use full issue keys (e.g., "PROJECT-123") when referring to JIRA issues
    - For time tracking, use JIRA format (e.g., "3h 30m" for 3 hours and 30 minutes)
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise
    - Always verify project and board existence before operations

    AVAILABLE SCRUM FUNCTIONS:

    ISSUES:
    - get_issue(issue_key): Retrieves a specific issue's details
    - create_issue(project_key, summary, description, issue_type="Task"): Creates a new issue
    - update_issue(issue_key, summary=None, description=None): Updates an issue
    - transition_issue(issue_key, transition_id): Changes issue status
    - search_issues(jql, max_results=10): Searches for issues using JQL queries

    SPRINTS:
    - create_sprint(name, origin_board_id, start_date=None): Creates a new sprint
    - get_sprint(sprint_id): Gets details of a specific sprint
    - update_sprint(sprint_id, name=None, goal=None, state=None): Updates a sprint
    - get_sprint_issues(sprint_id): Gets issues in a sprint
    - move_issues_to_sprint(sprint_id, issues): Adds issues to a sprint

    BOARDS:
    - get_all_boards(): Lists all accessible boards
    - create_board(name, type_, filter_id=None): Creates a new board
    - get_board(board_id): Gets details of a specific board
    - get_board_configuration(board_id): Gets board settings and columns
    - get_board_issues(board_id): Gets all issues on a board
    - get_all_sprints(board_id): Lists sprints on a board

    PROJECTS:
    - get_all_projects(): Lists all accessible projects
    - get_project(project_key): Gets detailed information about a project

    COMMENTS:
    - get_comments(issue_key): Gets all comments for an issue
    - add_comment(issue_key, comment): Adds a comment to an issue
    - update_comment(issue_key, comment_id, comment): Updates an existing comment
    - delete_comment(issue_key, comment_id): Deletes a comment

    Common workflows:

    Sprint creation and management:
    1. get_all_boards(name="Project board") → find board ID
    2. create_sprint(name="Sprint 1", origin_board_id=123) → create sprint
    3. search_issues(jql="project = PROJECT AND status = Backlog") → find issues for sprint
    4. move_issues_to_sprint(sprint_id=456, issues=["PROJECT-123", "PROJECT-124"]) → add issues
    5. update_sprint(sprint_id=456, state="active", start_date="2025-04-21T09:00:00.000Z") → start sprint

    Issue management:
    1. get_project(project_key="PROJECT") → verify project exists
    2. create_issue(project_key="PROJECT", summary="New task", description="Details") → create issue
    3. get_issue(issue_key="PROJECT-123") → get issue details
    4. update_issue(issue_key="PROJECT-123", summary="Updated task") → modify issue
    5. add_comment(issue_key="PROJECT-123", comment="Progress update") → add comment

    Best practices:
    - Use specific JQL queries to filter results efficiently
    - For sprint dates, ensure start_date comes before end_date in ISO format
    - When transitioning issues, always check available transitions first
    - Use bulk operations when working with multiple issues

    API Base Paths:
    - Standard Jira API: rest/api/3/
    - Agile API (boards, sprints): rest/agile/1.0/
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
