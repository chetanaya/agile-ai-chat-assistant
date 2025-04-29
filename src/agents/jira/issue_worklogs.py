"""
JIRA Issue Worklogs API Functions

This module provides tools for interacting with JIRA issue worklogs through the REST API.
"""

from datetime import datetime
from typing import Any

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_issue_worklogs(issue_key: str, start_at: int = 0, max_results: int = 50) -> str:
    """
    Returns worklogs for an issue (ordered by created time), starting from the oldest worklog
    or from the worklog started on or after a date and time.

    Useful for viewing time tracking for a specific issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        start_at (int, optional): The index of the first item to return. Defaults to 0.
        max_results (int, optional): The maximum number of items to return. Defaults to 50.

    Returns:
        str: JSON string with issue worklogs
    """
    client = get_jira_client()
    try:
        response = client.get(
            f"issue/{issue_key}/worklog", params={"startAt": start_at, "maxResults": max_results}
        )

        worklogs = response.get("worklogs", [])
        total = response.get("total", 0)

        result = f"Worklogs for issue {issue_key} (showing {len(worklogs)} of {total}):\n\n"

        for worklog in worklogs:
            author = worklog.get("author", {}).get("displayName", "Unknown")
            time_spent = worklog.get("timeSpent", "Unknown")
            started = worklog.get("started", "Unknown")
            comment = worklog.get("comment", "No comment")

            # Format the comment if it's in Atlassian Document Format
            if isinstance(comment, dict) and "content" in comment:
                # Simple extraction of text from ADF
                comment_text = ""
                for content in comment.get("content", []):
                    if content.get("type") == "paragraph":
                        for text_content in content.get("content", []):
                            if text_content.get("type") == "text":
                                comment_text += text_content.get("text", "")
                comment = comment_text or "No comment"

            result += f"- Author: {author}\n"
            result += f"  Time spent: {time_spent}\n"
            result += f"  Started: {started}\n"
            result += f"  Comment: {comment}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving worklogs for issue {issue_key}: {str(e)}"


@tool
def add_worklog(
    issue_key: str,
    time_spent: str,
    comment: str | None = None,
    started: str | None = None,
    visibility: dict[str, str] | None = None,
) -> str:
    """
    Adds a worklog to an issue.

    Useful for logging time spent working on an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        time_spent (str): The time spent working on the issue in jira format (e.g., "3h 30m")
        comment (str, optional): A comment about the work performed
        started (str, optional): The datetime when the work began in ISO format (e.g., "2023-04-21T12:00:00.000+0000")
        visibility (Dict[str, str], optional): The visibility of the worklog (e.g., {"type": "group", "value": "jira-developers"})

    Returns:
        str: Success message with worklog details or error message
    """
    client = get_jira_client()
    try:
        data: dict[str, Any] = {"timeSpent": time_spent}

        # Add comment if provided
        if comment:
            # Format comment as Atlassian Document Format
            data["comment"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }

        # Add started time if provided
        if started:
            data["started"] = started

        # Add visibility restrictions if provided
        if visibility:
            data["visibility"] = visibility

        response = client.post(f"issue/{issue_key}/worklog", data)

        author = response.get("author", {}).get("displayName", "Unknown")
        time_spent_response = response.get("timeSpent", "Unknown")
        worklog_id = response.get("id", "Unknown")

        return f"Worklog added to issue {issue_key} successfully. ID: {worklog_id}, Author: {author}, Time spent: {time_spent_response}"
    except Exception as e:
        return f"Error adding worklog to issue {issue_key}: {str(e)}"


@tool
def get_worklog(issue_key: str, worklog_id: str) -> str:
    """
    Returns a specific worklog for an issue.

    Useful for viewing details of a specific time tracking entry.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        worklog_id (str): The ID of the worklog to retrieve

    Returns:
        str: JSON string with worklog details
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/{issue_key}/worklog/{worklog_id}")

        author = response.get("author", {}).get("displayName", "Unknown")
        time_spent = response.get("timeSpent", "Unknown")
        started = response.get("started", "Unknown")
        comment = response.get("comment", "No comment")
        created = response.get("created", "Unknown")
        updated = response.get("updated", "Unknown")

        # Format the comment if it's in Atlassian Document Format
        if isinstance(comment, dict) and "content" in comment:
            # Simple extraction of text from ADF
            comment_text = ""
            for content in comment.get("content", []):
                if content.get("type") == "paragraph":
                    for text_content in content.get("content", []):
                        if text_content.get("type") == "text":
                            comment_text += text_content.get("text", "")
            comment = comment_text or "No comment"

        result = f"Worklog {worklog_id} for issue {issue_key}:\n\n"
        result += f"Author: {author}\n"
        result += f"Time spent: {time_spent}\n"
        result += f"Started: {started}\n"
        result += f"Created: {created}\n"
        result += f"Updated: {updated}\n"
        result += f"Comment: {comment}\n"

        return result
    except Exception as e:
        return f"Error retrieving worklog {worklog_id} for issue {issue_key}: {str(e)}"


@tool
def update_worklog(
    issue_key: str,
    worklog_id: str,
    time_spent: str | None = None,
    comment: str | None = None,
    started: str | None = None,
    visibility: dict[str, str] | None = None,
) -> str:
    """
    Updates a worklog entry for an issue.

    Useful for correcting time spent or details about work performed on an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        worklog_id (str): The ID of the worklog to update
        time_spent (str, optional): The updated time spent working on the issue (e.g., "3h 30m")
        comment (str, optional): An updated comment about the work performed
        started (str, optional): The updated datetime when the work began in ISO format
        visibility (Dict[str, str], optional): Updated visibility of the worklog

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        data: dict[str, Any] = {}

        # Add time spent if provided
        if time_spent:
            data["timeSpent"] = time_spent

        # Add comment if provided
        if comment:
            # Format comment as Atlassian Document Format
            data["comment"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }

        # Add started time if provided
        if started:
            data["started"] = started

        # Add visibility restrictions if provided
        if visibility:
            data["visibility"] = visibility

        # Don't send an empty update
        if not data:
            return "No updates specified"

        response = client.put(f"issue/{issue_key}/worklog/{worklog_id}", data)

        author = response.get("author", {}).get("displayName", "Unknown")
        time_spent_response = response.get("timeSpent", "Unknown")

        return f"Worklog {worklog_id} updated successfully for issue {issue_key}. Author: {author}, Time spent: {time_spent_response}"
    except Exception as e:
        return f"Error updating worklog {worklog_id} for issue {issue_key}: {str(e)}"


@tool
def delete_worklog(issue_key: str, worklog_id: str) -> str:
    """
    Deletes a worklog entry from an issue.

    Useful for removing incorrect or unnecessary time tracking entries.
    Warning: This action cannot be undone.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        worklog_id (str): The ID of the worklog to delete

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        client.delete(f"issue/{issue_key}/worklog/{worklog_id}")
        return f"Worklog {worklog_id} deleted successfully from issue {issue_key}"
    except Exception as e:
        return f"Error deleting worklog {worklog_id} from issue {issue_key}: {str(e)}"


@tool
def get_worklogs_by_ids(worklog_ids: list[str]) -> str:
    """
    Returns worklog details for a list of worklog IDs.

    Useful for batch retrieval of worklog information when you know the IDs.
    The returned list of worklogs is limited to 1000 items.

    Args:
        worklog_ids (List[str]): A list of worklog IDs to retrieve

    Returns:
        str: Formatted worklog details or error message
    """
    client = get_jira_client()
    try:
        data = {"ids": worklog_ids}
        response = client.post("worklog/list", data)

        worklogs = response
        result = f"Retrieved {len(worklogs)} worklogs:\n\n"

        for worklog in worklogs:
            worklog_id = worklog.get("id", "Unknown")
            issue_id = worklog.get("issueId", "Unknown")
            author = worklog.get("author", {}).get("displayName", "Unknown")
            time_spent = worklog.get("timeSpent", "Unknown")
            started = worklog.get("started", "Unknown")

            result += f"- Worklog ID: {worklog_id} (Issue ID: {issue_id})\n"
            result += f"  Author: {author}\n"
            result += f"  Time spent: {time_spent}\n"
            result += f"  Started: {started}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving worklogs by IDs: {str(e)}"


@tool
def get_deleted_worklog_ids(since: int | None = None) -> str:
    """
    Returns IDs of worklogs deleted since a specific timestamp.

    Useful for synchronizing worklog data with external systems by tracking deletions.

    Args:
        since (int, optional): A timestamp in milliseconds used to filter by last update time.
                               If not provided, all deleted worklogs will be returned up to the server's limit.

    Returns:
        str: List of deleted worklog IDs with timestamps or error message
    """
    client = get_jira_client()
    try:
        params = {}
        if since is not None:
            params["since"] = since

        response = client.get("worklog/deleted", params=params)

        values = response.get("values", [])
        until = response.get("until", 0)
        since_response = response.get("since", 0)

        result = f"Deleted worklog IDs since {since_response} until {until}:\n\n"

        for value in values:
            worklog_id = value.get("worklogId", "Unknown")
            deleted_timestamp = value.get("deletedTimestamp", 0)

            # Convert timestamp to readable date
            if deleted_timestamp:
                date_str = datetime.fromtimestamp(deleted_timestamp / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                result += f"- Worklog ID: {worklog_id}, Deleted at: {date_str}\n"
            else:
                result += f"- Worklog ID: {worklog_id}, Deleted timestamp unknown\n"

        return result
    except Exception as e:
        return f"Error retrieving deleted worklog IDs: {str(e)}"


@tool
def get_updated_worklog_ids(since: int | None = None) -> str:
    """
    Returns IDs of worklogs updated since a specific timestamp.

    Useful for synchronizing worklog data with external systems by tracking updates.

    Args:
        since (int, optional): A timestamp in milliseconds used to filter by last update time.
                               If not provided, all updated worklogs will be returned up to the server's limit.

    Returns:
        str: List of updated worklog IDs with timestamps or error message
    """
    client = get_jira_client()
    try:
        params = {}
        if since is not None:
            params["since"] = since

        response = client.get("worklog/updated", params=params)

        values = response.get("values", [])
        until = response.get("until", 0)
        since_response = response.get("since", 0)

        result = f"Updated worklog IDs since {since_response} until {until}:\n\n"

        for value in values:
            worklog_id = value.get("worklogId", "Unknown")
            updated_timestamp = value.get("updatedTimestamp", 0)

            # Convert timestamp to readable date
            if updated_timestamp:
                date_str = datetime.fromtimestamp(updated_timestamp / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                result += f"- Worklog ID: {worklog_id}, Updated at: {date_str}\n"
            else:
                result += f"- Worklog ID: {worklog_id}, Updated timestamp unknown\n"

        return result
    except Exception as e:
        return f"Error retrieving updated worklog IDs: {str(e)}"


@tool
def bulk_delete_worklogs(worklog_ids: list[str]) -> str:
    """
    Deletes multiple worklogs in a single operation.

    Useful for batch removal of worklogs when a large number need to be deleted.
    Warning: This action cannot be undone.

    Args:
        worklog_ids (List[str]): List of worklog IDs to delete

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        data = {"ids": worklog_ids}
        client.delete("worklog/delete", json=data)

        return f"Successfully deleted {len(worklog_ids)} worklogs"
    except Exception as e:
        return f"Error bulk deleting worklogs: {str(e)}"


@tool
def bulk_move_worklogs(
    source_issue_key: str, destination_issue_key: str, worklog_ids: list[str]
) -> str:
    """
    Moves worklogs from one issue to another.

    Useful for reassigning time tracking entries when work was logged against the wrong issue.
    This is an experimental Jira API endpoint.

    Args:
        source_issue_key (str): The issue key to move worklogs from (e.g., "PROJECT-123")
        destination_issue_key (str): The issue key to move worklogs to (e.g., "PROJECT-456")
        worklog_ids (List[str]): List of worklog IDs to move

    Returns:
        str: Success message or error message
    """
    client = get_jira_client()
    try:
        data = {"destinationIssueId": destination_issue_key, "worklogIds": worklog_ids}

        client.post(f"issue/{source_issue_key}/worklog/move", data)

        moved_count = len(worklog_ids)
        return f"Successfully moved {moved_count} worklogs from issue {source_issue_key} to {destination_issue_key}"
    except Exception as e:
        return f"Error moving worklogs: {str(e)}"


# Export the tools for use in the JIRA assistant
worklog_tools = [
    get_issue_worklogs,
    add_worklog,
    get_worklog,
    update_worklog,
    delete_worklog,
    get_worklogs_by_ids,
    get_deleted_worklog_ids,
    get_updated_worklog_ids,
    bulk_delete_worklogs,
    bulk_move_worklogs,
]
