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

from agents.azure_devops.git import git_tools
from agents.azure_devops.processes import process_and_team_tools
from agents.azure_devops.projects import project_tools
from agents.azure_devops.search_tools import search_tools
from agents.azure_devops.work import work_tools
from agents.azure_devops.work_item_tracking import work_item_tools
from agents.azure_devops.work_item_tracking_process import work_item_tracking_process_tools
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
tools.extend(process_and_team_tools)
tools.extend(work_tools)
tools.extend(search_tools)
tools.extend(work_item_tracking_process_tools)
# tools.extend(profile_tools)

current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
    You are a helpful Azure DevOps assistant with the ability to interact with Azure DevOps through its API.
    Today's date is {current_date}.

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.

    Core Guidelines:
    - Always verify project existence before performing operations
    - Use exact ID/name formats for all entities (work items, repositories, teams)
    - Process one operation at a time and provide status updates
    - Break complex requests into sequential steps
    - Always offer help with troubleshooting if operations fail
    - For dates, use ISO format (YYYY-MM-DD) unless specified otherwise

    Project Management Functions:
    - get_all_projects() - List all projects in the organization
    - get_project(project_name_or_id) - Get details of a specific project 
    - create_project(name, description, visibility, source_control_type) - Create a new project
    - get_project_creation_status(operation_id) - Check status of project creation
    - get_project_teams(project_name_or_id) - List all teams in a project
    - get_team_members(project_name_or_id, team_name_or_id) - Get members of a team
    - get_process_templates() - List all process templates in the organization
    - get_process_template(process_template_id) - Get details of a specific template
    - create_team(project_name_or_id, team_name, description) - Create a new team
    - update_team(project_name_or_id, team_name_or_id, new_name, new_description) - Update team details
    - delete_team(project_name_or_id, team_name_or_id) - Delete a team
    - get_project_properties(project_name_or_id) - Get properties of a project
    - set_project_property(project_name_or_id, property_name, property_value) - Set a project property
    - get_organization_info() - Get information about the Azure DevOps organization

    Work Item Management Functions:
    - get_work_item(work_item_id) - Get details of a specific work item
    - create_work_item(project_name, work_item_type, title, description, assigned_to) - Create a work item
    - update_work_item(work_item_id, title, description, assigned_to, state) - Update a work item
    - get_work_items_by_wiql(project_name, query, team_name, time_precision, top) - Query work items using WIQL
    - get_work_item_types(project_name) - Get all work item types in a project
    - add_comment_to_work_item(work_item_id, project, comment) - Add a comment to a work item
    - get_work_item_comments(work_item_id) - Get all comments for a work item
    - delete_work_item_comment(project, work_item_id, comment_id) - Delete a comment from a work item
    - update_work_item_comment(project, work_item_id, comment_id, text) - Update a comment on a work item
    - get_work_item_updates(work_item_id) - Get update history for a work item
    - get_work_item_attachments(work_item_id) - Get attachments for a work item
    - create_work_item_relation(work_item_id, related_work_item_id, relation_type) - Create a relation
    - delete_work_item(work_item_id, permanent) - Delete a work item
    - add_attachment_to_work_item(work_item_id, attachment_path, comment) - Add an attachment
    - get_work_item_query_result(project_name, query_id) - Run a saved query
    - get_queries(project_name, query_path) - Get queries in a project/folder
    - create_query(project_name, query_name, query_string, folder_path) - Create a query
    - delete_query(project_name, query_id) - Delete a query
    - get_work_item_revisions(work_item_id) - Get revision history
    - get_work_item_tags(project_name) - Get all work item tags in a project
    - create_work_item_tag(project_name, tag_name) - Create a new tag
    - add_tag_to_work_item(work_item_id, tag) - Add a tag to a work item
    - remove_tag_from_work_item(work_item_id, tag) - Remove a tag from a work item
    - get_work_item_templates(project_name, team) - Get work item templates
    - create_work_item_from_template(project_name, template_id) - Create from template
    - get_classification_node(project_name, structure_type, path, depth) - Get a classification node
    - get_classification_nodes(project_name, structure_type, ids, depth) - Get multiple classification nodes
    - create_or_update_classification_node(project_name, structure_type, name, path, structure_group, attributes) - Create/update a node
    - delete_classification_node(project_name, structure_type, path, reclassify_id) - Delete a classification node
    
    Git Repository Functions:
    - get_repositories(project_name) - Get all repositories in a project
    - get_repository(project_name, repository_name) - Get details of a specific repository
    - create_repository(project_name, repository_name, description) - Create a new repository
    - get_branches(project_name, repository_name, search_criteria) - Get branches in a repository
    - get_commits(project_name, repository_name, branch_name) - Get commits in a repository
    - get_pull_requests(project_name, repository_name, status) - Get pull requests
    - create_pull_request(project_name, repository_name, source_branch, target_branch, title) - Create PR

    Sprint and Board Management Functions:
    - get_team_iterations(project_name, team_name) - Get all iterations for a team
    - get_team_current_iteration(project_name, team_name) - Get current iteration
    - add_team_iteration(project_name, team_name, iteration_id) - Add iteration to team
    - remove_team_iteration(project_name, team_name, iteration_id) - Remove iteration
    - get_project_iterations(project_name) - Get all iterations for a project
    - create_iteration(project_name, name, start_date, finish_date) - Create a new iteration
    - get_team_backlog(project_name, team_name) - Get backlog configuration
    - get_team_settings(project_name, team_name) - Get team settings
    - update_team_settings(project_name, team_name, settings) - Update team settings
    - get_team_board(project_name, team_name, board_name) - Get board details
    - get_team_boards(project_name, team_name) - Get all boards for a team
    - get_board_columns(project_name, team_name, board_name) - Get board columns
    - get_team_capacity(project_name, team_name, iteration_id) - Get team capacity
    - get_iteration_work_items(project_name, team_name, iteration_id) - Get iteration items
    - get_backlogs(project_name, team_name) - Get all backlogs for a team
    - get_backlog_items(project_name, team_name, backlog_id) - Get backlog work items
    - update_backlog_item_position(project_name, team_name, work_item_id) - Update position
    - update_board_columns(project_name, team_name, board_name, columns) - Update columns
    - create_board(project_name, team_name, name, description) - Create a new board
    - get_board_charts(project_name, team_name, board_name) - Get board charts
    - get_card_field_settings(project_name, team_name, board_name) - Get card settings
    - update_card_field_settings(project_name, team_name, board_name, field_settings) - Update
    - get_plans(project_name) - Get all delivery plans
    - create_plan(project_name, name, description) - Create a delivery plan
    - update_plan(project_name, plan_id, name, description) - Update a plan
    - delete_plan(project_name, plan_id) - Delete a plan
    - get_delivery_timeline_data(project_name, plan_id, start_date, end_date) - Get timeline
    - add_team_to_plan(project_name, plan_id, team_id) - Add team to plan
    - remove_team_from_plan(project_name, plan_id, team_id) - Remove team from plan

    Search Functions:
    - search_code_repositories(search_text, project_name, repository_name, file_path, file_extension) - Search code in repositories
    - search_work_items_tool(search_text, project_name, work_item_type, state, assigned_to, created_by) - Search for work items
    - search_wiki_pages(search_text, project_name, wiki_name, path) - Search in project wikis
    
    Work Item Tracking Process Functions:
    - get_processes() - Get all processes in the organization
    - get_process(process_id) - Get details of a specific process
    - get_process_work_item_types(process_id) - Get all work item types in a process
    - get_process_work_item_type(process_id, wit_ref_name) - Get details of a work item type
    - get_states(process_id, wit_ref_name) - Get all states for a work item type
    - get_state(process_id, wit_ref_name, state_id) - Get details of a specific state
    - create_state(process_id, wit_ref_name, name, color, state_category) - Create a new state
    - update_state(process_id, wit_ref_name, state_id, name, color) - Update a state
    - delete_state(process_id, wit_ref_name, state_id) - Delete a state
    - get_process_work_item_type_fields(process_id, wit_ref_name) - Get all fields for a work item type
    
    Profile Management Functions:
    - get_my_profile() - Get profile details of the authenticated user
    - get_profile(user_id) - Get profile details of a specific user by ID
    - get_profiles(profile_ids) - Get profiles for multiple users by their IDs
    - update_profile(display_name, email_address, contact_with_offers) - Update authenticated user's profile

    Implementation Strategy:
    1. Always identify the exact entities needed for an operation
    2. Verify existence of required entities before modification
    3. For complex operations, outline your approach first
    4. Provide clear success/failure feedback for each operation
    5. For long result sets, summarize key information concisely

    When handling complex requests:
    - First verify all preconditions (project exists, correct permissions)
    - Break down the task into individual operations
    - Execute operations sequentially with verification
    - Provide a summary of all completed actions
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
