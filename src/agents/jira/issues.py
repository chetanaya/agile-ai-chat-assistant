"""
JIRA Issues API Functions

This module provides tools for interacting with JIRA issues through the REST API.
"""

from typing import Any

from langchain_core.tools import tool

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
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    fields: dict[str, Any] | None = None,
    update: dict[str, list[dict[str, Any]]] | None = None,
    properties: list[dict[str, Any]] | None = None,
    history_metadata: dict[str, Any] | None = None,
) -> str:
    """
    Updates an existing JIRA issue with advanced options.

    Useful for modifying issue details including fields, labels, components and custom fields.
    The edits to the issue's fields are defined using update and fields parameters.

    Note that textarea type fields (description, etc.) use Atlassian Document Format content.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        summary (str, optional): New issue summary/title (shorthand for fields["summary"])
        description (str, optional): New issue description (shorthand for fields["description"])
        fields (Dict[str, Any], optional): Fields to set directly (e.g., custom fields)
        update (Dict[str, List[Dict[str, Any]]], optional): Field updates with operations like add, remove, set
        properties (List[Dict[str, Any]], optional): Issue properties to set
        history_metadata (Dict[str, Any], optional): Metadata for the change in issue history

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data: dict[str, Any] = {}

        # Handle fields parameter
        if fields is None:
            fields = {}

        # Add summary and description to fields if provided
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

        # Only add fields to data if not empty
        if fields:
            data["fields"] = fields

        # Add update operations if provided
        if update:
            data["update"] = update

        # Add properties if provided
        if properties:
            data["properties"] = properties

        # Add history metadata if provided
        if history_metadata:
            data["historyMetadata"] = history_metadata

        # Don't send an empty update
        if not data:
            return "No updates specified"

        client.put(f"issue/{issue_key}", data)
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
        client.delete(f"issue/{issue_key}")
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

        client.put(f"issue/{issue_key}/assignee", data)
        return f"Issue {issue_key} assigned successfully to account ID: {account_id}"
    except Exception as e:
        return f"Error assigning issue {issue_key}: {str(e)}"


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
def transition_issue(issue_key: str, transition_id: str, comment: str | None = None) -> str:
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
        data: dict[str, Any] = {"transition": {"id": transition_id}}

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

        client.post(f"issue/{issue_key}/transitions", data)
        return f"Issue {issue_key} transitioned successfully"
    except Exception as e:
        return f"Error transitioning issue {issue_key}: {str(e)}"


@tool
def archive_issues_by_keys(issue_keys: list[str]) -> str:
    """
    Archives issues by their keys or IDs.

    Useful for archiving multiple issues that are no longer needed but should be preserved.
    This operation requires the Jira admin or site admin global permission.
    This is an experimental Jira API endpoint.

    Args:
        issue_keys (List[str]): A list of issue keys or IDs to archive

    Returns:
        str: Success or error message with details of archived issues
    """
    client = get_jira_client()
    try:
        data = {"issueKeys": issue_keys}
        response = client.put("issue/archive", data)

        errors = response.get("errors", [])
        if errors:
            return f"Some issues could not be archived: {errors}"

        return f"Successfully archived {len(issue_keys)} issues"
    except Exception as e:
        return f"Error archiving issues: {str(e)}"


@tool
def archive_issues_by_jql(jql: str) -> str:
    """
    Archives issues that match a JQL query.

    Useful for archiving multiple issues that match specific criteria.
    This operation requires the Jira admin or site admin global permission.
    This is an experimental Jira API endpoint.

    Args:
        jql (str): JQL query string to select issues for archiving

    Returns:
        str: Success or error message with details of archived issues
    """
    client = get_jira_client()
    try:
        data = {"jql": jql}
        response = client.post("issue/archive", data)

        archived_issue_count = response.get("archivedIssuesCount", 0)
        errors = response.get("errors", [])

        if errors:
            return f"Some issues could not be archived: {errors}"

        return f"Successfully archived {archived_issue_count} issues"
    except Exception as e:
        return f"Error archiving issues: {str(e)}"


@tool
def unarchive_issues(issue_keys: list[str]) -> str:
    """
    Unarchives issues by their keys or IDs.

    Useful for restoring archived issues back to active state.
    This operation requires the Jira admin or site admin global permission.
    This is an experimental Jira API endpoint.

    Args:
        issue_keys (List[str]): A list of issue keys or IDs to unarchive

    Returns:
        str: Success or error message with details of unarchived issues
    """
    client = get_jira_client()
    try:
        data = {"issueKeys": issue_keys}
        response = client.put("issue/unarchive", data)

        errors = response.get("errors", [])
        if errors:
            return f"Some issues could not be unarchived: {errors}"

        return f"Successfully unarchived {len(issue_keys)} issues"
    except Exception as e:
        return f"Error unarchiving issues: {str(e)}"


@tool
def export_archived_issues() -> str:
    """
    Exports archived issue data.

    Useful for exporting system field data from archived issues for auditing or reporting purposes.
    This operation requires the Jira admin or site admin global permission.
    This is an experimental Jira API endpoint.

    Returns:
        str: Success message with export details or error message
    """
    client = get_jira_client()
    try:
        response = client.put("issues/archive/export")

        task_id = response.get("taskId")
        if task_id:
            return f"Export started successfully. Task ID: {task_id}"

        return "Export request submitted, but no task ID was returned"
    except Exception as e:
        return f"Error exporting archived issues: {str(e)}"


@tool
def bulk_create_issues(issues_data: list[dict[str, Any]]) -> str:
    """
    Creates multiple issues in bulk.

    Useful for creating many issues at once, which is more efficient than creating them one by one.

    Args:
        issues_data (List[Dict[str, Any]]): List of issue data dictionaries. Each dictionary must contain
                                          project key, summary, description, and issue type.

    Returns:
        str: Success or error message with details of created issues
    """
    client = get_jira_client()
    try:
        formatted_issues = []

        for issue in issues_data:
            # Format description as Atlassian Document Format
            description_adf = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": issue.get("description", "")}],
                    }
                ],
            }

            formatted_issue = {
                "fields": {
                    "project": {"key": issue.get("project_key")},
                    "summary": issue.get("summary"),
                    "description": description_adf,
                    "issuetype": {"name": issue.get("issue_type", "Task")},
                }
            }
            formatted_issues.append(formatted_issue)

        data = {"issueUpdates": formatted_issues}
        response = client.post("issue/bulk", data)

        issues = response.get("issues", [])
        errors = response.get("errors", [])

        result = f"Created {len(issues)} issues successfully.\n"

        if issues:
            result += "Created issues:\n"
            for issue in issues:
                result += f"- {issue.get('key', 'Unknown')}\n"

        if errors:
            result += "\nErrors encountered:\n"
            for error in errors:
                result += f"- {error}\n"

        return result
    except Exception as e:
        return f"Error bulk creating issues: {str(e)}"


@tool
def bulk_fetch_issues(issue_keys: list[str]) -> str:
    """
    Fetches multiple issues in a single request.

    Useful for retrieving details of up to 100 issues at once.

    Args:
        issue_keys (List[str]): A list of issue keys to fetch

    Returns:
        str: Formatted details of the fetched issues or error message
    """
    client = get_jira_client()
    try:
        data = {
            "issueKeys": issue_keys,
            "fields": ["summary", "status", "assignee", "priority", "issuetype"],
        }

        response = client.post("issue/bulkfetch", data)

        issues = response.get("issues", [])
        errors = response.get("errors", [])

        result = f"Retrieved {len(issues)} issues.\n\n"

        if issues:
            for issue in issues:
                key = issue.get("key", "Unknown")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown status")

                result += f"Issue {key}: {summary} ({status})\n"

        if errors:
            result += "\nErrors encountered:\n"
            for error in errors:
                result += f"- {error}\n"

        return result
    except Exception as e:
        return f"Error fetching issues in bulk: {str(e)}"


@tool
def get_create_issue_metadata(
    project_keys: list[str] | None = None,
    issue_type_names: list[str] | None = None,
    expand: str | None = None,
) -> str:
    """
    Retrieves metadata for creating issues.

    Useful for getting information about what fields are required when creating issues in specific projects.
    This is a deprecated endpoint but still commonly used.

    Args:
        project_keys (List[str], optional): A list of project keys to get metadata for
        issue_type_names (List[str], optional): A list of issue type names to get metadata for
        expand (str, optional): Additional properties to expand in the response

    Returns:
        str: Formatted create metadata information or error message
    """
    client = get_jira_client()
    try:
        params = {}

        if project_keys:
            params["projectKeys"] = ",".join(project_keys)

        if issue_type_names:
            params["issuetypeNames"] = ",".join(issue_type_names)

        if expand:
            params["expand"] = expand

        response = client.get("issue/createmeta", params=params)

        projects = response.get("projects", [])
        result = "Create issue metadata:\n\n"

        for project in projects:
            project_key = project.get("key", "Unknown")
            project_name = project.get("name", "Unknown")
            result += f"Project: {project_name} ({project_key})\n"

            issue_types = project.get("issuetypes", [])
            for issue_type in issue_types:
                issue_type_name = issue_type.get("name", "Unknown")
                result += f"  Issue Type: {issue_type_name}\n"

                fields = issue_type.get("fields", {})
                for field_id, field_info in fields.items():
                    field_name = field_info.get("name", field_id)
                    required = field_info.get("required", False)
                    req_str = " (required)" if required else ""
                    result += f"    Field: {field_name}{req_str}\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving create issue metadata: {str(e)}"


@tool
def get_create_metadata_issue_types(project_key: str) -> str:
    """
    Gets issue type metadata for a project.

    Useful for getting information about available issue types for a specific project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")

    Returns:
        str: Formatted information about available issue types or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/createmeta/{project_key}/issuetypes")

        issue_types = response.get("values", [])
        result = f"Issue types for project {project_key}:\n\n"

        for issue_type in issue_types:
            name = issue_type.get("name", "Unknown")
            issue_type_id = issue_type.get("id", "Unknown")
            description = issue_type.get("description", "No description")

            result += f"- {name} (ID: {issue_type_id})\n"
            result += f"  Description: {description}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving issue types for project {project_key}: {str(e)}"


@tool
def get_create_field_metadata(project_key: str, issue_type_id: str) -> str:
    """
    Gets field metadata for a project and issue type.

    Useful for getting information about available fields when creating an issue of a specific type in a project.

    Args:
        project_key (str): The project key (e.g., "PROJECT")
        issue_type_id (str): The issue type ID

    Returns:
        str: Formatted information about available fields or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/createmeta/{project_key}/issuetypes/{issue_type_id}")

        fields = response.get("values", [])
        result = f"Fields for project {project_key} and issue type ID {issue_type_id}:\n\n"

        for field in fields:
            name = field.get("name", "Unknown")
            field_id = field.get("fieldId", "Unknown")
            required = field.get("required", False)
            req_str = " (required)" if required else ""

            result += f"- {name} (ID: {field_id}){req_str}\n"

            allowed_values = field.get("allowedValues", [])
            if allowed_values:
                result += "  Allowed values:\n"
                for value in allowed_values[
                    :5
                ]:  # Limit to first 5 values to avoid very long outputs
                    value_name = value.get("name", "Unknown")
                    result += f"    - {value_name}\n"
                if len(allowed_values) > 5:
                    result += f"    - ... and {len(allowed_values) - 5} more\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving field metadata for project {project_key} and issue type {issue_type_id}: {str(e)}"


@tool
def get_edit_issue_metadata(issue_key: str) -> str:
    """
    Gets metadata for editing an issue.

    Useful for getting information about what fields can be edited for a specific issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")

    Returns:
        str: Formatted information about editable fields or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/{issue_key}/editmeta")

        fields = response.get("fields", {})
        result = f"Edit metadata for issue {issue_key}:\n\n"

        for field_id, field_info in fields.items():
            name = field_info.get("name", field_id)
            required = field_info.get("required", False)
            editable = field_info.get("operations", [])

            req_str = " (required)" if required else ""
            edit_str = f" (operations: {', '.join(editable)})" if editable else ""

            result += f"- {name}{req_str}{edit_str}\n"

        return result
    except Exception as e:
        return f"Error retrieving edit metadata for issue {issue_key}: {str(e)}"


@tool
def get_issue_changelog(issue_key: str) -> str:
    """
    Gets a changelog for an issue.

    Useful for tracking all changes made to an issue over time.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")

    Returns:
        str: Formatted changelog information or error message
    """
    client = get_jira_client()
    try:
        response = client.get(f"issue/{issue_key}/changelog")

        values = response.get("values", [])
        result = f"Changelog for issue {issue_key}:\n\n"

        for changelog in values:
            author = changelog.get("author", {}).get("displayName", "Unknown user")
            created = changelog.get("created", "Unknown time")

            result += f"Changed by {author} on {created}:\n"

            items = changelog.get("items", [])
            for item in items:
                field = item.get("field", "Unknown field")
                from_value = item.get("fromString", "None")
                to_value = item.get("toString", "None")

                result += f"  - {field}: {from_value} → {to_value}\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving changelog for issue {issue_key}: {str(e)}"


@tool
def get_changelogs_by_ids(issue_key: str, changelog_ids: list[str]) -> str:
    """
    Gets changelogs for an issue by their IDs.

    Useful for retrieving specific changes to an issue when you know the changelog IDs.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        changelog_ids (List[str]): A list of changelog IDs to fetch

    Returns:
        str: Formatted changelog information or error message
    """
    client = get_jira_client()
    try:
        data = {"changelogIds": changelog_ids}
        response = client.post(f"issue/{issue_key}/changelog/list", data)

        values = response.get("values", [])
        result = f"Changelogs for issue {issue_key}:\n\n"

        for changelog in values:
            changelog_id = changelog.get("id", "Unknown")
            author = changelog.get("author", {}).get("displayName", "Unknown user")
            created = changelog.get("created", "Unknown time")

            result += f"Changelog ID {changelog_id} by {author} on {created}:\n"

            items = changelog.get("items", [])
            for item in items:
                field = item.get("field", "Unknown field")
                from_value = item.get("fromString", "None")
                to_value = item.get("toString", "None")

                result += f"  - {field}: {from_value} → {to_value}\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error retrieving changelogs by IDs for issue {issue_key}: {str(e)}"


@tool
def bulk_fetch_changelogs(issue_keys: list[str]) -> str:
    """
    Fetches changelogs for multiple issues in a single request.

    Useful for efficiently retrieving history of changes for up to 100 issues at once.

    Args:
        issue_keys (List[str]): A list of issue keys to fetch changelogs for

    Returns:
        str: Summary of changelogs for the requested issues or error message
    """
    client = get_jira_client()
    try:
        data = {"issueIds": issue_keys}
        response = client.post("changelog/bulkfetch", data)

        changelogs = response.get("changelogs", [])
        result = f"Bulk fetched changelogs for {len(changelogs)} issues:\n\n"

        for issue_changelog in changelogs:
            issue_id = issue_changelog.get("issueId", "Unknown")
            issue_key = issue_changelog.get("issueKey", "Unknown")

            result += f"Issue {issue_key} (ID: {issue_id}):\n"

            histories = issue_changelog.get("histories", [])
            if histories:
                result += f"  {len(histories)} changes recorded\n"

                # Show details of the most recent change
                if histories:
                    most_recent = histories[0]  # Assuming the first one is the most recent
                    author = most_recent.get("author", {}).get("displayName", "Unknown user")
                    created = most_recent.get("created", "Unknown time")

                    result += f"  Most recent change by {author} on {created}\n"
            else:
                result += "  No changes recorded\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error bulk fetching changelogs: {str(e)}"


@tool
def send_issue_notification(
    issue_key: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    to_reporter: bool = False,
    to_assignee: bool = False,
    to_watchers: bool = False,
    to_voters: bool = False,
    to_users: list[str] | None = None,
    to_groups: list[str] | None = None,
) -> str:
    """
    Sends a notification about an issue to specified recipients.

    Useful for notifying stakeholders about important updates to an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        subject (str): The email subject
        text_body (str): The plain text body of the email
        html_body (str, optional): The HTML body of the email
        to_reporter (bool, optional): Send to the issue reporter. Defaults to False.
        to_assignee (bool, optional): Send to the issue assignee. Defaults to False.
        to_watchers (bool, optional): Send to issue watchers. Defaults to False.
        to_voters (bool, optional): Send to issue voters. Defaults to False.
        to_users (List[str], optional): List of user account IDs to send to
        to_groups (List[str], optional): List of group names to send to

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        data = {"subject": subject, "textBody": text_body}

        # Optional HTML body
        if html_body:
            data["htmlBody"] = html_body

        # Define notification recipients
        notification = {}

        if to_reporter:
            notification["reporter"] = True

        if to_assignee:
            notification["assignee"] = True

        if to_watchers:
            notification["watchers"] = True

        if to_voters:
            notification["voters"] = True

        if to_users:
            notification["users"] = [{"accountId": user_id} for user_id in to_users]

        if to_groups:
            notification["groups"] = [{"name": group} for group in to_groups]

        data["notification"] = notification

        client.post(f"issue/{issue_key}/notify", data)
        return f"Notification sent successfully for issue {issue_key}"
    except Exception as e:
        return f"Error sending notification for issue {issue_key}: {str(e)}"


@tool
def get_issue_limit_report() -> str:
    """
    Gets a report of issues approaching or breaching their limits.

    Useful for administrators to identify issues with excessive comments, attachments, or other content.
    This is an experimental Jira API endpoint.

    Returns:
        str: Formatted limit report information or error message
    """
    client = get_jira_client()
    try:
        response = client.get("issue/limit/report")

        approaching_limits = response.get("approachingLimits", [])
        breached_limits = response.get("breachedLimits", [])
        result = "Issue Limit Report:\n\n"

        if breached_limits:
            result += "Issues breaching limits:\n"
            for issue in breached_limits:
                issue_key = issue.get("issueKey", "Unknown")
                limit_type = issue.get("limitTypeInfo", {}).get("name", "Unknown limit type")
                count = issue.get("count", 0)
                limit = issue.get("limit", 0)

                result += f"- {issue_key}: {limit_type} - {count}/{limit}\n"

            result += "\n"

        if approaching_limits:
            result += "Issues approaching limits:\n"
            for issue in approaching_limits:
                issue_key = issue.get("issueKey", "Unknown")
                limit_type = issue.get("limitTypeInfo", {}).get("name", "Unknown limit type")
                count = issue.get("count", 0)
                limit = issue.get("limit", 0)

                result += f"- {issue_key}: {limit_type} - {count}/{limit}\n"

        if not approaching_limits and not breached_limits:
            result += "No issues approaching or breaching limits were found."

        return result
    except Exception as e:
        return f"Error retrieving issue limit report: {str(e)}"


# Export the tools for use in the JIRA assistant
issue_tools = [
    get_issue,
    create_issue,
    update_issue,
    delete_issue,
    assign_issue,
    get_issue_transitions,
    transition_issue,
    archive_issues_by_keys,
    archive_issues_by_jql,
    unarchive_issues,
    export_archived_issues,
    bulk_create_issues,
    bulk_fetch_issues,
    get_create_issue_metadata,
    get_create_metadata_issue_types,
    get_create_field_metadata,
    get_edit_issue_metadata,
    get_issue_changelog,
    get_changelogs_by_ids,
    bulk_fetch_changelogs,
    send_issue_notification,
    get_issue_limit_report,
]
