"""
Azure DevOps Projects API Functions

This module provides tools for interacting with Azure DevOps projects through the API.
"""

from typing import Any, Dict, List, Optional, Union
import json

from langchain_core.tools import BaseTool, tool
from azure.devops.v7_1.core.models import TeamProject, TeamProjectReference

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_all_projects() -> str:
    """
    Get all projects in the Azure DevOps organization.

    Returns:
        str: JSON string containing all projects
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        # Get projects with continuation token support
        get_projects_response = core_client.get_projects()
        projects = []

        while get_projects_response is not None:
            projects.extend(get_projects_response.value)

            if get_projects_response.continuation_token:
                get_projects_response = core_client.get_projects(
                    continuation_token=get_projects_response.continuation_token
                )
            else:
                get_projects_response = None

        # Format projects for display
        formatted_projects = []
        for project in projects:
            formatted_projects.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "url": project.url,
                    "state": project.state,
                    "visibility": project.visibility,
                    "last_update_time": project.last_update_time.isoformat()
                    if project.last_update_time
                    else None,
                }
            )

        return json.dumps(formatted_projects, indent=2)
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"


@tool
def get_project(project_name_or_id: str) -> str:
    """
    Get details for a specific project by name or ID.

    Args:
        project_name_or_id (str): The name or ID of the project

    Returns:
        str: JSON string containing project details
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        project = core_client.get_project(project_name_or_id)

        # Format project for display
        formatted_project = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "url": project.url,
            "state": project.state,
            "visibility": project.visibility,
            "last_update_time": project.last_update_time.isoformat()
            if project.last_update_time
            else None,
            "default_team": {
                "id": project.default_team.id if project.default_team else None,
                "name": project.default_team.name if project.default_team else None,
            }
            if project.default_team
            else None,
        }

        return json.dumps(formatted_project, indent=2)
    except Exception as e:
        return f"Error retrieving project details: {str(e)}"


@tool
def create_project(
    name: str,
    description: str = "",
    visibility: str = "private",
    source_control_type: str = "Git",
    process_template_id: Optional[str] = None,
) -> str:
    """
    Create a new project in Azure DevOps.

    Args:
        name (str): The name of the project
        description (str, optional): The description of the project
        visibility (str, optional): The visibility of the project. One of 'private' or 'public'
        source_control_type (str, optional): Source control type. One of 'Git' or 'Tfvc'
        process_template_id (str, optional): Process template ID

    Returns:
        str: JSON string containing the created project details
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        # Validate visibility
        if visibility.lower() not in ["private", "public"]:
            return f"Invalid visibility: {visibility}. Must be one of 'private' or 'public'."

        # Validate source_control_type
        if source_control_type.lower() not in ["git", "tfvc"]:
            return f"Invalid source_control_type: {source_control_type}. Must be one of 'Git' or 'Tfvc'."

        # Create project object
        capabilities = {
            "versioncontrol": {"sourceControlType": source_control_type},
            "processTemplate": {},
        }

        # Add process template if provided
        if process_template_id:
            capabilities["processTemplate"]["templateTypeId"] = process_template_id

        # Create project
        operation_reference = core_client.queue_create_project(
            project_to_create=TeamProject(
                name=name, description=description, visibility=visibility, capabilities=capabilities
            )
        )

        # Return immediately with operation ID since project creation is async
        return f"Project creation started. Operation ID: {operation_reference.id}"
    except Exception as e:
        return f"Error creating project: {str(e)}"


@tool
def get_project_creation_status(operation_id: str) -> str:
    """
    Check status of project creation operation.

    Args:
        operation_id (str): The operation ID returned from create_project

    Returns:
        str: JSON string containing the operation status
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        operation = core_client.get_operation(operation_id)

        status = {
            "id": operation.id,
            "status": operation.status,
            "detail_message": operation.detailed_message,
            "result_message": operation.result_message,
            "complete": operation.status in ["succeeded", "cancelled", "failed"],
        }

        return json.dumps(status, indent=2)
    except Exception as e:
        return f"Error checking project creation status: {str(e)}"


@tool
def get_project_teams(project_name_or_id: str) -> str:
    """
    Get all teams in a project.

    Args:
        project_name_or_id (str): The name or ID of the project

    Returns:
        str: JSON string containing all teams
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        teams = core_client.get_teams(project_name_or_id)

        # Format teams for display
        formatted_teams = []
        for team in teams:
            formatted_teams.append(
                {"id": team.id, "name": team.name, "description": team.description, "url": team.url}
            )

        return json.dumps(formatted_teams, indent=2)
    except Exception as e:
        return f"Error retrieving project teams: {str(e)}"


@tool
def get_team_members(project_name_or_id: str, team_name_or_id: str) -> str:
    """
    Get members of a team.

    Args:
        project_name_or_id (str): The name or ID of the project
        team_name_or_id (str): The name or ID of the team

    Returns:
        str: JSON string containing team members
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client("core")

        team_members = core_client.get_team_members_with_extended_properties(
            project_name_or_id, team_name_or_id
        )

        # Format team members for display
        formatted_members = []
        for member in team_members:
            formatted_members.append(
                {
                    "id": member.identity.id,
                    "display_name": member.identity.display_name,
                    "unique_name": member.identity.unique_name,
                    "is_team_admin": member.is_team_admin,
                }
            )

        return json.dumps(formatted_members, indent=2)
    except Exception as e:
        return f"Error retrieving team members: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
project_tools = [
    get_all_projects,
    get_project,
    create_project,
    get_project_creation_status,
    get_project_teams,
    get_team_members,
]
