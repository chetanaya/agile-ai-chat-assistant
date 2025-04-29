"""
JIRA Projects API Functions

This module provides tools for interacting with JIRA projects through the REST API.
"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool, tool

from agents.jira.utils import get_jira_client


@tool
def get_all_projects() -> str:
    """
    Get a list of all projects in JIRA that the user has access to.

    Useful for getting an overview of available projects.

    Returns:
        str: JSON string with project details
    """
    client = get_jira_client()
    try:
        response = client.get("project")

        result = "Available JIRA Projects:\n\n"

        for project in response:
            key = project.get("key", "Unknown")
            name = project.get("name", "Unnamed Project")
            result += f"- {key}: {name}\n"

        return result
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"


@tool
def get_project(project_key: str) -> str:
    """
    Get detailed information about a specific JIRA project.

    Useful for learning about project settings, lead, and other details.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with project details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}")

        key = response.get("key", "Unknown")
        name = response.get("name", "Unnamed Project")
        description = response.get("description", "No description")
        lead = response.get("lead", {}).get("displayName", "Unknown")

        result = f"Project: {name} ({key})\n"
        result += f"Lead: {lead}\n"
        result += f"Description: {description}\n"

        return result
    except Exception as e:
        return f"Error retrieving project {project_key}: {str(e)}"


@tool
def get_project_components(project_key: str) -> str:
    """
    Get all components for a specific project.

    Useful for understanding how a project is organized into components.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with component details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/components")

        result = f"Components for project {project_key}:\n\n"

        if not response:
            return f"No components found for project {project_key}"

        for component in response:
            name = component.get("name", "Unnamed Component")
            description = component.get("description", "No description")
            lead = component.get("lead", {}).get("displayName", "No lead assigned")

            result += f"- {name}\n"
            result += f"  Description: {description}\n"
            result += f"  Lead: {lead}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving components for project {project_key}: {str(e)}"


@tool
def get_project_versions(project_key: str) -> str:
    """
    Get all versions for a specific project.

    Useful for understanding version management in a project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with version details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/versions")

        result = f"Versions for project {project_key}:\n\n"

        if not response:
            return f"No versions found for project {project_key}"

        for version in response:
            name = version.get("name", "Unnamed Version")
            description = version.get("description", "No description")
            released = "Released" if version.get("released", False) else "Unreleased"

            result += f"- {name} ({released})\n"
            if description:
                result += f"  Description: {description}\n"

        return result
    except Exception as e:
        return f"Error retrieving versions for project {project_key}: {str(e)}"


@tool
def get_project_statuses(project_key: str) -> str:
    """
    Get all issue statuses for a specific project.

    Useful for understanding workflow and possible issue states in a project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with status details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/statuses")

        result = f"Statuses for project {project_key}:\n\n"

        for item in response:
            issue_type = item.get("name", "Unknown Issue Type")
            result += f"Issue Type: {issue_type}\n"

            statuses = item.get("statuses", [])
            for status in statuses:
                name = status.get("name", "Unknown Status")
                category = status.get("statusCategory", {}).get("name", "Unknown Category")
                result += f"  - {name} ({category})\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving statuses for project {project_key}: {str(e)}"


@tool
def get_project_roles(project_key: str) -> str:
    """
    Get all roles for a specific project.

    Useful for understanding permission structure and roles in a project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with role details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/role")

        result = f"Roles for project {project_key}:\n\n"

        for role_name, role_url in response.items():
            result += f"- {role_name}\n"

        return result
    except Exception as e:
        return f"Error retrieving roles for project {project_key}: {str(e)}"


@tool
def create_project(
    name: str,
    key: str,
    project_type_key: str = "business",
    description: str = "",
    lead_account_id: Optional[str] = None,
) -> str:
    """
    Create a new JIRA project.

    Useful for setting up a new project in JIRA.

    Args:
        name (str): The name of the project
        key (str): The project key (must be unique, uppercase letters)
        project_type_key (str, optional): The project type. Defaults to "business".
            Options: "business", "software", "service_desk"
        description (str, optional): The project description. Defaults to "".
        lead_account_id (str, optional): The account ID of the project lead.
            If not provided, the current user will be used.

    Returns:
        str: Success message with created project details or error message
    """
    client = get_jira_client()
    try:
        data = {
            "name": name,
            "key": key,
            "projectTypeKey": project_type_key,
        }

        if description:
            data["description"] = description

        if lead_account_id:
            data["leadAccountId"] = lead_account_id

        response = client.post("project", data)

        return (
            f"Project created successfully:\nKey: {response.get('key')}\nID: {response.get('id')}"
        )
    except Exception as e:
        return f"Error creating project: {str(e)}"


@tool
def update_project(
    project_key: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    lead_account_id: Optional[str] = None,
) -> str:
    """
    Update an existing JIRA project.

    Useful for modifying project details like name, description or project lead.

    Args:
        project_key (str): The project key (e.g., "PROJECT")
        name (str, optional): The new name for the project
        description (str, optional): The new description for the project
        lead_account_id (str, optional): The account ID of the new project lead

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {}

        if name:
            data["name"] = name

        if description:
            data["description"] = description

        if lead_account_id:
            data["leadAccountId"] = lead_account_id

        if not data:
            return "No updates specified for the project"

        response = client.put(f"project/{project_key}", data)

        return f"Project {project_key} updated successfully"
    except Exception as e:
        return f"Error updating project {project_key}: {str(e)}"


@tool
def delete_project(project_key: str) -> str:
    """
    Delete a JIRA project.

    Useful for removing projects that are no longer needed.
    Warning: This action cannot be undone immediately.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        response = client.delete(f"project/{project_key}")

        return f"Project {project_key} deleted successfully"
    except Exception as e:
        return f"Error deleting project {project_key}: {str(e)}"


@tool
def archive_project(project_key: str) -> str:
    """
    Archive a JIRA project.

    Useful for making a project inactive without deleting it.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        response = client.post(f"project/{project_key}/archive", {})

        return f"Project {project_key} archived successfully"
    except Exception as e:
        return f"Error archiving project {project_key}: {str(e)}"


@tool
def restore_project(project_key: str) -> str:
    """
    Restore a deleted or archived JIRA project.

    Useful for recovering projects that were archived or recently deleted.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        response = client.post(f"project/{project_key}/restore", {})

        return f"Project {project_key} restored successfully"
    except Exception as e:
        return f"Error restoring project {project_key}: {str(e)}"


@tool
def get_project_issue_type_hierarchy(project_key: str) -> str:
    """
    Get the issue type hierarchy for a project.

    Useful for understanding the structure of issue types in a project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with issue type hierarchy
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/hierarchy")

        result = f"Issue Type Hierarchy for project {project_key}:\n\n"

        if not response:
            return f"No issue type hierarchy found for project {project_key}"

        project_details = response.get("projectId", "Unknown project ID")
        root_level = response.get("hierarchy", [])

        for level in root_level:
            level_id = level.get("entityId", "Unknown")
            level_name = level.get("name", "Unknown Level")

            result += f"- {level_name} (ID: {level_id})\n"

            # Process children if any
            children = level.get("children", [])
            for child in children:
                child_id = child.get("entityId", "Unknown")
                child_name = child.get("name", "Unknown Child Level")

                result += f"  - {child_name} (ID: {child_id})\n"

        return result
    except Exception as e:
        return f"Error retrieving issue type hierarchy for project {project_key}: {str(e)}"


@tool
def get_project_notification_scheme(project_key: str) -> str:
    """
    Get the notification scheme for a project.

    Useful for understanding who gets notified about project events.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: JSON string with notification scheme details
    """
    client = get_jira_client()
    try:
        response = client.get(f"project/{project_key}/notificationscheme")

        scheme = response.get("notificationScheme", {})

        scheme_id = scheme.get("id", "Unknown ID")
        scheme_name = scheme.get("name", "Unknown Scheme")
        scheme_description = scheme.get("description", "No description")

        result = f"Notification Scheme for project {project_key}:\n"
        result += f"Name: {scheme_name}\n"
        result += f"ID: {scheme_id}\n"
        result += f"Description: {scheme_description}\n"

        return result
    except Exception as e:
        return f"Error retrieving notification scheme for project {project_key}: {str(e)}"


@tool
def search_projects(
    query: Optional[str] = None, project_type_key: Optional[str] = None, max_results: int = 10
) -> str:
    """
    Search for JIRA projects with pagination.

    Useful for finding specific projects by name or type.

    Args:
        query (str, optional): Text to search for in the project name
        project_type_key (str, optional): The project type to filter by.
            Options: "business", "software", "service_desk"
        max_results (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        str: JSON string with project search results
    """
    client = get_jira_client()
    try:
        params = {"maxResults": max_results}

        if query:
            params["query"] = query

        if project_type_key:
            params["typeKey"] = project_type_key

        response = client.get("project/search", params=params)

        result = "Project Search Results:\n\n"

        projects = response.get("values", [])
        total = response.get("total", 0)

        result += f"Found {total} projects. Showing {len(projects)} results:\n\n"

        for project in projects:
            key = project.get("key", "Unknown")
            name = project.get("name", "Unnamed Project")
            project_type = project.get("projectTypeKey", "Unknown type")

            result += f"- {name} ({key})\n"
            result += f"  Type: {project_type}\n\n"

        return result
    except Exception as e:
        return f"Error searching projects: {str(e)}"


@tool
def get_recent_projects(max_results: int = 10) -> str:
    """
    Get a list of recently viewed projects for the current user.

    Useful for quickly accessing projects the user has been working with.

    Args:
        max_results (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        str: JSON string with recent project details
    """
    client = get_jira_client()
    try:
        response = client.get("project/recent")

        result = "Recently viewed projects:\n\n"

        if not response:
            return "No recently viewed projects found"

        # Limit to max_results
        projects = response[:max_results]

        for project in projects:
            key = project.get("key", "Unknown")
            name = project.get("name", "Unnamed Project")
            last_viewed = project.get("lastViewed", "Unknown time")

            result += f"- {name} ({key})\n"
            result += f"  Last viewed: {last_viewed}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving recent projects: {str(e)}"


# Export the tools for use in the JIRA assistant
project_tools = [
    get_all_projects,
    get_project,
    get_project_components,
    get_project_versions,
    get_project_statuses,
    get_project_roles,
    create_project,
    update_project,
    delete_project,
    archive_project,
    restore_project,
    get_project_issue_type_hierarchy,
    get_project_notification_scheme,
    search_projects,
    get_recent_projects,
]
