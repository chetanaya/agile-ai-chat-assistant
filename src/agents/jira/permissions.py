"""
JIRA Permissions API Functions

This module provides tools for interacting with JIRA permissions through the REST API.
These endpoints help check permissions before taking actions rather than discovering permission issues later.
Based on: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/
"""

from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_my_permissions(
    permissions: Optional[str] = None,
    project_key: Optional[str] = None,
    project_id: Optional[str] = None,
    issue_key: Optional[str] = None,
    issue_id: Optional[str] = None,
) -> str:
    """
    Get permissions for the current user.

    Useful for determining what actions the current user can perform before attempting them.

    Args:
        permissions (str, optional): Comma-separated list of permissions to check. e.g. "BROWSE_PROJECTS,EDIT_ISSUES"
        project_key (str, optional): Key of the project to check permissions for
        project_id (str, optional): ID of the project to check permissions for
        issue_key (str, optional): Key of the issue to check permissions for
        issue_id (str, optional): ID of the issue to check permissions for

    Returns:
        str: JSON string with permission details
    """
    client = get_jira_client()
    try:
        params = {}
        if permissions:
            params["permissions"] = permissions
        if project_key:
            params["projectKey"] = project_key
        if project_id:
            params["projectId"] = project_id
        if issue_key:
            params["issueKey"] = issue_key
        if issue_id:
            params["issueId"] = issue_id

        response = client.get("mypermissions", params=params)
        permissions_data = response.get("permissions", {})

        result = "Your JIRA Permissions:\n\n"

        for perm_key, perm_info in permissions_data.items():
            has_permission = perm_info.get("havePermission", False)
            description = perm_info.get("description", "No description")
            perm_type = perm_info.get("type", "Unknown")

            status = "✓" if has_permission else "✗"
            result += f"{status} {perm_key}: {description} (Type: {perm_type})\n"

        return result
    except Exception as e:
        return f"Error retrieving user permissions: {str(e)}"


@tool
def get_all_permissions() -> str:
    """
    Get all permission types in JIRA.

    Useful for understanding what permissions exist in the JIRA instance.

    Returns:
        str: JSON string with all permission types
    """
    client = get_jira_client()
    try:
        response = client.get("permissions")
        permissions = response.get("permissions", {})

        result = "All JIRA Permissions:\n\n"

        for perm_key, perm_info in permissions.items():
            name = perm_info.get("name", "Unknown")
            description = perm_info.get("description", "No description")
            perm_type = perm_info.get("type", "Unknown")

            result += f"- {name} ({perm_key})\n"
            result += f"  Description: {description}\n"
            result += f"  Type: {perm_type}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving all permissions: {str(e)}"


@tool
def check_bulk_permissions(
    global_permissions: Optional[List[str]] = None,
    project_permissions: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Check multiple permissions for the current user.

    Useful for checking if the user has all the required permissions before performing operations.

    Args:
        global_permissions (List[str], optional): Global permissions to check
        project_permissions (List[Dict[str, Any]], optional): Project permissions to check

    Returns:
        str: JSON string with permission check results
    """
    client = get_jira_client()
    try:
        data = {}
        if global_permissions:
            data["globalPermissions"] = global_permissions
        if project_permissions:
            data["projectPermissions"] = project_permissions

        if not data:
            return "No permissions specified to check"

        response = client.post("permissions/check", data)

        result = "Permission Check Results:\n\n"

        # Process global permissions
        global_perms = response.get("globalPermissions", [])
        if global_perms:
            result += "Global Permissions Granted:\n"
            for perm in global_perms:
                result += f"- {perm}\n"
            result += "\n"

        # Process project permissions
        project_perms = response.get("projectPermissions", [])
        if project_perms:
            result += "Project Permissions Granted:\n"
            for perm_info in project_perms:
                permission = perm_info.get("permission", "Unknown")
                projects = perm_info.get("projects", [])
                issues = perm_info.get("issues", [])

                result += f"- {permission}:\n"
                if projects:
                    result += f"  Projects: {', '.join(map(str, projects))}\n"
                if issues:
                    result += f"  Issues: {', '.join(map(str, issues))}\n"

        if not global_perms and not project_perms:
            result += "No permissions granted for the requested checks.\n"

        return result
    except Exception as e:
        return f"Error checking bulk permissions: {str(e)}"


@tool
def get_permitted_projects(permissions: List[str]) -> str:
    """
    Get all projects the user has specific permissions for.

    Useful for finding all projects where the user can perform specific actions.

    Args:
        permissions (List[str]): List of permissions to check

    Returns:
        str: JSON string with projects where user has specified permissions
    """
    client = get_jira_client()
    try:
        data = {"permissions": permissions}
        response = client.post("permissions/project", data)

        projects = response.get("projects", [])

        result = f"Projects where you have permissions {', '.join(permissions)}:\n\n"

        if not projects:
            return (
                f"No projects found where you have all these permissions: {', '.join(permissions)}"
            )

        for project in projects:
            project_id = project.get("id", "Unknown ID")
            project_key = project.get("key", "Unknown Key")

            result += f"- {project_key} (ID: {project_id})\n"

        return result
    except Exception as e:
        return f"Error retrieving permitted projects: {str(e)}"


# Export the tools for use in the JIRA assistant
permission_tools = [
    get_my_permissions,
    get_all_permissions,
    check_bulk_permissions,
    get_permitted_projects,
]
