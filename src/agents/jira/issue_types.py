"""
JIRA Issue Types API Functions

This module provides tools for interacting with JIRA issue types through the REST API.
Based on: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/
"""

import json
from typing import Any

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_all_issue_types() -> str:
    """
    Returns all issue types.

    Useful for discovering available issue types and their properties.

    Returns:
        str: Formatted list of issue types or error message
    """
    client = get_jira_client()
    try:
        response = client.get("issuetype")

        result = "All JIRA Issue Types:\n\n"

        for issue_type in response:
            name = issue_type.get("name", "Unknown")
            issue_id = issue_type.get("id", "Unknown ID")
            description = issue_type.get("description", "No description")
            is_subtask = issue_type.get("subtask", False)

            subtask_status = "Subtask" if is_subtask else "Standard issue type"

            result += f"- {name} (ID: {issue_id})\n"
            result += f"  {subtask_status}\n"
            result += f"  Description: {description}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving issue types: {str(e)}"


@tool
def get_issue_type(issue_type_id: str) -> str:
    """
    Returns an issue type.

    Useful for getting detailed information about a specific issue type.

    Args:
        issue_type_id (str): The ID of the issue type

    Returns:
        str: Formatted information about the issue type or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issuetype/{issue_type_id}")

        name = response.get("name", "Unknown")
        description = response.get("description", "No description")
        is_subtask = response.get("subtask", False)
        avatar_id = response.get("avatarId", "No avatar")

        result = f"Issue Type: {name} (ID: {issue_type_id})\n"
        result += f"Description: {description}\n"
        result += f"Subtask: {'Yes' if is_subtask else 'No'}\n"
        result += f"Avatar ID: {avatar_id}\n"

        # Include additional fields if present
        if "scope" in response:
            scope_type = response.get("scope", {}).get("type", "Unknown")
            scope_project = response.get("scope", {}).get("project", {}).get("key", "Unknown")
            result += f"Scope: {scope_type} (Project: {scope_project})\n"

        return result
    except Exception as e:
        return f"Error retrieving issue type {issue_type_id}: {str(e)}"


@tool
def create_issue_type(
    name: str, description: str = "", type_: str = "standard", hierarchy_level: int | None = None
) -> str:
    """
    Creates an issue type.

    Useful for adding a new issue type to JIRA.
    This operation requires the JIRA admin global permission.

    Args:
        name (str): The name of the new issue type
        description (str, optional): The description of the new issue type. Defaults to "".
        type_ (str, optional): The type of the issue type. Can be 'subtask' or 'standard'. Defaults to "standard".
        hierarchy_level (int, optional): The hierarchy level of the issue type. Defaults to None.

    Returns:
        str: Success message with details of the created issue type or error message
    """
    client = get_jira_client()
    try:
        data = {"name": name, "description": description, "type": type_}

        if hierarchy_level is not None:
            data["hierarchyLevel"] = hierarchy_level

        response = client.post("issuetype", data)

        issue_type_id = response.get("id", "Unknown")
        issue_type_name = response.get("name", "Unknown")
        is_subtask = response.get("subtask", False)

        subtask_status = "subtask" if is_subtask else "standard issue type"

        return f"Issue type created successfully: {issue_type_name} (ID: {issue_type_id}, Type: {subtask_status})"
    except Exception as e:
        return f"Error creating issue type: {str(e)}"


@tool
def update_issue_type(
    issue_type_id: str,
    name: str | None = None,
    description: str | None = None,
    avatar_id: int | None = None,
) -> str:
    """
    Updates an issue type.

    Useful for modifying an existing issue type in JIRA.
    This operation requires the JIRA admin global permission.

    Args:
        issue_type_id (str): The ID of the issue type to update
        name (str, optional): The new name of the issue type. Defaults to None.
        description (str, optional): The new description of the issue type. Defaults to None.
        avatar_id (int, optional): The ID of the avatar for the issue type. Defaults to None.

    Returns:
        str: Success message with details of the updated issue type or error message
    """
    client = get_jira_client()
    try:
        data = {}

        if name is not None:
            data["name"] = name

        if description is not None:
            data["description"] = description

        if avatar_id is not None:
            data["avatarId"] = avatar_id

        # Don't send an empty update
        if not data:
            return "No updates specified"

        response = client.put(f"issuetype/{issue_type_id}", data)

        updated_name = response.get("name", "Unknown")
        is_subtask = response.get("subtask", False)

        subtask_status = "subtask" if is_subtask else "standard issue type"

        return f"Issue type updated successfully: {updated_name} (ID: {issue_type_id}, Type: {subtask_status})"
    except Exception as e:
        return f"Error updating issue type {issue_type_id}: {str(e)}"


@tool
def delete_issue_type(issue_type_id: str, alternative_issue_type_id: str | None = None) -> str:
    """
    Deletes an issue type.

    Useful for removing an issue type from JIRA.
    If the issue type is in use, an alternative issue type ID can be provided to replace it.
    This operation requires the JIRA admin global permission.

    Args:
        issue_type_id (str): The ID of the issue type to delete
        alternative_issue_type_id (str, optional): An alternative issue type ID to replace the deleted type. Defaults to None.

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        params = {}
        if alternative_issue_type_id:
            params["alternativeIssueTypeId"] = alternative_issue_type_id

        client.delete(f"issuetype/{issue_type_id}", params=params)

        alt_msg = (
            f" (replaced with issue type ID: {alternative_issue_type_id})"
            if alternative_issue_type_id
            else ""
        )
        return f"Issue type {issue_type_id} deleted successfully{alt_msg}"
    except Exception as e:
        return f"Error deleting issue type {issue_type_id}: {str(e)}"


@tool
def get_alternative_issue_types(issue_type_id: str) -> str:
    """
    Returns a list of issue types that can be used to replace a deleted issue type.

    Useful when planning to delete an issue type.
    This operation requires the JIRA admin global permission.

    Args:
        issue_type_id (str): The ID of the issue type to be deleted

    Returns:
        str: Formatted list of alternative issue types or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issuetype/{issue_type_id}/alternatives")

        result = f"Alternative issue types for {issue_type_id}:\n\n"

        for issue_type in response:
            name = issue_type.get("name", "Unknown")
            alt_id = issue_type.get("id", "Unknown ID")
            description = issue_type.get("description", "No description")
            is_subtask = issue_type.get("subtask", False)

            subtask_status = "Subtask" if is_subtask else "Standard issue type"

            result += f"- {name} (ID: {alt_id})\n"
            result += f"  {subtask_status}\n"
            result += f"  Description: {description}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving alternative issue types for {issue_type_id}: {str(e)}"


@tool
def get_issue_type_property_keys(issue_type_id: str) -> str:
    """
    Returns the keys of all properties for an issue type.

    Useful for discovering what properties are set for a specific issue type.

    Args:
        issue_type_id (str): The ID of the issue type

    Returns:
        str: Formatted list of property keys or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issuetype/{issue_type_id}/properties")

        keys = response.get("keys", [])

        if not keys:
            return f"No properties found for issue type {issue_type_id}"

        result = f"Property keys for issue type {issue_type_id}:\n\n"

        for key_info in keys:
            key = key_info.get("key", "Unknown key")
            self_link = key_info.get("self", "No link")

            result += f"- {key}\n"
            result += f"  Link: {self_link}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving property keys for issue type {issue_type_id}: {str(e)}"


@tool
def get_issue_type_property(issue_type_id: str, property_key: str) -> str:
    """
    Returns the value of a property from an issue type.

    Useful for retrieving specific property values for an issue type.

    Args:
        issue_type_id (str): The ID of the issue type
        property_key (str): The key of the property to get

    Returns:
        str: The property value or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issuetype/{issue_type_id}/properties/{property_key}")

        key = response.get("key", "Unknown key")
        value = response.get("value", {})

        result = f"Property {key} for issue type {issue_type_id}:\n\n"
        result += json.dumps(value, indent=2)

        return result
    except Exception as e:
        return f"Error retrieving property {property_key} for issue type {issue_type_id}: {str(e)}"


@tool
def set_issue_type_property(issue_type_id: str, property_key: str, value: Any) -> str:
    """
    Sets a property for an issue type.

    Useful for storing additional data with an issue type.
    This operation requires the JIRA admin global permission.

    Args:
        issue_type_id (str): The ID of the issue type
        property_key (str): The key of the property to set
        value (Any): The value of the property

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        client.put(f"issuetype/{issue_type_id}/properties/{property_key}", value)

        return f"Property {property_key} set successfully for issue type {issue_type_id}"
    except Exception as e:
        return f"Error setting property {property_key} for issue type {issue_type_id}: {str(e)}"


@tool
def delete_issue_type_property(issue_type_id: str, property_key: str) -> str:
    """
    Deletes a property from an issue type.

    Useful for removing a property that is no longer needed.
    This operation requires the JIRA admin global permission.

    Args:
        issue_type_id (str): The ID of the issue type
        property_key (str): The key of the property to delete

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        client.delete(f"issuetype/{issue_type_id}/properties/{property_key}")

        return f"Property {property_key} deleted successfully from issue type {issue_type_id}"
    except Exception as e:
        return f"Error deleting property {property_key} from issue type {issue_type_id}: {str(e)}"


# Export the tools for use in the JIRA assistant
issue_type_tools = [
    get_all_issue_types,
    get_issue_type,
    create_issue_type,
    update_issue_type,
    delete_issue_type,
    get_alternative_issue_types,
    get_issue_type_property_keys,
    get_issue_type_property,
    set_issue_type_property,
    delete_issue_type_property,
]
