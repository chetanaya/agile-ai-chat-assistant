"""
JIRA Sprints API Functions

This module provides tools for interacting with JIRA Sprints through the REST API.
"""

import json
from typing import Any

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def create_sprint(
    name: str,
    origin_board_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
    goal: str | None = None,
) -> str:
    """
    Creates a new sprint.

    Useful for creating a new sprint in a board with the specified details.

    Args:
        name (str): The name of the sprint
        origin_board_id (int): The ID of the board in which to create the sprint
        start_date (str, optional): The start date of the sprint in ISO format (e.g., "2023-04-11T15:22:00.000+10:00")
        end_date (str, optional): The end date of the sprint in ISO format (e.g., "2023-04-20T01:22:00.000+10:00")
        goal (str, optional): The goal of the sprint

    Returns:
        str: JSON string with created sprint details
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        # Prepare data for the API request
        data = {"name": name, "originBoardId": origin_board_id}

        # Add optional fields if provided
        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date
        if goal:
            data["goal"] = goal

        response = client.post("sprint", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))

    except Exception as e:
        return f"Error creating sprint: {str(e)}"


@tool
def get_sprint(sprint_id: int) -> str:
    """
    Retrieves details of a specific sprint by its ID.

    Useful for getting information about a particular sprint such as name, state, start date, end date, etc.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)

    Returns:
        str: JSON string with sprint details
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        response = client.get(f"sprint/{sprint_id}")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))

    except Exception as e:
        return f"Error retrieving sprint {sprint_id}: {str(e)}"


@tool
def update_sprint(
    sprint_id: int,
    name: str | None = None,
    goal: str | None = None,
    state: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    complete_date: str | None = None,
) -> str:
    """
    Updates an existing sprint.

    Useful for modifying sprint details such as name, goal, dates, or state.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        name (str, optional): New name for the sprint
        goal (str, optional): New goal for the sprint
        state (str, optional): New state for the sprint (e.g., "future", "active", "closed")
        start_date (str, optional): New start date in ISO format (e.g., "2023-04-11T15:22:00.000+10:00")
        end_date (str, optional): New end date in ISO format (e.g., "2023-04-20T01:22:00.000+10:00")
        complete_date (str, optional): New complete date in ISO format (e.g., "2023-04-20T11:04:00.000+10:00")

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        data = {}

        # Add optional fields if provided
        if name is not None:
            data["name"] = name
        if goal is not None:
            data["goal"] = goal
        if state is not None:
            data["state"] = state
        if start_date is not None:
            data["startDate"] = start_date
        if end_date is not None:
            data["endDate"] = end_date
        if complete_date is not None:
            data["completeDate"] = complete_date

        # Don't send an empty update
        if not data:
            return "No updates specified"

        client.put(f"sprint/{sprint_id}", data)
        return f"Sprint {sprint_id} updated successfully"

    except Exception as e:
        return f"Error updating sprint {sprint_id}: {str(e)}"


@tool
def delete_sprint(sprint_id: int) -> str:
    """
    Deletes a sprint.

    Useful for removing a sprint that is no longer needed.
    Warning: This action cannot be undone.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        client.delete(f"sprint/{sprint_id}")
        return f"Sprint {sprint_id} deleted successfully"

    except Exception as e:
        return f"Error deleting sprint {sprint_id}: {str(e)}"


@tool
def get_sprint_issues(
    sprint_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues in a sprint.

    Useful for retrieving issues assigned to a specific sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues in the sprint
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: JSON string with sprint issues data
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql

        if fields:
            params["fields"] = ",".join(fields)

        response = client.get(f"sprint/{sprint_id}/issue", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))

    except Exception as e:
        return f"Error retrieving issues for sprint {sprint_id}: {str(e)}"


@tool
def move_issues_to_sprint(
    sprint_id: int,
    issues: list[str],
    rank_before_issue: str | None = None,
    rank_after_issue: str | None = None,
    rank_custom_field_id: int | None = None,
) -> str:
    """
    Moves issues to a sprint and optionally ranks them.

    Useful for assigning issues to a sprint and adjusting their order within the sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        issues (List[str]): List of issue keys or IDs to move to the sprint
        rank_before_issue (str, optional): Issue key to place the issues before
        rank_after_issue (str, optional): Issue key to place the issues after
        rank_custom_field_id (int, optional): The ID of the custom field that stores rank

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        data = {"issues": issues}

        if rank_before_issue:
            data["rankBeforeIssue"] = rank_before_issue

        if rank_after_issue:
            data["rankAfterIssue"] = rank_after_issue

        if rank_custom_field_id:
            data["rankCustomFieldId"] = rank_custom_field_id

        client.post(f"sprint/{sprint_id}/issue", data)
        return f"Successfully moved {len(issues)} issues to sprint {sprint_id}"

    except Exception as e:
        return f"Error moving issues to sprint {sprint_id}: {str(e)}"


@tool
def get_sprint_properties_keys(sprint_id: int) -> str:
    """
    Gets the keys of all properties stored for a sprint.

    Useful for discovering what custom properties are available for a sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)

    Returns:
        str: JSON string with property keys
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        response = client.get(f"sprint/{sprint_id}/properties")

        keys = response.get("keys", [])

        if not keys:
            return f"No properties found for sprint {sprint_id}"

        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))

    except Exception as e:
        return f"Error retrieving property keys for sprint {sprint_id}: {str(e)}"


@tool
def get_sprint_property(sprint_id: int, property_key: str) -> str:
    """
    Gets the value of a specific sprint property.

    Useful for retrieving custom data stored on a sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        property_key (str): The key of the property to get

    Returns:
        str: JSON string with Property value
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        response = client.get(f"sprint/{sprint_id}/properties/{property_key}")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))

    except Exception as e:
        return f"Error retrieving property '{property_key}' for sprint {sprint_id}: {str(e)}"


@tool
def set_sprint_property(sprint_id: int, property_key: str, value: Any) -> str:
    """
    Sets the value of a sprint property.

    Useful for storing custom data on a sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        property_key (str): The key of the property to set
        value (Any): The value to set (any JSON-serializable data)

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        client.put(f"sprint/{sprint_id}/properties/{property_key}", value)
        return f"Successfully set property '{property_key}' for sprint {sprint_id}"

    except Exception as e:
        return f"Error setting property '{property_key}' for sprint {sprint_id}: {str(e)}"


@tool
def delete_sprint_property(sprint_id: int, property_key: str) -> str:
    """
    Deletes a sprint property.

    Useful for removing custom data stored on a sprint.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        property_key (str): The key of the property to delete

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        client.delete(f"sprint/{sprint_id}/properties/{property_key}")
        return f"Successfully deleted property '{property_key}' from sprint {sprint_id}"

    except Exception as e:
        return f"Error deleting property '{property_key}' from sprint {sprint_id}: {str(e)}"


@tool
def swap_sprint(sprint_id: int, sprint_to_swap_with: int) -> str:
    """
    Swaps the position of two sprints in the backlog.

    Useful for reordering sprints within a board.

    Args:
        sprint_id (int): The sprint ID (e.g., 123)
        sprint_to_swap_with (int): The ID of the sprint to swap positions with

    Returns:
        str: Success or error message
    """
    client = get_jira_client(api_base_path="rest/agile/1.0/")
    try:
        data = {"sprintToSwapWith": sprint_to_swap_with}

        client.post(f"sprint/{sprint_id}/swap", data)
        return f"Successfully swapped positions of sprints {sprint_id} and {sprint_to_swap_with}"

    except Exception as e:
        return f"Error swapping sprint positions: {str(e)}"


# Export the tools for use in the JIRA assistant
sprint_tools = [
    create_sprint,
    get_sprint,
    update_sprint,
    delete_sprint,
    get_sprint_issues,
    move_issues_to_sprint,
    get_sprint_properties_keys,
    get_sprint_property,
    set_sprint_property,
    delete_sprint_property,
    swap_sprint,
]
