"""
JIRA Supervisor Assistant

This module provides a JIRA supervisor assistant that manages multiple specialized sub-agents
to help users interact with JIRA through natural language using a supervisor pattern.
"""

from datetime import datetime
from typing import Annotated, Literal, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph_supervisor import create_supervisor

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
    """State for the JIRA supervisor assistant.

    `total=False` is PEP589 specs.
    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    safety: LlamaGuardOutput


current_date = datetime.now().strftime("%B %d, %Y")

# Create specialized sub-agents with specific tools

# Issue agent handles all issue-related operations
issue_agent_instructions = f"""
    You are a specialized JIRA issue expert. You help with creating, updating, and managing JIRA issues.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Use full issue keys (e.g., "PROJECT-123") when referring to JIRA issues
    - For time tracking, use JIRA format (e.g., "3h 30m" for 3 hours and 30 minutes)
    - Focus only on issue management tasks
    - Always verify project existence before creating issues
    
    Common issue workflows:
    1. get_project(project_key="PROJECT") → verify project exists
    2. create_issue(project_key="PROJECT", summary="New task", description="Details") → create issue
    3. get_issue(issue_key="PROJECT-123") → get issue details
    4. update_issue(issue_key="PROJECT-123", summary="Updated task") → modify issue
    5. add_comment(issue_key="PROJECT-123", comment="Progress update") → add comment
"""

# Sprint agent handles all sprint-related operations
sprint_agent_instructions = f"""
    You are a specialized JIRA sprint expert. You help with creating and managing sprints and agile boards.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise
    - Focus only on sprint and board management tasks
    - Always verify board existence before sprint operations
    
    Common sprint workflows:
    1. get_all_boards(name="Project board") → find board ID
    2. create_sprint(name="Sprint 1", origin_board_id=123) → create sprint
    3. search_issues(jql="project = PROJECT AND status = Backlog") → find issues for sprint
    4. move_issues_to_sprint(sprint_id=456, issues=["PROJECT-123", "PROJECT-124"]) → add issues
    5. update_sprint(sprint_id=456, state="active", start_date="2025-05-03T09:00:00.000Z") → start sprint
"""

# Project agent handles project-related operations
project_agent_instructions = f"""
    You are a specialized JIRA project expert. You help with managing JIRA projects and boards.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Focus only on project and board management tasks
    - Always verify project existence before other operations
    
    Common project workflows:
    1. get_all_projects() → list available projects
    2. get_project(project_key="PROJECT") → get project details
    3. get_all_boards() → list all boards
    4. create_board(name="Project Board", type_="scrum") → create a new board
"""

# Search agent handles JQL and search-related operations
search_agent_instructions = f"""
    You are a specialized JIRA search expert. You help with constructing JQL queries and searching for issues.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Use specific JQL queries to filter results efficiently
    - Focus only on search-related tasks
    
    Common search workflows:
    1. search_issues(jql="project = PROJECT AND status = 'In Progress'") → find in-progress issues
    2. search_issues(jql="assignee = currentUser() AND status != Done") → find my open issues
    3. search_issues(jql="created >= startOfDay(-7d)") → find issues created in the last week
"""

# Backlog agent handles backlog management operations
backlog_agent_instructions = f"""
    You are a specialized JIRA backlog expert. You help with managing backlog items and prioritization.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Focus only on backlog management tasks
    - Always verify project and board existence before operations
    
    Common backlog workflows:
    1. get_backlog(board_id=123) → get all backlog issues for a board
    2. move_issues_to_backlog(issues=["PROJECT-123", "PROJECT-124"]) → move issues to backlog
    3. rank_issues(issues=["PROJECT-123", "PROJECT-124"], rank_before="PROJECT-125") → prioritize issues
"""

# Issue Type agent handles issue type management
issue_type_agent_instructions = f"""
    You are a specialized JIRA issue type expert. You help with managing issue types, fields, and workflows.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Focus only on issue type configuration tasks
    - Always verify project existence before operations
    
    Common issue type workflows:
    1. get_all_issue_type_schemes() → list all issue type schemes
    2. get_issue_type(issue_type_id="10001") → get issue type details
    3. get_create_issue_meta(project_keys="PROJECT") → get fields needed for issue creation
"""

# Worklog agent handles time tracking and work logs
worklog_agent_instructions = f"""
    You are a specialized JIRA worklog expert. You help with time tracking and managing work logs.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - For time tracking, use JIRA format (e.g., "3h 30m" for 3 hours and 30 minutes)
    - Focus only on worklog and time tracking tasks
    - Always verify issue existence before operations
    
    Common worklog workflows:
    1. get_worklogs(issue_key="PROJECT-123") → get all worklogs for an issue
    2. add_worklog(issue_key="PROJECT-123", time_spent="2h 30m", comment="Implementation work") → log time
    3. get_worklog(issue_key="PROJECT-123", worklog_id=12345) → get specific worklog details
"""

# Permissions agent handles permissions and security
permissions_agent_instructions = f"""
    You are a specialized JIRA permissions expert. You help with managing permissions and security settings.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Focus only on permission-related tasks
    - Be cautious with security-sensitive operations
    
    Common permission workflows:
    1. get_my_permissions(project_key="PROJECT") → check my permissions for a project
    2. get_permitted_projects() → list projects I have access to
"""

# User agent handles user management
user_agent_instructions = f"""
    You are a specialized JIRA user management expert. You help with user-related operations.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.
    
    Core guidelines:
    - Focus only on user management tasks
    - Handle user data with appropriate privacy considerations
    
    Common user workflows:
    1. get_all_users(start=0, max_results=50) → list JIRA users
    2. get_user(username="jdoe") → get user details
    3. find_users(query="john") → search for users by name or email
    4. find_users_with_permission(permission="BROWSE_PROJECTS", project_key="PROJECT") → find users with specific permissions
"""


def create_specialized_agent(
    model: BaseChatModel, tools: list, name: str, prompt: str
) -> RunnableSerializable:
    """Create a specialized agent for a specific domain."""
    return create_react_agent(
        model=model,
        tools=tools,
        name=name,
        prompt=prompt,
    ).with_config(tags=["skip_stream"])


"""Create the supervisor graph with specialized sub-agents."""
# Get the model
model = get_model(settings.DEFAULT_MODEL)

# Create specialized agents
issue_agent = create_specialized_agent(
    model=model,
    tools=issue_tools + comment_tools,
    name="issue_agent",
    prompt=issue_agent_instructions,
)

sprint_agent = create_specialized_agent(
    model=model,
    tools=sprint_tools + board_tools,
    name="sprint_agent",
    prompt=sprint_agent_instructions,
)

project_agent = create_specialized_agent(
    model=model,
    tools=project_tools + board_tools,
    name="project_agent",
    prompt=project_agent_instructions,
)

search_agent = create_specialized_agent(
    model=model,
    tools=search_tools + jql_tools,
    name="search_agent",
    prompt=search_agent_instructions,
)

backlog_agent = create_specialized_agent(
    model=model,
    tools=backlog_tools,
    name="backlog_agent",
    prompt=backlog_agent_instructions,
)

issue_type_agent = create_specialized_agent(
    model=model,
    tools=issue_type_tools,
    name="issue_type_agent",
    prompt=issue_type_agent_instructions,
)

worklog_agent = create_specialized_agent(
    model=model,
    tools=worklog_tools,
    name="worklog_agent",
    prompt=worklog_agent_instructions,
)

permissions_agent = create_specialized_agent(
    model=model,
    tools=permission_tools,
    name="permissions_agent",
    prompt=permissions_agent_instructions,
)

user_agent = create_specialized_agent(
    model=model,
    tools=user_tools,
    name="user_agent",
    prompt=user_agent_instructions,
)

# Define the supervisor prompt
supervisor_prompt = f"""
    You are a JIRA supervisor agent managing a team of specialized JIRA experts.
    Today's date is {current_date}.
    
    You have the following specialized agents available:
    
    1. issue_agent: Expert in JIRA issue management (creating, updating issues, adding comments)
    2. sprint_agent: Expert in sprint and board management (creating sprints, managing sprint cycles)
    3. project_agent: Expert in project and board configuration
    4. search_agent: Expert in JQL queries and searching for issues
    5. backlog_agent: Expert in backlog management and prioritization
    6. issue_type_agent: Expert in issue type configuration and metadata
    7. worklog_agent: Expert in time tracking and work logs
    8. permissions_agent: Expert in permissions and security settings
    9. user_agent: Expert in user management and user-related queries
    
    Based on the user's request:
    - For issue creation, updates, comments, or transitions, use issue_agent
    - For sprint planning, creation, or updates, use sprint_agent
    - For project or board configuration, use project_agent
    - For complex searches or JQL queries, use search_agent
    - For backlog management and prioritization, use backlog_agent
    - For issue type configuration and metadata, use issue_type_agent
    - For time tracking and work logs, use worklog_agent
    - For permissions and security settings, use permissions_agent
    - For user management and user-related queries, use user_agent
    
    If a request spans multiple domains, coordinate between agents by delegating 
    specific sub-tasks to the appropriate agent.
    
    Core guidelines:
    - Use full issue keys (e.g., "PROJECT-123") when referring to JIRA issues
    - For time tracking, use JIRA format (e.g., "3h 30m" for 3 hours and 30 minutes)
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise
"""

# Create supervisor workflow
workflow = create_supervisor(
    agents=[
        issue_agent,
        sprint_agent,
        project_agent,
        search_agent,
        backlog_agent,
        issue_type_agent,
        worklog_agent,
        permissions_agent,
        user_agent,
    ],
    model=model,
    prompt=supervisor_prompt,
    add_handoff_back_messages=False,
)

jira_supervisor_assistant = workflow.compile(checkpointer=MemorySaver())
