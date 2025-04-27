"""
JIRA Issues API Functions

This module provides tools for interacting with JIRA issues through the REST API.
"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool, tool

from agents.jira.utils import get_jira_client


@tool
def get_issue(issue_key: str) -> str:
    """
    Retrieves details of a specific JIRA issue by its key.

    Useful for getting information about a particular issue such as summary, description,
    status, assignee, and other fields.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")

    Returns:
        str: JSON string with issue details
    """
    client = get_jira_client()
    try:
        # Include fields parameter to control which fields to return
        response = client.get(
            f"issue/{issue_key}",
            params={
                "fields": "summary,description,status,assignee,priority,issuetype,created,updated"
            },
        )
        return f"Issue details for {issue_key}:\n{response}"
    except Exception as e:
        return f"Error retrieving issue {issue_key}: {str(e)}"


@tool
def create_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> str:
    """
    Creates a new JIRA issue.

    Useful for creating a new issue in a project with the specified details.

    Args:
        project_key (str): The project key (e.g., "PROJECT")
        summary (str): Issue summary/title
        description (str): Issue description
        issue_type (str, optional): Issue type (e.g., "Task", "Bug", "Story"). Defaults to "Task".

    Returns:
        str: JSON string with created issue details
    """
    client = get_jira_client()
    try:
        # Format description as Atlassian Document Format
        description_adf = {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
        }

        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description_adf,
                "issuetype": {"name": issue_type},
            }
        }

        response = client.post("issue", data)
        return f"Issue created successfully: {response.get('key', 'Unknown')}"
    except Exception as e:
        return f"Error creating issue: {str(e)}"


@tool
def update_issue(
    issue_key: str, summary: Optional[str] = None, description: Optional[str] = None
) -> str:
    """
    Updates an existing JIRA issue.

    Useful for modifying issue details like summary or description.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        summary (str, optional): New issue summary/title
        description (str, optional): New issue description

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        fields: Dict[str, Any] = {}

        if summary:
            fields["summary"] = summary

        if description:
            # Format description as Atlassian Document Format
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            }

        if not fields:
            return "No fields specified for update"

        data = {"fields": fields}

        response = client.put(f"issue/{issue_key}", data)
        return f"Issue {issue_key} updated successfully"
    except Exception as e:
        return f"Error updating issue {issue_key}: {str(e)}"


@tool
def delete_issue(issue_key: str) -> str:
    """
    Deletes a JIRA issue.

    Useful for removing issues that are no longer needed.
    Warning: This action cannot be undone.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        response = client.delete(f"issue/{issue_key}")
        return f"Issue {issue_key} deleted successfully"
    except Exception as e:
        return f"Error deleting issue {issue_key}: {str(e)}"


@tool
def assign_issue(issue_key: str, account_id: str) -> str:
    """
    Assigns a JIRA issue to a specific user.

    Useful for assigning issues to team members.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        account_id (str): The account ID of the assignee

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {"accountId": account_id}

        response = client.put(f"issue/{issue_key}/assignee", data)
        return f"Issue {issue_key} assigned successfully to account ID: {account_id}"
    except Exception as e:
        return f"Error assigning issue {issue_key}: {str(e)}"


@tool
def search_issues(jql: str, max_results: int = 10) -> str:
    """
    Searches for JIRA issues using JQL (JIRA Query Language).

    Useful for finding issues that match specific criteria.

    Args:
        jql (str): JQL query string (e.g., "project = PROJ AND status = 'In Progress'")
        max_results (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        str: JSON string with search results
    """
    client = get_jira_client()
    try:
        data = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["key", "summary", "status", "assignee", "priority", "issuetype"],
        }

        response = client.post("search", data)

        issues = response.get("issues", [])
        total = response.get("total", 0)

        result = f"Found {total} issues. Showing {len(issues)} results:\n\n"

        for issue in issues:
            key = issue.get("key", "Unknown")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "No summary")
            status_name = fields.get("status", {}).get("name", "Unknown status")

            result += f"- {key}: {summary} ({status_name})\n"

        return result
    except Exception as e:
        return f"Error searching issues: {str(e)}"


@tool
def get_issue_transitions(issue_key: str) -> str:
    """
    Gets available transitions for a JIRA issue.

    Useful for determining what status changes are possible for an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")

    Returns:
        str: JSON string with available transitions
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/{issue_key}/transitions")
        transitions = response.get("transitions", [])

        result = f"Available transitions for issue {issue_key}:\n\n"

        for transition in transitions:
            transition_id = transition.get("id", "Unknown")
            name = transition.get("name", "Unknown")

            result += f"- {name} (ID: {transition_id})\n"

        return result
    except Exception as e:
        return f"Error getting transitions for issue {issue_key}: {str(e)}"


@tool
def transition_issue(issue_key: str, transition_id: str, comment: Optional[str] = None) -> str:
    """
    Transitions a JIRA issue to a new status.

    Useful for changing the status of an issue (e.g., from "To Do" to "In Progress").

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        transition_id (str): The ID of the transition to perform
        comment (str, optional): Comment to add with the transition

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data: Dict[str, Any] = {"transition": {"id": transition_id}}

        if comment:
            data["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": comment}],
                                    }
                                ],
                            }
                        }
                    }
                ]
            }

        response = client.post(f"issue/{issue_key}/transitions", data)
        return f"Issue {issue_key} transitioned successfully"
    except Exception as e:
        return f"Error transitioning issue {issue_key}: {str(e)}"


@tool
def add_comment(issue_key: str, comment: str) -> str:
    """
    Adds a comment to a JIRA issue.

    Useful for adding notes or additional information to an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        comment (str): Comment text

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }
        }

        response = client.post(f"issue/{issue_key}/comment", data)
        return f"Comment added to issue {issue_key} successfully"
    except Exception as e:
        return f"Error adding comment to issue {issue_key}: {str(e)}"


# Export the tools for use in the JIRA assistant
issue_tools = [
    get_issue,
    create_issue,
    update_issue,
    delete_issue,
    assign_issue,
    search_issues,
    get_issue_transitions,
    transition_issue,
    add_comment,
]
