"""
JIRA Boards API Functions

This module provides tools for interacting with JIRA Boards through the REST API.
"""

import json
from typing import Any

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_all_boards(
    start_at: int = 0,
    max_results: int = 50,
    type_: str | None = None,
    name: str | None = None,
    project_key_or_id: str | None = None,
) -> str:
    """
    Returns all boards. This only includes boards that the user has permission to view.

    Useful for listing all available boards in JIRA.

    Args:
        start_at (int, optional): The starting index of the returned boards. Defaults to 0.
        max_results (int, optional): The maximum number of boards to return per page. Defaults to 50.
        type_ (str, optional): Filters results to boards of the specified type. Valid values: 'scrum', 'kanban'.
        name (str, optional): Filters results to boards that match or partially match the specified name.
        project_key_or_id (str, optional): Filters results to boards that are relevant to a project.

    Returns:
        str: JSON string with board details
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        # Add optional parameters if provided
        if type_:
            params["type"] = type_
        if name:
            params["name"] = name
        if project_key_or_id:
            params["projectKeyOrId"] = project_key_or_id

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get("board", params=params)
            return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving boards: {str(e)}"


@tool
def create_board(
    name: str,
    type_: str,
    filter_id: int | None = None,
    location_type: str | None = None,
    location_id: int | None = None,
) -> str:
    """
    Creates a new board. Board name, type and filter ID is required.

    Useful for setting up a new board in JIRA.

    Args:
        name (str): Name of the board to create
        type_ (str): Type of board to create (e.g., 'scrum', 'kanban')
        filter_id (int, optional): ID of a filter that the user has permissions to view
        location_type (str, optional): Type of location for the board (e.g., 'project')
        location_id (int, optional): ID of the location for the board

    Returns:
        str: JSON string with created board details
    """
    client = get_jira_client()
    try:
        # Prepare data for the API request
        data = {"name": name, "type": type_}

        # Add optional fields if provided
        if filter_id:
            data["filterId"] = filter_id
        if location_type:
            data["location"] = {"type": location_type}
            if location_id:
                data["location"]["projectId"] = location_id

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.post("board", data)

            board_id = response.get("id", "Unknown")
            board_name = response.get("name", "Unknown")
            board_type = response.get("type", "Unknown")

            return f"Board created successfully: ID {board_id} - {board_name} ({board_type})"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error creating board: {str(e)}"


@tool
def get_board_by_filter_id(filter_id: int) -> str:
    """
    Returns any boards which use the provided filter id. This method can be executed by users
    without a valid software license in order to find which boards are using a particular filter.

    Useful for finding boards that use a specific filter.

    Args:
        filter_id (int): The ID of the filter to search for

    Returns:
        str: Formatted list of boards that use the specified filter
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/filter/{filter_id}")

            boards = response.get("values", [])
            total = response.get("total", 0)

            if not boards:
                return f"No boards found using filter ID {filter_id}"

            result = f"Found {len(boards)} of {total} total boards using filter ID {filter_id}:\n\n"

            for board in boards:
                board_id = board.get("id", "Unknown")
                board_name = board.get("name", "Unknown")
                board_type = board.get("type", "Unknown")

                result += f"- Board ID: {board_id}, Name: {board_name}, Type: {board_type}\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving boards for filter ID {filter_id}: {str(e)}"


@tool
def get_board(board_id: int) -> str:
    """
    Retrieves details of a specific board by its ID.

    Useful for getting information about a particular board such as name, type, and configuration.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: JSON string with board details
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}")
            return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving board {board_id}: {str(e)}"


@tool
def delete_board(board_id: int) -> str:
    """
    Deletes a board.

    Useful for removing a board that is no longer needed.
    Warning: This action cannot be undone.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            client.delete(f"board/{board_id}")
            return f"Board {board_id} deleted successfully"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error deleting board {board_id}: {str(e)}"


@tool
def get_backlog_issues(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues in the backlog of a board.

    Useful for retrieving issues that are in the backlog of a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues in the backlog
        validate_query (bool, optional): Whether to validate the JQL query. Defaults to True.
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: Formatted list of issues in the backlog
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
            params["validateQuery"] = validate_query

        if fields:
            params["fields"] = ",".join(fields)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/backlog", params=params)

            issues = response.get("issues", [])
            total = response.get("total", 0)

            if not issues:
                return f"No issues found in the backlog of board {board_id}"

            result = f"Found {len(issues)} of {total} total issues in the backlog of board {board_id}:\n\n"

            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown type")

                result += f"- {key} [{issue_type}]: {summary} ({status})\n"

            if len(issues) < total:
                result += f"\nShowing {len(issues)} of {total} issues. Use start_at parameter to see more."

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving backlog issues for board {board_id}: {str(e)}"


@tool
def get_board_configuration(board_id: int) -> str:
    """
    Gets the configuration of a board.

    Useful for retrieving the detailed configuration of a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Formatted board configuration details
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/configuration")

            id = response.get("id", "Unknown")
            name = response.get("name", "Unknown")

            result = f"Board Configuration for ID {id} - {name}:\n\n"

            # Add column configuration if available
            if "columnConfig" in response:
                columns = response.get("columnConfig", {}).get("columns", [])
                result += "Column Configuration:\n"
                for column in columns:
                    column_name = column.get("name", "Unknown")
                    statuses = [
                        status.get("name", "Unknown") for status in column.get("statuses", [])
                    ]
                    result += f"- Column: {column_name}, Statuses: {', '.join(statuses)}\n"
                result += "\n"

            # Add estimation configuration if available
            if "estimation" in response:
                estimation = response.get("estimation", {})
                estimation_type = estimation.get("type", "Unknown")
                field = estimation.get("field", {}).get("name", "Unknown")
                result += f"Estimation: Type={estimation_type}, Field={field}\n\n"

            # Add filter configuration if available
            if "filter" in response:
                filter_config = response.get("filter", {})
                filter_id = filter_config.get("id", "Unknown")
                filter_name = filter_config.get("name", "Unknown")
                result += f"Filter: ID={filter_id}, Name={filter_name}\n\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving configuration for board {board_id}: {str(e)}"


@tool
def get_board_epics(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    done: bool | None = None,
) -> str:
    """
    Gets all epics from the board, for the given board ID.

    Useful for retrieving epics associated with a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first epic to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of epics to return. Defaults to 50.
        done (bool, optional): Filters results to epics that are either done or not done

    Returns:
        str: Formatted list of epics on the board
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if done is not None:
            params["done"] = str(done).lower()

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/epic", params=params)

            epics = response.get("values", [])
            total = response.get("total", 0)

            if not epics:
                return f"No epics found for board {board_id}"

            result = f"Found {len(epics)} of {total} total epics for board {board_id}:\n\n"

            for epic in epics:
                epic_id = epic.get("id", "Unknown")
                epic_key = epic.get("key", "Unknown")
                epic_name = epic.get("name", "Unknown")
                epic_done = epic.get("done", False)
                status = "Done" if epic_done else "Not Done"

                result += f"- Epic {epic_key} (ID: {epic_id}): {epic_name} ({status})\n"

            if len(epics) < total:
                result += (
                    f"\nShowing {len(epics)} of {total} epics. Use start_at parameter to see more."
                )

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving epics for board {board_id}: {str(e)}"


@tool
def get_issues_without_epic(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues that do not belong to any epic on a board, for the given board ID.

    Useful for finding issues that need to be assigned to an epic.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues
        validate_query (bool, optional): Whether to validate the JQL query. Defaults to True.
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: Formatted list of issues without an epic
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
            params["validateQuery"] = validate_query

        if fields:
            params["fields"] = ",".join(fields)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/epic/none/issue", params=params)

            issues = response.get("issues", [])
            total = response.get("total", 0)

            if not issues:
                return f"No issues without epic found for board {board_id}"

            result = f"Found {len(issues)} of {total} total issues without epic for board {board_id}:\n\n"

            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown type")

                result += f"- {key} [{issue_type}]: {summary} ({status})\n"

            if len(issues) < total:
                result += f"\nShowing {len(issues)} of {total} issues. Use start_at parameter to see more."

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving issues without epic for board {board_id}: {str(e)}"


@tool
def get_epic_issues(
    board_id: int,
    epic_id: str,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues that belong to an epic on a board, for the given epic ID and board ID.

    Useful for retrieving all issues within a specific epic.

    Args:
        board_id (int): The board ID (e.g., 123)
        epic_id (str): The epic ID (e.g., 456) or epic key (e.g., 'PROJECT-123')
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues
        validate_query (bool, optional): Whether to validate the JQL query. Defaults to True.
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: Formatted list of issues in the epic
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
            params["validateQuery"] = validate_query

        if fields:
            params["fields"] = ",".join(fields)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/epic/{epic_id}/issue", params=params)

            issues = response.get("issues", [])
            total = response.get("total", 0)

            if not issues:
                return f"No issues found in epic {epic_id} for board {board_id}"

            result = f"Found {len(issues)} of {total} total issues in epic {epic_id} for board {board_id}:\n\n"

            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown type")

                result += f"- {key} [{issue_type}]: {summary} ({status})\n"

            if len(issues) < total:
                result += f"\nShowing {len(issues)} of {total} issues. Use start_at parameter to see more."

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving issues for epic {epic_id} in board {board_id}: {str(e)}"


@tool
def get_board_features(board_id: int) -> str:
    """
    Gets all features of a board.

    Useful for checking which features are enabled on a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Formatted list of board features and their status
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/features")

            features = response.get("features", [])

            if not features:
                return f"No features found for board {board_id}"

            result = f"Features for board {board_id}:\n\n"

            for feature in features:
                feature_id = feature.get("id", "Unknown")
                feature_name = feature.get("name", "Unknown")
                feature_state = feature.get("state", "Unknown")

                result += f"- Feature: {feature_name} (ID: {feature_id}), State: {feature_state}\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving features for board {board_id}: {str(e)}"


@tool
def toggle_board_feature(
    board_id: int,
    feature_key: str,
    state: str,
) -> str:
    """
    Toggles the state of a feature on a board.

    Useful for enabling or disabling features on a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        feature_key (str): The key of the feature to toggle (e.g., 'estimation')
        state (str): The state to set the feature to (e.g., 'enabled', 'disabled')

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {"state": state}

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            client.put(f"board/{board_id}/features/{feature_key}", data)
            return f"Successfully set feature '{feature_key}' to '{state}' on board {board_id}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error toggling feature '{feature_key}' on board {board_id}: {str(e)}"


@tool
def get_board_issues(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues for a board.

    Useful for retrieving all issues on a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues
        validate_query (bool, optional): Whether to validate the JQL query. Defaults to True.
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: Formatted list of issues on the board
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
            params["validateQuery"] = validate_query

        if fields:
            params["fields"] = ",".join(fields)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/issue", params=params)

            issues = response.get("issues", [])
            total = response.get("total", 0)

            if not issues:
                return f"No issues found for board {board_id}"

            result = f"Found {len(issues)} of {total} total issues for board {board_id}:\n\n"

            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown type")

                result += f"- {key} [{issue_type}]: {summary} ({status})\n"

            if len(issues) < total:
                result += f"\nShowing {len(issues)} of {total} issues. Use start_at parameter to see more."

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving issues for board {board_id}: {str(e)}"


@tool
def move_issues_to_board(
    board_id: int,
    issues: list[str],
    rank_before: str | None = None,
    rank_after: str | None = None,
) -> str:
    """
    Moves issues to a board.

    Useful for adding issues to a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        issues (List[str]): List of issue keys or IDs to move to the board
        rank_before (str, optional): Issue key to place the issues before
        rank_after (str, optional): Issue key to place the issues after

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {"issues": issues}

        if rank_before:
            data["rankBefore"] = rank_before

        if rank_after:
            data["rankAfter"] = rank_after

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            client.post(f"board/{board_id}/issue", data)
            return f"Successfully moved {len(issues)} issues to board {board_id}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error moving issues to board {board_id}: {str(e)}"


@tool
def get_board_projects(board_id: int) -> str:
    """
    Gets all projects that are associated with the board.

    Useful for identifying which projects are connected to a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Formatted list of projects associated with the board
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/project")

            projects = response.get("values", [])

            if not projects:
                return f"No projects found for board {board_id}"

            result = f"Projects associated with board {board_id}:\n\n"

            for project in projects:
                project_id = project.get("id", "Unknown")
                project_key = project.get("key", "Unknown")
                project_name = project.get("name", "Unknown")

                result += f"- Project: {project_name} (Key: {project_key}, ID: {project_id})\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving projects for board {board_id}: {str(e)}"


@tool
def get_board_projects_full(board_id: int) -> str:
    """
    Gets all projects that are associated with the board with all attributes.

    Useful for retrieving detailed information about projects connected to a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Formatted detailed list of projects associated with the board
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/project/full")

            projects = response.get("values", [])

            if not projects:
                return f"No projects found for board {board_id}"

            result = f"Detailed projects associated with board {board_id}:\n\n"

            for project in projects:
                project_id = project.get("id", "Unknown")
                project_key = project.get("key", "Unknown")
                project_name = project.get("name", "Unknown")
                project_type = project.get("projectTypeKey", "Unknown")

                result += (
                    f"- Project: {project_name}\n"
                    f"  Key: {project_key}\n"
                    f"  ID: {project_id}\n"
                    f"  Type: {project_type}\n"
                )

                # Add lead information if available
                if "lead" in project:
                    lead = project.get("lead", {})
                    lead_name = lead.get("displayName", "Unknown")
                    result += f"  Lead: {lead_name}\n"

                result += "\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving detailed projects for board {board_id}: {str(e)}"


@tool
def get_board_property_keys(board_id: int) -> str:
    """
    Gets the keys of all properties stored for a board.

    Useful for discovering what custom properties are available for a board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: List of property keys
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/properties")

            keys = response.get("keys", [])

            if not keys:
                return f"No properties found for board {board_id}"

            result = f"Properties for board {board_id}:\n\n"
            for key_info in keys:
                key = key_info.get("key", "Unknown")
                # self_url = key_info.get("self", "Unknown")
                result += f"- {key}\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving property keys for board {board_id}: {str(e)}"


@tool
def get_board_property(board_id: int, property_key: str) -> str:
    """
    Gets the value of a specific board property.

    Useful for retrieving custom data stored on a board.

    Args:
        board_id (int): The board ID (e.g., 123)
        property_key (str): The key of the property to get

    Returns:
        str: Property value
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/properties/{property_key}")

            key = response.get("key", "Unknown")
            value = response.get("value", "No value")

            return f"Property '{key}' for board {board_id}: {value}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving property '{property_key}' for board {board_id}: {str(e)}"


@tool
def set_board_property(board_id: int, property_key: str, value: Any) -> str:
    """
    Sets the value of a board property.

    Useful for storing custom data on a board.

    Args:
        board_id (int): The board ID (e.g., 123)
        property_key (str): The key of the property to set
        value (Any): The value to set (any JSON-serializable data)

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            client.put(f"board/{board_id}/properties/{property_key}", value)
            return f"Successfully set property '{property_key}' for board {board_id}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error setting property '{property_key}' for board {board_id}: {str(e)}"


@tool
def delete_board_property(board_id: int, property_key: str) -> str:
    """
    Deletes a board property.

    Useful for removing custom data stored on a board.

    Args:
        board_id (int): The board ID (e.g., 123)
        property_key (str): The key of the property to delete

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            client.delete(f"board/{board_id}/properties/{property_key}")
            return f"Successfully deleted property '{property_key}' from board {board_id}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error deleting property '{property_key}' from board {board_id}: {str(e)}"


@tool
def get_all_quickfilters(board_id: int, start_at: int = 0, max_results: int = 50) -> str:
    """
    Gets all quick filters from a board.

    Useful for retrieving quick filters configured for a board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first quick filter to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of quick filters to return. Defaults to 50.

    Returns:
        str: Formatted list of quick filters on the board
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/quickfilter", params=params)

            quick_filters = response.get("values", [])

            if not quick_filters:
                return f"No quick filters found for board {board_id}"

            result = f"Quick filters for board {board_id}:\n\n"

            for filter in quick_filters:
                filter_id = filter.get("id", "Unknown")
                filter_name = filter.get("name", "Unknown")
                filter_query = filter.get("jql", "No JQL")

                result += (
                    f"- Quick Filter: {filter_name} (ID: {filter_id})\n  JQL: {filter_query}\n\n"
                )

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving quick filters for board {board_id}: {str(e)}"


@tool
def get_quickfilter(board_id: int, quickfilter_id: int) -> str:
    """
    Gets a quick filter from a board.

    Useful for retrieving details of a specific quick filter.

    Args:
        board_id (int): The board ID (e.g., 123)
        quickfilter_id (int): The quick filter ID (e.g., 456)

    Returns:
        str: Formatted quick filter details
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/quickfilter/{quickfilter_id}")

            filter_id = response.get("id", "Unknown")
            filter_name = response.get("name", "Unknown")
            filter_query = response.get("jql", "No JQL")
            filter_desc = response.get("description", "No description")

            result = (
                f"Quick Filter: {filter_name} (ID: {filter_id})\n"
                f"Description: {filter_desc}\n"
                f"JQL: {filter_query}\n"
            )

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving quick filter {quickfilter_id} for board {board_id}: {str(e)}"


@tool
def get_board_reports(board_id: int) -> str:
    """
    Gets all reports from a board.

    Useful for retrieving available reports for a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)

    Returns:
        str: Formatted list of reports available for the board
    """
    client = get_jira_client()
    try:
        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/reports")

            reports = response.get("values", [])

            if not reports:
                return f"No reports found for board {board_id}"

            result = f"Reports for board {board_id}:\n\n"

            for report in reports:
                report_key = report.get("key", "Unknown")
                report_name = report.get("name", "Unknown")
                report_desc = report.get("description", "No description")

                result += (
                    f"- Report: {report_name} (Key: {report_key})\n  Description: {report_desc}\n\n"
                )

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving reports for board {board_id}: {str(e)}"


@tool
def get_all_sprints(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    state: list[str] | None = None,
) -> str:
    """
    Gets all sprints from a board.

    Useful for retrieving all sprints associated with a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first sprint to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of sprints to return. Defaults to 50.
        state (List[str], optional): Filters results to sprints in the specified states (e.g., ['active', 'future'])

    Returns:
        str: Formatted list of sprints on the board
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if state:
            params["state"] = ",".join(state)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/sprint", params=params)

            sprints = response.get("values", [])

            if not sprints:
                return f"No sprints found for board {board_id}"

            result = f"Sprints for board {board_id}:\n\n"

            for sprint in sprints:
                sprint_id = sprint.get("id", "Unknown")
                sprint_name = sprint.get("name", "Unknown")
                sprint_state = sprint.get("state", "Unknown")

                result += f"- Sprint: {sprint_name} (ID: {sprint_id}, State: {sprint_state})\n"

                # Add dates if available
                if sprint.get("startDate"):
                    result += f"  Start Date: {sprint.get('startDate')}\n"
                if sprint.get("endDate"):
                    result += f"  End Date: {sprint.get('endDate')}\n"

                result += "\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving sprints for board {board_id}: {str(e)}"


@tool
def get_sprint_issues_for_board(
    board_id: int,
    sprint_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Gets all issues in a sprint for the given board ID and sprint ID.

    Useful for retrieving issues in a specific sprint for a particular board.

    Args:
        board_id (int): The board ID (e.g., 123)
        sprint_id (int): The sprint ID (e.g., 456)
        start_at (int, optional): The index of the first issue to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): JQL filter to apply to the issues
        validate_query (bool, optional): Whether to validate the JQL query. Defaults to True.
        fields (List[str], optional): List of issue fields to include in the response

    Returns:
        str: Formatted list of issues in the sprint
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
            params["validateQuery"] = validate_query

        if fields:
            params["fields"] = ",".join(fields)

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/sprint/{sprint_id}/issue", params=params)

            issues = response.get("issues", [])
            total = response.get("total", 0)

            if not issues:
                return f"No issues found in sprint {sprint_id} for board {board_id}"

            result = f"Found {len(issues)} of {total} total issues in sprint {sprint_id} for board {board_id}:\n\n"

            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown type")

                result += f"- {key} [{issue_type}]: {summary} ({status})\n"

            if len(issues) < total:
                result += f"\nShowing {len(issues)} of {total} issues. Use start_at parameter to see more."

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving issues for sprint {sprint_id} in board {board_id}: {str(e)}"


@tool
def get_board_versions(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    released: bool | None = None,
) -> str:
    """
    Gets all versions from a board.

    Useful for retrieving all versions associated with a specific board.

    Args:
        board_id (int): The board ID (e.g., 123)
        start_at (int, optional): The index of the first version to return (0-based). Defaults to 0.
        max_results (int, optional): The maximum number of versions to return. Defaults to 50.
        released (bool, optional): Filters results to versions that are either released or unreleased

    Returns:
        str: Formatted list of versions on the board
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results}

        if released is not None:
            params["released"] = str(released).lower()

        # The Boards API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            response = client.get(f"board/{board_id}/version", params=params)

            versions = response.get("values", [])

            if not versions:
                return f"No versions found for board {board_id}"

            result = f"Versions for board {board_id}:\n\n"

            for version in versions:
                version_id = version.get("id", "Unknown")
                version_name = version.get("name", "Unknown")
                is_released = version.get("released", False)
                release_status = "Released" if is_released else "Unreleased"

                result += (
                    f"- Version: {version_name} (ID: {version_id}, Status: {release_status})\n"
                )

                # Add dates if available
                if version.get("startDate"):
                    result += f"  Start Date: {version.get('startDate')}\n"
                if version.get("releaseDate"):
                    result += f"  Release Date: {version.get('releaseDate')}\n"

                result += "\n"

            return result
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error retrieving versions for board {board_id}: {str(e)}"


# Export the tools for use in the JIRA assistant
board_tools = [
    get_all_boards,
    create_board,
    get_board_by_filter_id,
    get_board,
    delete_board,
    get_backlog_issues,
    get_board_configuration,
    get_board_epics,
    get_issues_without_epic,
    get_epic_issues,
    get_board_features,
    toggle_board_feature,
    get_board_issues,
    move_issues_to_board,
    get_board_projects,
    get_board_projects_full,
    get_board_property_keys,
    get_board_property,
    set_board_property,
    delete_board_property,
    get_all_quickfilters,
    get_quickfilter,
    get_board_reports,
    get_all_sprints,
    get_sprint_issues_for_board,
    get_board_versions,
]
