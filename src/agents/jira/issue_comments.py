"""
JIRA Issue Comments API Functions

This module provides tools for interacting with JIRA issue comments through the REST API.
"""

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_comment(issue_key: str, comment_id: str, expand: str | None = None) -> str:
    """
    Retrieves a specific comment from an issue.

    Useful for getting details of a single comment when you know its ID.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        comment_id (str): The ID of the comment to retrieve
        expand (str, optional): Additional properties to expand in the response

    Returns:
        str: JSON string with comment details
    """
    client = get_jira_client()
    try:
        params = {}
        if expand:
            params["expand"] = expand

        response = client.get(f"issue/{issue_key}/comment/{comment_id}", params=params)

        author = response.get("author", {}).get("displayName", "Unknown")
        body_text = "No content"

        # Extract text from Atlassian Document Format
        if response.get("body") and isinstance(response["body"], dict):
            if response["body"].get("content") and len(response["body"]["content"]) > 0:
                paragraphs = []
                for content in response["body"]["content"]:
                    if content.get("content"):
                        for text_node in content.get("content", []):
                            if text_node.get("text"):
                                paragraphs.append(text_node.get("text", ""))
                body_text = "\n".join(paragraphs)

        created = response.get("created", "Unknown")
        updated = response.get("updated", "Unknown")

        return f"Comment {comment_id} on issue {issue_key}:\n\nAuthor: {author}\nCreated: {created}\nUpdated: {updated}\n\nContent:\n{body_text}"
    except Exception as e:
        return f"Error retrieving comment {comment_id} for issue {issue_key}: {str(e)}"


@tool
def get_comments(
    issue_key: str, start_at: int = 0, max_results: int = 50, order_by: str = "created"
) -> str:
    """
    Retrieves all comments from an issue with pagination support.

    Useful for getting a list of comments on an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        start_at (int, optional): The index of the first comment to return. Defaults to 0.
        max_results (int, optional): Maximum number of comments to return. Defaults to 50.
        order_by (str, optional): Sort order for comments. Defaults to "created".
                                  Can be "created", "-created", "updated", or "-updated".

    Returns:
        str: Formatted list of comments
    """
    client = get_jira_client()
    try:
        params = {"startAt": start_at, "maxResults": max_results, "orderBy": order_by}

        response = client.get(f"issue/{issue_key}/comment", params=params)

        comments = response.get("comments", [])
        total = response.get("total", 0)

        result = f"Comments for issue {issue_key} (showing {len(comments)} of {total}):\n\n"

        for comment in comments:
            comment_id = comment.get("id", "Unknown ID")
            author = comment.get("author", {}).get("displayName", "Unknown")
            created = comment.get("created", "Unknown date")

            # Extract text from Atlassian Document Format
            body_text = "No content"
            if comment.get("body") and isinstance(comment["body"], dict):
                if comment["body"].get("content") and len(comment["body"]["content"]) > 0:
                    paragraphs = []
                    for content in comment["body"]["content"]:
                        if content.get("content"):
                            for text_node in content.get("content", []):
                                if text_node.get("text"):
                                    paragraphs.append(text_node.get("text", ""))
                    body_text = "\n".join(paragraphs)

            result += f"#{comment_id} by {author} on {created}:\n{body_text}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving comments for issue {issue_key}: {str(e)}"


@tool
def add_comment(issue_key: str, comment: str, visibility: dict[str, str] | None = None) -> str:
    """
    Adds a comment to a JIRA issue.

    Useful for adding notes or additional information to an issue.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        comment (str): Comment text
        visibility (Dict[str, str], optional): Visibility restrictions for the comment.
                                              Example: {"type": "role", "value": "Administrators"}

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

        if visibility:
            data["visibility"] = visibility

        response = client.post(f"issue/{issue_key}/comment", data)
        comment_id = response.get("id", "Unknown")
        return f"Comment added to issue {issue_key} successfully (ID: {comment_id})"
    except Exception as e:
        return f"Error adding comment to issue {issue_key}: {str(e)}"


@tool
def update_comment(
    issue_key: str, comment_id: str, comment: str, visibility: dict[str, str] | None = None
) -> str:
    """
    Updates an existing comment on an issue.

    Useful for editing comment text or changing visibility.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        comment_id (str): The ID of the comment to update
        comment (str): New comment text
        visibility (Dict[str, str], optional): Visibility restrictions for the comment.
                                              Example: {"type": "role", "value": "Administrators"}

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

        if visibility:
            data["visibility"] = visibility

        client.put(f"issue/{issue_key}/comment/{comment_id}", data)
        return f"Comment {comment_id} on issue {issue_key} updated successfully"
    except Exception as e:
        return f"Error updating comment {comment_id} on issue {issue_key}: {str(e)}"


@tool
def delete_comment(issue_key: str, comment_id: str) -> str:
    """
    Deletes a comment from an issue.

    Useful for removing comments that are no longer needed or contain incorrect information.

    Args:
        issue_key (str): The issue key (e.g., "PROJECT-123")
        comment_id (str): The ID of the comment to delete

    Returns:
        str: Success or error message
    """
    client = get_jira_client()
    try:
        client.delete(f"issue/{issue_key}/comment/{comment_id}")
        return f"Comment {comment_id} deleted from issue {issue_key} successfully"
    except Exception as e:
        return f"Error deleting comment {comment_id} from issue {issue_key}: {str(e)}"


@tool
def get_comments_by_ids(comment_ids: list[int], expand: str | None = None) -> str:
    """
    Retrieves comments from issues by their IDs.

    Useful for getting multiple comments across different issues when you know the comment IDs.

    Args:
        comment_ids (List[int]): A list of comment IDs to retrieve
        expand (str, optional): Additional properties to expand in the response

    Returns:
        str: Formatted list of comments
    """
    client = get_jira_client()
    try:
        data = {"ids": comment_ids}

        if expand:
            data["expand"] = expand

        response = client.post("comment/list", data)

        comments = response.get("comments", [])
        result = f"Retrieved {len(comments)} comments:\n\n"

        for comment in comments:
            comment_id = comment.get("id", "Unknown ID")
            issue_key = comment.get("self", "").split("/")[-3] if "self" in comment else "Unknown"
            author = comment.get("author", {}).get("displayName", "Unknown")
            created = comment.get("created", "Unknown date")

            # Extract text from Atlassian Document Format
            body_text = "No content"
            if comment.get("body") and isinstance(comment["body"], dict):
                if comment["body"].get("content") and len(comment["body"]["content"]) > 0:
                    paragraphs = []
                    for content in comment["body"]["content"]:
                        if content.get("content"):
                            for text_node in content.get("content", []):
                                if text_node.get("text"):
                                    paragraphs.append(text_node.get("text", ""))
                    body_text = "\n".join(paragraphs)

            result += f"Comment #{comment_id} on issue {issue_key} by {author} on {created}:\n{body_text}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving comments by IDs: {str(e)}"


# Export the tools for use in the JIRA assistant
comment_tools = [
    get_comment,
    get_comments,
    add_comment,
    update_comment,
    delete_comment,
    get_comments_by_ids,
]
