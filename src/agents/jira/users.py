"""
JIRA Users API Functions

This module provides tools for interacting with JIRA users through the REST API.
"""

import json

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_current_user() -> str:
    """
    Get information about the currently authenticated user.

    Useful for verifying the authentication and permissions of the current user.

    Returns:
        str: JSON string with user details
    """
    client = get_jira_client()
    try:
        response = client.get("myself")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving current user information: {str(e)}"


@tool
def find_users(query: str, max_results: int = 10) -> str:
    """
    Search for users in JIRA based on a query string.

    Useful for finding users to assign issues to or add to projects.

    Args:
        query (str): Search string (can be name, username, or email)
        max_results (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        str: JSON string with user search results
    """
    client = get_jira_client()
    try:
        params = {"query": query, "maxResults": max_results}
        response = client.get("user/search", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error searching for users: {str(e)}"


@tool
def get_user_permissions() -> str:
    """
    Get permissions for the current user.

    Useful for understanding what actions the current user can perform in JIRA.

    Returns:
        str: JSON string with permission details
    """
    client = get_jira_client()
    try:
        response = client.get("mypermissions")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving user permissions: {str(e)}"


@tool
def get_assignable_users(project_key: str, max_results: int = 10) -> str:
    """
    Get users that can be assigned to issues in a project.

    Useful for finding users who can be assigned to issues in a specific project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")
        max_results (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        str: JSON string with assignable users
    """
    client = get_jira_client()
    try:
        params = {"project": project_key, "maxResults": max_results}
        response = client.get("user/assignable/search", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving assignable users for project {project_key}: {str(e)}"


@tool
def get_user_by_account_id(account_id: str) -> str:
    """
    Get a user by their account ID.

    Useful for retrieving detailed information about a specific user.

    Args:
        account_id (str): The account ID of the user

    Returns:
        str: JSON string with user details
    """
    client = get_jira_client()
    try:
        params = {"accountId": account_id}
        response = client.get("user", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving user with account ID {account_id}: {str(e)}"


@tool
def get_user_groups(account_id: str) -> str:
    """
    Get groups that a user belongs to.

    Useful for understanding a user's group memberships and permissions.

    Args:
        account_id (str): The account ID of the user

    Returns:
        str: JSON string with user group details
    """
    client = get_jira_client()
    try:
        params = {"accountId": account_id}
        response = client.get("user/groups", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving groups for user with account ID {account_id}: {str(e)}"


@tool
def get_user_email_by_account_id(account_id: str) -> str:
    """
    Get a user's email address by their account ID.

    Useful for getting the email address of a specific user.

    Args:
        account_id (str): The account ID of the user

    Returns:
        str: JSON string with the user's email address
    """
    client = get_jira_client()
    try:
        params = {"accountId": account_id}
        response = client.get("user/email", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving email for user with account ID {account_id}: {str(e)}"


@tool
def get_user_email_bulk(account_ids: str) -> str:
    """
    Get email addresses for multiple users by their account IDs.

    Useful for getting email addresses for a group of users at once.

    Args:
        account_ids (str): Comma-separated list of account IDs

    Returns:
        str: JSON string with user email details
    """
    client = get_jira_client()
    try:
        account_id_list = [aid.strip() for aid in account_ids.split(",")]
        params = {"accountId": account_id_list}
        response = client.get("user/email/bulk", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving emails for users: {str(e)}"


@tool
def get_all_users(max_results: int = 50) -> str:
    """
    Get all users in the JIRA instance.

    Useful for getting a list of all users in the JIRA instance.

    Args:
        max_results (int, optional): Maximum number of results to return. Defaults to 50.

    Returns:
        str: JSON string with all users
    """
    client = get_jira_client()
    try:
        params = {"maxResults": max_results}
        response = client.get("users", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving all users: {str(e)}"


@tool
def get_account_ids_for_users(usernames: str) -> str:
    """
    Get account IDs for a list of usernames.

    Useful for converting usernames to account IDs for API calls.

    Args:
        usernames (str): Comma-separated list of usernames

    Returns:
        str: JSON string with account ID details
    """
    client = get_jira_client()
    try:
        username_list = [username.strip() for username in usernames.split(",")]
        params = {"username": username_list}
        response = client.get("user/bulk/migration", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving account IDs for usernames: {str(e)}"


@tool
def get_user_default_columns(account_id: str) -> str:
    """
    Get a user's default issue navigator columns.

    Useful for understanding which columns a user sees in their issue navigator.

    Args:
        account_id (str): The account ID of the user

    Returns:
        str: JSON string with default column details
    """
    client = get_jira_client()
    try:
        params = {"accountId": account_id}
        response = client.get("user/columns", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving default columns for user with account ID {account_id}: {str(e)}"


@tool
def set_user_default_columns(account_id: str, columns: str) -> str:
    """
    Set a user's default issue navigator columns.

    Useful for customizing which columns a user sees in their issue navigator.

    Args:
        account_id (str): The account ID of the user
        columns (str): Comma-separated list of column names

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        column_list = [column.strip() for column in columns.split(",")]
        params = {"accountId": account_id}
        data = column_list

        client.put("user/columns", data=data, params=params)

        return f"Default columns for user with account ID {account_id} set successfully"
    except Exception as e:
        return f"Error setting default columns for user with account ID {account_id}: {str(e)}"


@tool
def reset_user_default_columns(account_id: str) -> str:
    """
    Reset a user's default issue navigator columns to the system default.

    Useful for resetting a user's issue navigator columns to the default.

    Args:
        account_id (str): The account ID of the user

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        params = {"accountId": account_id}
        client.delete("user/columns", params=params)

        return f"Default columns for user with account ID {account_id} reset successfully"
    except Exception as e:
        return f"Error resetting default columns for user with account ID {account_id}: {str(e)}"


# Export the tools for use in the JIRA assistant
user_tools = [
    get_current_user,
    find_users,
    get_user_permissions,
    get_assignable_users,
    get_user_by_account_id,
    get_user_groups,
    get_user_email_by_account_id,
    get_user_email_bulk,
    get_all_users,
    get_account_ids_for_users,
    get_user_default_columns,
    set_user_default_columns,
    reset_user_default_columns,
]
