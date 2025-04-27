"""
Azure DevOps Work Items API Functions

This module provides tools for interacting with Azure DevOps work items through the API.
"""

from typing import Any, Dict, List, Optional, Union
import json

from langchain_core.tools import BaseTool, tool
from azure.devops.v7_1.work_item_tracking.models import (
    JsonPatchOperation,
    WorkItem,
    WorkItemReference,
    WorkItemQueryResult,
)

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_work_item(work_item_id: int) -> str:
    """
    Get details for a specific work item by ID.

    Args:
        work_item_id (int): The ID of the work item

    Returns:
        str: JSON string containing work item details
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Get work item with all fields
        work_item = wit_client.get_work_item(work_item_id, expand="All")

        # Format for display
        formatted_work_item = {
            "id": work_item.id,
            "rev": work_item.rev,
            "fields": work_item.fields,
            "url": work_item.url,
        }

        # Add relationships if they exist
        if hasattr(work_item, "relations") and work_item.relations:
            formatted_work_item["relations"] = [
                {"rel": relation.rel, "url": relation.url, "attributes": relation.attributes}
                for relation in work_item.relations
            ]

        return json.dumps(formatted_work_item, indent=2)
    except Exception as e:
        return f"Error retrieving work item: {str(e)}"


@tool
def create_work_item(
    project_name: str,
    work_item_type: str,
    title: str,
    description: Optional[str] = None,
    assigned_to: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[int] = None,
    additional_fields: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new work item.

    Args:
        project_name (str): The name of the project
        work_item_type (str): The type of work item (Bug, Task, User Story, etc.)
        title (str): The title of the work item
        description (Optional[str]): The description of the work item
        assigned_to (Optional[str]): The user to assign the work item to
        state (Optional[str]): The state of the work item
        priority (Optional[int]): The priority of the work item
        additional_fields (Optional[Dict[str, Any]]): Additional fields to set on the work item

    Returns:
        str: JSON string containing the created work item details
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Create document for json patch operations
        document = []

        # Add title
        document.append({"op": "add", "path": "/fields/System.Title", "value": title})

        # Add description if provided
        if description:
            document.append(
                {"op": "add", "path": "/fields/System.Description", "value": description}
            )

        # Add assigned to if provided
        if assigned_to:
            document.append(
                {"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to}
            )

        # Add state if provided
        if state:
            document.append({"op": "add", "path": "/fields/System.State", "value": state})

        # Add priority if provided
        if priority is not None:
            document.append(
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority}
            )

        # Add additional fields if provided
        if additional_fields:
            for field, value in additional_fields.items():
                document.append({"op": "add", "path": f"/fields/{field}", "value": value})

        # Create work item
        created_work_item = wit_client.create_work_item(
            document=document, project=project_name, type=work_item_type
        )

        # Format for display
        formatted_work_item = {
            "id": created_work_item.id,
            "url": created_work_item.url,
            "fields": created_work_item.fields,
        }

        return json.dumps(formatted_work_item, indent=2)
    except Exception as e:
        return f"Error creating work item: {str(e)}"


@tool
def update_work_item(
    work_item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assigned_to: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[int] = None,
    additional_fields: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Update an existing work item.

    Args:
        work_item_id (int): The ID of the work item to update
        title (Optional[str]): The new title
        description (Optional[str]): The new description
        assigned_to (Optional[str]): The user to assign the work item to
        state (Optional[str]): The new state
        priority (Optional[int]): The new priority
        additional_fields (Optional[Dict[str, Any]]): Additional fields to update

    Returns:
        str: JSON string containing the updated work item details
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Create document for json patch operations
        document = []

        # Update title if provided
        if title:
            document.append({"op": "add", "path": "/fields/System.Title", "value": title})

        # Update description if provided
        if description:
            document.append(
                {"op": "add", "path": "/fields/System.Description", "value": description}
            )

        # Update assigned to if provided
        if assigned_to:
            document.append(
                {"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to}
            )

        # Update state if provided
        if state:
            document.append({"op": "add", "path": "/fields/System.State", "value": state})

        # Update priority if provided
        if priority is not None:
            document.append(
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority}
            )

        # Update additional fields if provided
        if additional_fields:
            for field, value in additional_fields.items():
                document.append({"op": "add", "path": f"/fields/{field}", "value": value})

        # If no fields to update, return an error
        if not document:
            return "Error: No fields provided to update."

        # Update work item
        updated_work_item = wit_client.update_work_item(document=document, id=work_item_id)

        # Format for display
        formatted_work_item = {
            "id": updated_work_item.id,
            "rev": updated_work_item.rev,
            "fields": updated_work_item.fields,
            "url": updated_work_item.url,
        }

        return json.dumps(formatted_work_item, indent=2)
    except Exception as e:
        return f"Error updating work item: {str(e)}"


@tool
def get_work_items_by_wiql(project_name: str, query: str, top: int = 100) -> str:
    """
    Query work items using WIQL (Work Item Query Language).

    Args:
        project_name (str): The name of the project
        query (str): The WIQL query string
        top (int, optional): Maximum number of results to return

    Returns:
        str: JSON string containing the work items that match the query
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Ensure query starts with SELECT
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Query must start with SELECT."

        # Create WIQL object
        wiql = {"query": query}

        # Run query
        query_result = wit_client.query_by_wiql(wiql, project=project_name, top=top)

        # If no work items found
        if not query_result.work_items:
            return json.dumps({"count": 0, "work_items": []})

        # Get work item IDs
        work_item_ids = [item.id for item in query_result.work_items]

        # Get full work items
        work_items = wit_client.get_work_items(work_item_ids, expand="All")

        # Format for display
        formatted_work_items = []
        for work_item in work_items:
            formatted_work_item = {
                "id": work_item.id,
                "rev": work_item.rev,
                "fields": work_item.fields,
                "url": work_item.url,
            }
            formatted_work_items.append(formatted_work_item)

        return json.dumps(
            {"count": len(formatted_work_items), "work_items": formatted_work_items}, indent=2
        )
    except Exception as e:
        return f"Error querying work items: {str(e)}"


@tool
def get_work_item_types(project_name: str) -> str:
    """
    Get all work item types in a project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: JSON string containing all work item types
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        work_item_types = wit_client.get_work_item_types(project_name)

        # Format for display
        formatted_types = []
        for wit in work_item_types:
            formatted_types.append(
                {
                    "name": wit.name,
                    "reference_name": wit.reference_name,
                    "description": wit.description,
                    "color": wit.color,
                    "icon": wit.icon,
                }
            )

        return json.dumps(formatted_types, indent=2)
    except Exception as e:
        return f"Error retrieving work item types: {str(e)}"


@tool
def get_work_item_states(project_name: str, work_item_type: str) -> str:
    """
    Get all states for a work item type.

    Args:
        project_name (str): The name of the project
        work_item_type (str): The type of work item

    Returns:
        str: JSON string containing all states
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        states = wit_client.get_work_item_type_states(project_name, work_item_type)

        # Format for display
        formatted_states = []
        for state in states:
            formatted_states.append(
                {"name": state.name, "color": state.color, "state_category": state.state_category}
            )

        return json.dumps(formatted_states, indent=2)
    except Exception as e:
        return f"Error retrieving work item states: {str(e)}"


@tool
def add_comment_to_work_item(work_item_id: int, comment: str) -> str:
    """
    Add a comment to a work item.

    Args:
        work_item_id (int): The ID of the work item
        comment (str): The comment text

    Returns:
        str: JSON string containing the added comment
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        comment_obj = {"text": comment}

        # Add comment
        added_comment = wit_client.add_comment(comment_obj, work_item_id)

        # Format for display
        formatted_comment = {
            "id": added_comment.id,
            "text": added_comment.text,
            "created_by": {
                "id": added_comment.created_by.id,
                "display_name": added_comment.created_by.display_name,
            }
            if added_comment.created_by
            else None,
            "created_date": added_comment.created_date.isoformat()
            if added_comment.created_date
            else None,
            "url": added_comment.url,
        }

        return json.dumps(formatted_comment, indent=2)
    except Exception as e:
        return f"Error adding comment: {str(e)}"


@tool
def get_work_item_comments(work_item_id: int) -> str:
    """
    Get all comments for a work item.

    Args:
        work_item_id (int): The ID of the work item

    Returns:
        str: JSON string containing all comments
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Get comments
        comments = wit_client.get_comments(work_item_id)

        # Format for display
        formatted_comments = []
        for comment in comments.comments:
            formatted_comment = {
                "id": comment.id,
                "text": comment.text,
                "created_by": {
                    "id": comment.created_by.id,
                    "display_name": comment.created_by.display_name,
                }
                if comment.created_by
                else None,
                "created_date": comment.created_date.isoformat() if comment.created_date else None,
                "url": comment.url,
            }
            formatted_comments.append(formatted_comment)

        return json.dumps({"count": comments.count, "comments": formatted_comments}, indent=2)
    except Exception as e:
        return f"Error retrieving comments: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
work_item_tools = [
    get_work_item,
    create_work_item,
    update_work_item,
    get_work_items_by_wiql,
    get_work_item_types,
    get_work_item_states,
    add_comment_to_work_item,
    get_work_item_comments,
]
