"""
Azure DevOps Work Items API Functions

This module provides tools for interacting with Azure DevOps work items through the API.
"""

from typing import Any, Dict, Optional
import json

from langchain_core.tools import tool
from azure.devops.v7_1.work_item_tracking.models import (
    QueryHierarchyItem,
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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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
                    "icon": {
                        "id": wit.icon.id,
                        "url": wit.icon.url,
                    },
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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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
        wit_client = client.get_work_item_tracking_client()

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


@tool
def get_work_item_updates(work_item_id: int) -> str:
    """
    Get the update history for a work item.

    Args:
        work_item_id (int): The ID of the work item

    Returns:
        str: JSON string containing the update history
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get updates
        updates = wit_client.get_updates(work_item_id)

        # Format for display
        formatted_updates = []
        for update in updates:
            formatted_update = {
                "id": update.id,
                "rev": update.rev,
                "fields": update.fields if hasattr(update, "fields") else None,
                "work_item_id": update.work_item_id,
                "updated_by": {
                    "id": update.revised_by.id,
                    "display_name": update.revised_by.display_name,
                }
                if hasattr(update, "revised_by") and update.revised_by
                else None,
                "updated_date": update.revised_date.isoformat()
                if hasattr(update, "revised_date") and update.revised_date
                else None,
            }
            formatted_updates.append(formatted_update)

        return json.dumps({"count": len(formatted_updates), "updates": formatted_updates}, indent=2)
    except Exception as e:
        return f"Error retrieving work item updates: {str(e)}"


@tool
def get_work_item_attachments(work_item_id: int) -> str:
    """
    Get all attachments for a work item.

    Args:
        work_item_id (int): The ID of the work item

    Returns:
        str: JSON string containing all attachments
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get work item with all fields
        work_item = wit_client.get_work_item(work_item_id, expand="Relations")

        # Check if work item has attachments
        if not hasattr(work_item, "relations") or not work_item.relations:
            return json.dumps({"count": 0, "attachments": []})

        # Filter relations to get only attachments
        attachment_relations = [rel for rel in work_item.relations if rel.rel == "AttachedFile"]

        # Format for display
        formatted_attachments = []
        for relation in attachment_relations:
            attachment_url = relation.url
            attachment_id = attachment_url.split("/")[-1]

            formatted_attachment = {
                "id": attachment_id,
                "url": attachment_url,
                "attributes": relation.attributes,
            }
            formatted_attachments.append(formatted_attachment)

        return json.dumps(
            {"count": len(formatted_attachments), "attachments": formatted_attachments}, indent=2
        )
    except Exception as e:
        return f"Error retrieving work item attachments: {str(e)}"


@tool
def create_work_item_relation(
    work_item_id: int, related_work_item_id: int, relation_type: str
) -> str:
    """
    Create a relation between two work items.

    Args:
        work_item_id (int): The ID of the source work item
        related_work_item_id (int): The ID of the target work item
        relation_type (str): The type of relation (e.g., "Child", "Parent", "Related", etc.)

    Returns:
        str: JSON string containing the updated work item with the new relation
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Map relation type to API relation string
        relation_map = {
            "Child": "System.LinkTypes.Hierarchy-Forward",
            "Parent": "System.LinkTypes.Hierarchy-Reverse",
            "Related": "System.LinkTypes.Related",
            "Successor": "System.LinkTypes.Dependency-Forward",
            "Predecessor": "System.LinkTypes.Dependency-Reverse",
        }

        relation_url = relation_map.get(relation_type)
        if not relation_url:
            relation_url = relation_type  # Use the provided value if not in our map

        # Create the URL for the related work item
        organization_url = client.get_connection().base_url.rstrip("/")
        target_url = f"{organization_url}/_apis/wit/workItems/{related_work_item_id}"

        # Create document for json patch operations
        document = [
            {"op": "add", "path": "/relations/-", "value": {"rel": relation_url, "url": target_url}}
        ]

        # Update work item to add the relation
        updated_work_item = wit_client.update_work_item(document=document, id=work_item_id)

        # Format for display
        formatted_work_item = {
            "id": updated_work_item.id,
            "rev": updated_work_item.rev,
            "url": updated_work_item.url,
            "message": f"Relation of type '{relation_type}' created between work items {work_item_id} and {related_work_item_id}",
        }

        return json.dumps(formatted_work_item, indent=2)
    except Exception as e:
        return f"Error creating work item relation: {str(e)}"


@tool
def delete_work_item(work_item_id: int, permanent: bool = False) -> str:
    """
    Delete a work item. By default, the work item is moved to the Recycle Bin.

    Args:
        work_item_id (int): The ID of the work item to delete
        permanent (bool, optional): If True, permanently delete the work item bypassing the Recycle Bin

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Delete the work item
        result = wit_client.delete_work_item(id=work_item_id, destroy=permanent)

        # Format for display
        formatted_result = {
            "id": result.id,
            "code": result.code,
            "message": f"Work item {work_item_id} has been {'permanently deleted' if permanent else 'moved to the Recycle Bin'}",
            "url": result.url if hasattr(result, "url") else None,
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error deleting work item: {str(e)}"


@tool
def add_attachment_to_work_item(
    work_item_id: int, attachment_path: str, comment: str = None
) -> str:
    """
    Add an attachment to a work item.

    Args:
        work_item_id (int): The ID of the work item
        attachment_path (str): The path to the file to attach
        comment (str, optional): A comment to include with the attachment

    Returns:
        str: JSON string containing the attachment information
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Read the file contents
        import os
        import base64

        if not os.path.exists(attachment_path):
            return f"Error: File {attachment_path} does not exist"

        with open(attachment_path, "rb") as f:
            file_content = f.read()

        # Get filename from path
        filename = os.path.basename(attachment_path)

        # Upload the attachment
        attachment = wit_client.create_attachment(upload_stream=file_content, file_name=filename)

        # Create the relation to the work item
        attachment_url = attachment.url

        # Create document for json patch operations
        document = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "AttachedFile",
                    "url": attachment_url,
                    "attributes": {"comment": comment if comment else f"Attached file: {filename}"},
                },
            }
        ]

        # Update work item to add the attachment relation
        updated_work_item = wit_client.update_work_item(document=document, id=work_item_id)

        # Format for display
        formatted_result = {
            "work_item_id": updated_work_item.id,
            "attachment_name": filename,
            "attachment_url": attachment_url,
            "message": f"Attachment '{filename}' added to work item {work_item_id}",
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error adding attachment to work item: {str(e)}"


@tool
def get_work_item_query_result(project_name: str, query_id: str) -> str:
    """
    Run a saved work item query by ID.

    Args:
        project_name (str): The name of the project
        query_id (str): The ID of the saved query

    Returns:
        str: JSON string containing the query results
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Run the saved query
        query_result = wit_client.query_by_id(query_id, project=project_name)

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
        return f"Error running saved query: {str(e)}"


@tool
def get_queries(project_name: str, query_path: Optional[str] = None) -> str:
    """
    Get all queries in a project or folder.

    Args:
        project_name (str): The name of the project
        query_path (Optional[str]): The path to the queries folder (e.g., "Shared Queries/Folder")

    Returns:
        str: JSON string containing the queries
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get queries from the specified path
        queries = wit_client.get_queries(project_name, query_path, depth=2)

        # Format for display
        formatted_queries = []
        for query in queries:
            formatted_query = {
                "id": query.id,
                "name": query.name,
                "path": query.path,
                "query_type": query.query_type,
                "is_folder": query.has_children if hasattr(query, "has_children") else False,
                "is_public": query.is_public if hasattr(query, "is_public") else False,
                "url": query.url,
            }
            formatted_queries.append(formatted_query)

        return json.dumps(formatted_queries, indent=2)
    except Exception as e:
        return f"Error retrieving queries: {str(e)}"


@tool
def create_query(
    project_name: str,
    query_name: str,
    query_string: str,
    folder_path: str,
    is_public: bool = True,
) -> str:
    """
    Create a new query in a project.

    Args:
        project_name (str): The name of the project
        query_name (str): The name of the query
        query_string (str): The WIQL query string
        folder_path (str): The path to the folder where the query should be created
        is_public (bool, optional): Whether the query is public

    Returns:
        str: JSON string containing the created query
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Ensure query starts with SELECT
        if not query_string.strip().upper().startswith("SELECT"):
            return "Error: Query must start with SELECT."

        # Create the query object
        query = QueryHierarchyItem(
            name=query_name,
            wiql=query_string,
            is_public=is_public,
            query_type="flat",  # Use 'flat' for simple queries, 'tree' for hierarchy queries
        )

        # Create the query
        created_query = wit_client.create_query(query, project_name, folder_path)

        # Format for display
        formatted_query = {
            "id": created_query.id,
            "name": created_query.name,
            "path": created_query.path,
            "query_type": created_query.query_type,
            "wiql": created_query.wiql if hasattr(created_query, "wiql") else None,
            "is_public": created_query.is_public if hasattr(created_query, "is_public") else None,
            "url": created_query.url,
        }

        return json.dumps(formatted_query, indent=2)
    except Exception as e:
        return f"Error creating query: {str(e)}"


@tool
def delete_query(project_name: str, query_id: str) -> str:
    """
    Delete a query.

    Args:
        project_name (str): The name of the project
        query_id (str): The ID of the query

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Delete the query
        wit_client.delete_query(project_name, query_id)

        # Format for display
        formatted_result = {"message": f"Query with ID {query_id} has been deleted successfully."}

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error deleting query: {str(e)}"


@tool
def get_work_item_revisions(work_item_id: int, top: int = 10) -> str:
    """
    Get the revision history of a work item.

    Args:
        work_item_id (int): The ID of the work item
        top (int, optional): Maximum number of revisions to return

    Returns:
        str: JSON string containing the revision history
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get revisions
        revisions = wit_client.get_revisions(work_item_id, top=top)

        # Format for display
        formatted_revisions = []
        for revision in revisions:
            formatted_revision = {
                "id": revision.id,
                "rev": revision.rev,
                "fields": revision.fields,
                "work_item_id": revision.id,
                "url": revision.url,
            }

            # Add revised by info if available
            if hasattr(revision, "revised_by") and revision.revised_by:
                formatted_revision["revised_by"] = {
                    "id": revision.revised_by.id,
                    "display_name": revision.revised_by.display_name,
                }

            # Add revised date if available
            if hasattr(revision, "revised_date") and revision.revised_date:
                formatted_revision["revised_date"] = revision.revised_date.isoformat()

            formatted_revisions.append(formatted_revision)

        return json.dumps(
            {"count": len(formatted_revisions), "revisions": formatted_revisions}, indent=2
        )
    except Exception as e:
        return f"Error retrieving work item revisions: {str(e)}"


@tool
def get_work_item_revision(work_item_id: int, revision_number: int) -> str:
    """
    Get a specific revision of a work item.

    Args:
        work_item_id (int): The ID of the work item
        revision_number (int): The revision number to retrieve

    Returns:
        str: JSON string containing the work item revision
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get the specific revision
        revision = wit_client.get_revision(work_item_id, revision_number)

        # Format for display
        formatted_revision = {
            "id": revision.id,
            "rev": revision.rev,
            "fields": revision.fields,
            "url": revision.url,
        }

        # Add revised by info if available
        if hasattr(revision, "revised_by") and revision.revised_by:
            formatted_revision["revised_by"] = {
                "id": revision.revised_by.id,
                "display_name": revision.revised_by.display_name,
            }

        # Add revised date if available
        if hasattr(revision, "revised_date") and revision.revised_date:
            formatted_revision["revised_date"] = revision.revised_date.isoformat()

        return json.dumps(formatted_revision, indent=2)
    except Exception as e:
        return f"Error retrieving work item revision: {str(e)}"


@tool
def get_work_item_tags(project_name: str) -> str:
    """
    Get all work item tags in a project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: JSON string containing all tags
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get all tags in the project
        tags = wit_client.get_tags(project_name)

        # Format for display
        formatted_tags = []
        for tag in tags.value:
            formatted_tag = {
                "id": tag.id,
                "name": tag.name,
                "url": tag.url,
            }
            formatted_tags.append(formatted_tag)

        return json.dumps({"count": len(formatted_tags), "tags": formatted_tags}, indent=2)
    except Exception as e:
        return f"Error retrieving work item tags: {str(e)}"


@tool
def create_work_item_tag(project_name: str, tag_name: str) -> str:
    """
    Create a new work item tag.

    Args:
        project_name (str): The name of the project
        tag_name (str): The name of the tag to create

    Returns:
        str: JSON string containing the created tag
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Create the tag
        tag = wit_client.create_tag(project_name, tag_name)

        # Format for display
        formatted_tag = {
            "id": tag.id,
            "name": tag.name,
            "url": tag.url,
        }

        return json.dumps(formatted_tag, indent=2)
    except Exception as e:
        return f"Error creating work item tag: {str(e)}"


@tool
def add_tag_to_work_item(work_item_id: int, tag: str) -> str:
    """
    Add a tag to a work item.

    Args:
        work_item_id (int): The ID of the work item
        tag (str): The tag to add

    Returns:
        str: JSON string containing the updated work item
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get current work item to check if it already has the tag
        work_item = wit_client.get_work_item(work_item_id)

        current_tags = []
        if work_item.fields.get("System.Tags"):
            current_tags = [t.strip() for t in work_item.fields["System.Tags"].split(";")]

        # If tag already exists, return early
        if tag in current_tags:
            return json.dumps(
                {
                    "id": work_item.id,
                    "message": f"Tag '{tag}' already exists on work item {work_item_id}",
                },
                indent=2,
            )

        # Add the new tag to the list
        current_tags.append(tag)
        new_tags_string = "; ".join(current_tags)

        # Create document for json patch operations
        document = [{"op": "add", "path": "/fields/System.Tags", "value": new_tags_string}]

        # Update work item to add the tag
        updated_work_item = wit_client.update_work_item(document=document, id=work_item_id)

        # Format for display
        formatted_result = {
            "id": updated_work_item.id,
            "rev": updated_work_item.rev,
            "message": f"Tag '{tag}' added to work item {work_item_id}",
            "tags": updated_work_item.fields.get("System.Tags", ""),
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error adding tag to work item: {str(e)}"


@tool
def remove_tag_from_work_item(work_item_id: int, tag: str) -> str:
    """
    Remove a tag from a work item.

    Args:
        work_item_id (int): The ID of the work item
        tag (str): The tag to remove

    Returns:
        str: JSON string containing the updated work item
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Get current work item to check if it has the tag
        work_item = wit_client.get_work_item(work_item_id)

        if not work_item.fields.get("System.Tags"):
            return json.dumps(
                {
                    "id": work_item.id,
                    "message": f"Work item {work_item_id} has no tags",
                },
                indent=2,
            )

        current_tags = [t.strip() for t in work_item.fields["System.Tags"].split(";")]

        # If tag doesn't exist, return early
        if tag not in current_tags:
            return json.dumps(
                {
                    "id": work_item.id,
                    "message": f"Tag '{tag}' does not exist on work item {work_item_id}",
                    "tags": work_item.fields.get("System.Tags", ""),
                },
                indent=2,
            )

        # Remove the tag from the list
        current_tags.remove(tag)
        new_tags_string = "; ".join(current_tags)

        # Create document for json patch operations
        document = [{"op": "add", "path": "/fields/System.Tags", "value": new_tags_string}]

        # Update work item to remove the tag
        updated_work_item = wit_client.update_work_item(document=document, id=work_item_id)

        # Format for display
        formatted_result = {
            "id": updated_work_item.id,
            "rev": updated_work_item.rev,
            "message": f"Tag '{tag}' removed from work item {work_item_id}",
            "tags": updated_work_item.fields.get("System.Tags", ""),
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error removing tag from work item: {str(e)}"


@tool
def get_work_item_templates(project_name: str, team: Optional[str] = None) -> str:
    """
    Get all work item templates for a team or project.

    Args:
        project_name (str): The name of the project
        team (Optional[str]): The name of the team

    Returns:
        str: JSON string containing the templates
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # If team is provided, get templates for that specific team
        if team:
            templates = wit_client.get_templates(project_name, team)
        else:
            # Get templates for the project
            templates = wit_client.get_templates(project_name)

        # Format for display
        formatted_templates = []
        for template in templates:
            formatted_template = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "work_item_type": template.work_item_type_name,
                "fields": template.fields,
            }
            formatted_templates.append(formatted_template)

        return json.dumps(
            {"count": len(formatted_templates), "templates": formatted_templates}, indent=2
        )
    except Exception as e:
        return f"Error retrieving work item templates: {str(e)}"


@tool
def create_work_item_from_template(
    project_name: str, template_id: str, additional_fields: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a work item from a template.

    Args:
        project_name (str): The name of the project
        template_id (str): The ID of the template
        additional_fields (Optional[Dict[str, Any]]): Additional fields to set on the work item

    Returns:
        str: JSON string containing the created work item
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Create work item from template
        document = []

        # Add additional fields if provided
        if additional_fields:
            for field, value in additional_fields.items():
                document.append({"op": "add", "path": f"/fields/{field}", "value": value})

        # Create the work item using the template
        created_work_item = wit_client.create_work_item_from_template(
            document=document, project=project_name, template_id=template_id
        )

        # Format for display
        formatted_work_item = {
            "id": created_work_item.id,
            "rev": created_work_item.rev,
            "fields": created_work_item.fields,
            "url": created_work_item.url,
        }

        return json.dumps(formatted_work_item, indent=2)
    except Exception as e:
        return f"Error creating work item from template: {str(e)}"


@tool
def get_work_item_classification_nodes(
    project_name: str, structure_type: str, path: Optional[str] = None, depth: int = 2
) -> str:
    """
    Get work item classification nodes (areas or iterations).

    Args:
        project_name (str): The name of the project
        structure_type (str): The type of structure ('areas' or 'iterations')
        path (Optional[str]): The path of the classification node (optional)
        depth (int): The depth of children to fetch

    Returns:
        str: JSON string containing the classification nodes
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_work_item_tracking_client()

        # Validate structure type
        if structure_type.lower() not in ["areas", "iterations"]:
            return "Error: structure_type must be either 'areas' or 'iterations'"

        # Get classification nodes
        nodes = wit_client.get_classification_node(
            project=project_name, structure_type=structure_type.lower(), path=path, depth=depth
        )

        # Format for display
        def format_node(node):
            formatted = {
                "id": node.id,
                "name": node.name,
                "path": node.path,
                "url": node.url,
            }

            # Add children if they exist
            if hasattr(node, "children") and node.children:
                formatted["children"] = [format_node(child) for child in node.children]

            return formatted

        formatted_result = format_node(nodes)

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error retrieving classification nodes: {str(e)}"


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
    get_work_item_updates,
    get_work_item_attachments,
    create_work_item_relation,
    delete_work_item,
    add_attachment_to_work_item,
    get_work_item_query_result,
    get_queries,
    create_query,
    delete_query,
    get_work_item_revisions,
    get_work_item_revision,
    get_work_item_tags,
    create_work_item_tag,
    add_tag_to_work_item,
    remove_tag_from_work_item,
    get_work_item_templates,
    create_work_item_from_template,
    get_work_item_classification_nodes,
]
