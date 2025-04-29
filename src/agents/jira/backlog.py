"""
JIRA Backlog API Functions

This module provides tools for interacting with JIRA backlogs through the REST API.
Based on: https://developer.atlassian.com/cloud/jira/software/rest/api-group-backlog/
"""

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_backlog_items(
    board_id: int,
    start_at: int = 0,
    max_results: int = 50,
    jql: str | None = None,
    validate_query: bool = True,
    fields: list[str] | None = None,
) -> str:
    """
    Get issues from a board's backlog.

    Useful for accessing issues that are in the backlog of a specific board.

    Args:
        board_id (int): The ID of the board
        start_at (int, optional): The starting index of the returned issues. Defaults to 0.
        max_results (int, optional): The maximum number of issues to return. Defaults to 50.
        jql (str, optional): Filter the results using a JQL query
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
                return f"No issues found in the backlog for board {board_id}"

            result = f"Found {len(issues)} of {total} total issues in the backlog for board {board_id}:\n\n"

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
def move_issues_to_backlog(issue_keys: list[str]) -> str:
    """
    Move issues to the backlog.

    Useful for moving issues from a sprint back to the backlog.
    This operation is only available for Scrum boards.

    Args:
        issue_keys (List[str]): A list of issue keys to move to the backlog

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        # The Agile API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            data = {"issues": issue_keys}
            client.post("backlog/issue", data)

            keys_str = ", ".join(issue_keys)
            return f"Successfully moved issues to backlog: {keys_str}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error moving issues to backlog: {str(e)}"


@tool
def rank_backlog_issues(
    issues: list[str], rankBefore: str | None = None, rankAfter: str | None = None
) -> str:
    """
    Rank (prioritize) issues in the backlog.

    Useful for ordering backlog items by rank. Either rankBefore or rankAfter can be provided
    to position the issues relative to another issue.

    Args:
        issues (List[str]): A list of issue keys to rank
        rankBefore (str, optional): Issue key that the issues should be ranked before
        rankAfter (str, optional): Issue key that the issues should be ranked after

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        # Validate that only one of rankBefore or rankAfter is provided
        if rankBefore and rankAfter:
            return "Error: Only one of rankBefore or rankAfter should be provided, not both"

        if not (rankBefore or rankAfter):
            return "Error: Either rankBefore or rankAfter must be provided"

        # The Agile API uses a different base path
        original_api_base_path = client.api_base_path
        client.api_base_path = "rest/agile/1.0/"

        try:
            data = {"issues": issues}

            if rankBefore:
                data["rankBefore"] = rankBefore
            else:
                data["rankAfter"] = rankAfter

            client.put("backlog/issue", data)

            issues_str = ", ".join(issues)
            return f"Successfully ranked issues in backlog: {issues_str}"
        finally:
            # Restore the original API base path
            client.api_base_path = original_api_base_path

    except Exception as e:
        return f"Error ranking issues in backlog: {str(e)}"


# Export the tools for use in the JIRA assistant
backlog_tools = [
    get_backlog_items,
    move_issues_to_backlog,
    rank_backlog_issues,
]
