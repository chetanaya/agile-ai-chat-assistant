"""
JIRA Issue Search API Functions

This module provides tools for searching JIRA issues through the REST API.
"""

import json

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


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
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error searching issues: {str(e)}"


@tool
def match_issues_with_jql(
    jql_queries: list[str],
    issue_ids: list[int] | None = None,
    issue_keys: list[str] | None = None,
) -> str:
    """
    Checks if issues match one or more JQL queries.

    Useful for validating whether issues match specific criteria without fetching full issue details.

    Args:
        jql_queries (List[str]): A list of JQL queries to match against issues.
        issue_ids (List[int], optional): A list of issue IDs to check.
        issue_keys (List[str], optional): A list of issue keys to check.

    Returns:
        str: JSON string with match results
    """
    client = get_jira_client()
    try:
        if not issue_ids and not issue_keys:
            return "Error: Either issue_ids or issue_keys must be provided."

        data = {
            "jqls": jql_queries,
        }

        if issue_ids:
            data["issueIds"] = issue_ids

        if issue_keys:
            data["issueKeys"] = issue_keys

        response = client.post("jql/match", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error matching issues with JQL: {str(e)}"


@tool
def get_issue_picker_suggestions(
    query: str,
    current_project_id: str | None = None,
    current_issue_key: str | None = None,
    show_sub_tasks: bool = True,
    show_sub_task_parent: bool = False,
) -> str:
    """
    Returns issue picker suggestions like the Jira UI issue picker.

    Useful for finding issues with a simple text search rather than complex JQL.

    Args:
        query (str): Text to query for suggested issues (summary, description, etc.)
        current_project_id (str, optional): ID of the current project context.
        current_issue_key (str, optional): Key of the current issue context.
        show_sub_tasks (bool, optional): Whether to include subtasks in suggestions. Defaults to True.
        show_sub_task_parent (bool, optional): Whether to include parent issue of subtasks. Defaults to False.

    Returns:
        str: JSON string with issue picker suggestions
    """
    client = get_jira_client()
    try:
        params = {
            "query": query,
            "showSubTasks": str(show_sub_tasks).lower(),
            "showSubTaskParent": str(show_sub_task_parent).lower(),
        }

        if current_project_id:
            params["currentProjectId"] = current_project_id

        if current_issue_key:
            params["currentIssueKey"] = current_issue_key

        response = client.get("issue/picker", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error getting issue picker suggestions: {str(e)}"


@tool
def count_issues_by_jql(jql: str) -> str:
    """
    Counts issues that match a JQL query without retrieving the issues.

    Useful for getting a count of issues matching criteria when you don't need the issue details.

    Args:
        jql (str): JQL query string (e.g., "project = PROJ AND status = 'In Progress'")

    Returns:
        str: JSON string with issue count data
    """
    client = get_jira_client()
    try:
        response = client.post("issue/jqlCountForFilter", {"jql": jql})
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error counting issues for JQL query: {str(e)}"


@tool
def parse_jql_queries(queries: list[str], validate_only: bool = False) -> str:
    """
    Parses and validates JQL queries and returns the results.

    Useful for checking JQL syntax before using it in a search, especially for complex queries.

    Args:
        queries (List[str]): A list of JQL queries to parse.
        validate_only (bool, optional): If True, only validates without converting. Defaults to False.

    Returns:
        str: JSON string with parsing results
    """
    client = get_jira_client()
    try:
        data = {"queries": queries, "validateOnly": validate_only}
        response = client.post("jql/parse", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error parsing JQL queries: {str(e)}"


@tool
def get_advanced_search_fields() -> str:
    """
    Gets a list of fields that can be used in an advanced search.

    Useful for discovering available fields for building JQL queries.

    Returns:
        str: JSON string with searchable fields data
    """
    client = get_jira_client()
    try:
        response = client.get("field/search")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error getting advanced search fields: {str(e)}"


# Export the tools for use in the JIRA assistant
search_tools = [
    search_issues,
    match_issues_with_jql,
    get_issue_picker_suggestions,
    count_issues_by_jql,
    parse_jql_queries,
    get_advanced_search_fields,
]
