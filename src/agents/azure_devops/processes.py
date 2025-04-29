"""
Azure DevOps Process Templates and Teams API Functions

This module provides tools for interacting with Azure DevOps process templates, teams,
and organization-level settings through the API.
"""

import json

from langchain_core.tools import tool

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_process_templates() -> str:
    """
    Get all process templates in the Azure DevOps organization.

    Returns:
        str: JSON string containing all process templates
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Get process templates
        process_templates = core_client.get_process_templates()

        # Format process templates for display
        formatted_templates = []
        for template in process_templates:
            formatted_templates.append(
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "type": template.type,
                    "is_default": template.is_default,
                    "url": template.url,
                }
            )

        return json.dumps(formatted_templates, indent=2)
    except Exception as e:
        return f"Error retrieving process templates: {str(e)}"


@tool
def get_process_template(process_template_id: str) -> str:
    """
    Get details for a specific process template by ID.

    Args:
        process_template_id (str): The ID of the process template

    Returns:
        str: JSON string containing process template details
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Get process template
        template = core_client.get_process_template(process_template_id)

        # Format template for display
        formatted_template = {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "type": template.type,
            "is_default": template.is_default,
            "url": template.url,
        }

        return json.dumps(formatted_template, indent=2)
    except Exception as e:
        return f"Error retrieving process template details: {str(e)}"


@tool
def create_team(project_name_or_id: str, team_name: str, description: str | None = None) -> str:
    """
    Create a new team in a project.

    Args:
        project_name_or_id (str): The name or ID of the project
        team_name (str): The name of the team
        description (str, optional): The description of the team

    Returns:
        str: JSON string containing the created team details
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Create team object with optional description
        team_params = {"name": team_name}
        if description:
            team_params["description"] = description

        # Create team
        created_team = core_client.create_team(team_params, project_name_or_id)

        # Format team for display
        formatted_team = {
            "id": created_team.id,
            "name": created_team.name,
            "description": created_team.description,
            "url": created_team.url,
        }

        return json.dumps(formatted_team, indent=2)
    except Exception as e:
        return f"Error creating team: {str(e)}"


@tool
def update_team(
    project_name_or_id: str,
    team_name_or_id: str,
    new_name: str | None = None,
    new_description: str | None = None,
) -> str:
    """
    Update a team's name and/or description.

    Args:
        project_name_or_id (str): The name or ID of the project
        team_name_or_id (str): The name or ID of the team
        new_name (str, optional): The new name for the team
        new_description (str, optional): The new description for the team

    Returns:
        str: JSON string containing the updated team details
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Create patch document with changes
        team_patch = {}
        if new_name:
            team_patch["name"] = new_name
        if new_description:
            team_patch["description"] = new_description

        # No changes requested
        if not team_patch:
            return "No changes requested for team update."

        # Update team
        updated_team = core_client.update_team(team_patch, project_name_or_id, team_name_or_id)

        # Format team for display
        formatted_team = {
            "id": updated_team.id,
            "name": updated_team.name,
            "description": updated_team.description,
            "url": updated_team.url,
        }

        return json.dumps(formatted_team, indent=2)
    except Exception as e:
        return f"Error updating team: {str(e)}"


@tool
def delete_team(project_name_or_id: str, team_name_or_id: str) -> str:
    """
    Delete a team from a project.

    Args:
        project_name_or_id (str): The name or ID of the project
        team_name_or_id (str): The name or ID of the team

    Returns:
        str: Confirmation message
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Delete team
        core_client.delete_team(project_name_or_id, team_name_or_id)

        return f"Team '{team_name_or_id}' was successfully deleted from project '{project_name_or_id}'."
    except Exception as e:
        return f"Error deleting team: {str(e)}"


@tool
def get_team_settings(project_name_or_id: str, team_name_or_id: str) -> str:
    """
    Get team settings.

    Args:
        project_name_or_id (str): The name or ID of the project
        team_name_or_id (str): The name or ID of the team

    Returns:
        str: JSON string containing team settings
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Get team settings
        team_settings = core_client.get_team_settings(project_name_or_id, team_name_or_id)

        # Format settings for display
        formatted_settings = {
            "backlog_iteration": team_settings.backlog_iteration.name
            if team_settings.backlog_iteration
            else None,
            "backlog_visibilities": team_settings.backlog_visibilities,
            "bugs_behavior": team_settings.bugs_behavior,
            "default_iteration": team_settings.default_iteration.name
            if team_settings.default_iteration
            else None,
            "working_days": team_settings.working_days,
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error retrieving team settings: {str(e)}"


@tool
def get_project_properties(project_name_or_id: str) -> str:
    """
    Get properties for a project.

    Args:
        project_name_or_id (str): The name or ID of the project

    Returns:
        str: JSON string containing project properties
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Get project properties
        properties = core_client.get_project_properties(project_name_or_id)

        # Format properties for display
        formatted_properties = []
        for prop in properties:
            formatted_properties.append(
                {
                    "name": prop.name,
                    "value": prop.value,
                }
            )

        return json.dumps(formatted_properties, indent=2)
    except Exception as e:
        return f"Error retrieving project properties: {str(e)}"


@tool
def set_project_property(project_name_or_id: str, property_name: str, property_value: str) -> str:
    """
    Set a property for a project.

    Args:
        project_name_or_id (str): The name or ID of the project
        property_name (str): The name of the property
        property_value (str): The value of the property

    Returns:
        str: Confirmation message
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Set project property
        core_client.set_project_properties(
            project_name_or_id, [{"name": property_name, "value": property_value}]
        )

        return (
            f"Property '{property_name}' was successfully set for project '{project_name_or_id}'."
        )
    except Exception as e:
        return f"Error setting project property: {str(e)}"


@tool
def get_organization_info() -> str:
    """
    Get information about the Azure DevOps organization.

    Returns:
        str: JSON string containing organization information
    """
    try:
        client = get_azure_devops_client()
        core_client = client.get_client()

        # Get organization information
        org_info = core_client.get_connected_service_details()

        # Format organization info for display
        formatted_info = []
        for service in org_info:
            formatted_info.append(
                {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "type": service.type,
                    "url": service.url,
                }
            )

        return json.dumps(formatted_info, indent=2)
    except Exception as e:
        return f"Error retrieving organization information: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
process_and_team_tools = [
    get_process_templates,
    get_process_template,
    create_team,
    update_team,
    delete_team,
    get_team_settings,
    get_project_properties,
    set_project_property,
    get_organization_info,
]
