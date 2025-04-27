"""
JIRA Issue Search API Functions

This module provides tools for searching JIRA issues through the REST API.
"""

from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import BaseTool, tool

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
def match_issues_with_jql(
    jql_queries: List[str],
    issue_ids: Optional[List[int]] = None,
    issue_keys: Optional[List[str]] = None,
) -> str:
    """
    Checks if issues match one or more JQL queries.

    Useful for validating whether issues match specific criteria without fetching full issue details.

    Args:
        jql_queries (List[str]): A list of JQL queries to match against issues.
        issue_ids (List[int], optional): A list of issue IDs to check.
        issue_keys (List[str], optional): A list of issue keys to check.

    Returns:
        str: Results showing which issues match which queries
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

        matches = response.get("matches", [])
        result = "JQL Match Results:\n\n"

        for i, match in enumerate(matches):
            result += f'Query {i + 1}: "{jql_queries[i]}"\n'

            matched_issues = match.get("matchedIssues", [])
            if matched_issues:
                result += f"  Matched {len(matched_issues)} issues:\n"
                for issue in matched_issues[:10]:  # Limit to first 10 for readability
                    result += f"  - Issue ID: {issue}\n"
                if len(matched_issues) > 10:
                    result += f"  - ... and {len(matched_issues) - 10} more\n"
            else:
                result += "  No issues matched this query.\n"

            errors = match.get("errors", [])
            if errors:
                result += "  Errors:\n"
                for error in errors:
                    result += f"  - {error}\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error matching issues with JQL: {str(e)}"


@tool
def get_issue_picker_suggestions(
    query: str,
    current_project_id: Optional[str] = None,
    current_issue_key: Optional[str] = None,
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
        str: Formatted issue picker suggestions
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

        sections = response.get("sections", [])
        result = "Issue picker suggestions:\n\n"

        for section in sections:
            section_label = section.get("label", "Unnamed section")
            result += f"{section_label}:\n"

            issues = section.get("issues", [])
            if issues:
                for issue in issues:
                    key = issue.get("key", "Unknown")
                    summary = issue.get("summaryText", "No summary")
                    result += f"- {key}: {summary}\n"
            else:
                message = section.get("msg", "No issues found")
                result += f"  {message}\n"

            result += "\n"

        if not sections:
            result += "No suggestions found for the query.\n"

        return result
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
        str: Issue count for the JQL query
    """
    client = get_jira_client()
    try:
        response = client.post("issue/jqlCountForFilter", {"jql": jql})
        issue_count = response.get("issueCount", 0)

        return f"Found {issue_count} issues matching the JQL query:\n{jql}"
    except Exception as e:
        return f"Error counting issues for JQL query: {str(e)}"


@tool
def parse_jql_queries(queries: List[str], validate_only: bool = False) -> str:
    """
    Parses and validates JQL queries and returns the results.

    Useful for checking JQL syntax before using it in a search, especially for complex queries.

    Args:
        queries (List[str]): A list of JQL queries to parse.
        validate_only (bool, optional): If True, only validates without converting. Defaults to False.

    Returns:
        str: Parsed and validated JQL results
    """
    client = get_jira_client()
    try:
        data = {"queries": queries, "validateOnly": validate_only}

        response = client.post("jql/parse", data)

        results = response.get("queries", [])
        result = "JQL Query Parsing Results:\n\n"

        for i, parsed in enumerate(results):
            query = queries[i]
            result += f'Query {i + 1}: "{query}"\n'

            errors = parsed.get("errors", [])
            if errors:
                result += "  Errors:\n"
                for error in errors:
                    result += f"  - {error}\n"
            else:
                result += "  Valid: Yes\n"

            converted_query = parsed.get("convertedQuery", "")
            if converted_query and not validate_only:
                result += f'  Converted Query: "{converted_query}"\n'

            result += "\n"

        return result
    except Exception as e:
        return f"Error parsing JQL queries: {str(e)}"


@tool
def get_advanced_search_fields() -> str:
    """
    Gets a list of fields that can be used in an advanced search.

    Useful for discovering available fields for building JQL queries.

    Returns:
        str: Formatted list of fields for advanced search
    """
    client = get_jira_client()
    try:
        response = client.get("field/search")

        fields = response.get("fields", [])
        result = f"Found {len(fields)} searchable fields:\n\n"

        for field in fields:
            id = field.get("id", "Unknown")
            name = field.get("name", "Unknown")
            clause_names = field.get("clauseNames", [])

            result += f"- {name} (ID: {id})\n"
            if clause_names:
                result += f"  JQL clauses: {', '.join(clause_names)}\n"

            schema = field.get("schema")
            if schema:
                type_name = schema.get("type", "Unknown type")
                result += f"  Type: {type_name}\n"

            result += "\n"

        return result
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
