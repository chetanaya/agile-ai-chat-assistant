"""
Azure DevOps Work Item Tracking Process API Functions

This module provides tools for interacting with Azure DevOps work item tracking processes through the API.
"""

import json

from langchain_core.tools import tool

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_processes() -> str:
    """
    Get all processes in the organization.

    Returns:
        str: JSON string containing all processes
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get processes
        processes = process_client.get_list_of_processes()

        # Format for display
        formatted_processes = []
        for process in processes:
            formatted_process = {
                "id": process.id,
                "name": process.name,
                "description": process.description,
                "type_id": process.type_id,
                "is_default": process.is_default,
                "is_enabled": process.is_enabled,
                "url": process.url,
            }
            formatted_processes.append(formatted_process)

        return json.dumps(
            {"count": len(formatted_processes), "processes": formatted_processes}, indent=2
        )
    except Exception as e:
        return f"Error retrieving processes: {str(e)}"


@tool
def get_process(process_id: str) -> str:
    """
    Get details of a specific process.

    Args:
        process_id (str): The ID of the process

    Returns:
        str: JSON string containing process details
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get process
        process = process_client.get_process_by_id(process_id)

        # Format for display
        formatted_process = {
            "id": process.id,
            "name": process.name,
            "description": process.description,
            "type_id": process.type_id,
            "is_default": process.is_default,
            "is_enabled": process.is_enabled,
            "url": process.url,
        }

        return json.dumps(formatted_process, indent=2)
    except Exception as e:
        return f"Error retrieving process: {str(e)}"


@tool
def get_process_work_item_types(process_id: str) -> str:
    """
    Get all work item types in a process.

    Args:
        process_id (str): The ID of the process

    Returns:
        str: JSON string containing all work item types
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get work item types
        work_item_types = process_client.get_work_item_types(process_id)

        # Format for display
        formatted_types = []
        for wit in work_item_types:
            formatted_type = {
                "id": wit.id,
                "name": wit.name,
                "description": wit.description,
                "color": wit.color,
                "icon": wit.icon,
                "is_disabled": wit.is_disabled,
                "inherits_from": wit.inherits_from,
                "reference_name": wit.reference_name,
                "url": wit.url,
            }
            formatted_types.append(formatted_type)

        return json.dumps(
            {"count": len(formatted_types), "work_item_types": formatted_types}, indent=2
        )
    except Exception as e:
        return f"Error retrieving work item types: {str(e)}"


@tool
def get_process_work_item_type(process_id: str, wit_ref_name: str) -> str:
    """
    Get details of a specific work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type

    Returns:
        str: JSON string containing work item type details
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get work item type
        wit = process_client.get_work_item_type(process_id, wit_ref_name)

        # Format for display
        formatted_type = {
            "id": wit.id,
            "name": wit.name,
            "description": wit.description,
            "color": wit.color,
            "icon": wit.icon,
            "is_disabled": wit.is_disabled,
            "inherits_from": wit.inherits_from,
            "reference_name": wit.reference_name,
            "url": wit.url,
        }

        return json.dumps(formatted_type, indent=2)
    except Exception as e:
        return f"Error retrieving work item type: {str(e)}"


@tool
def get_states(process_id: str, wit_ref_name: str) -> str:
    """
    Get all states for a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type

    Returns:
        str: JSON string containing all states
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get states
        states = process_client.get_states(process_id, wit_ref_name)

        # Format for display
        formatted_states = []
        for state in states:
            formatted_state = {
                "id": state.id,
                "name": state.name,
                "color": state.color,
                "state_category": state.state_category,
                "order": state.order,
                "hidden": state.hidden if hasattr(state, "hidden") else False,
                "url": state.url,
            }
            formatted_states.append(formatted_state)

        return json.dumps({"count": len(formatted_states), "states": formatted_states}, indent=2)
    except Exception as e:
        return f"Error retrieving states: {str(e)}"


@tool
def get_state(process_id: str, wit_ref_name: str, state_id: str) -> str:
    """
    Get details of a specific state for a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type
        state_id (str): The ID of the state

    Returns:
        str: JSON string containing state details
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get state
        state = process_client.get_state(process_id, wit_ref_name, state_id)

        # Format for display
        formatted_state = {
            "id": state.id,
            "name": state.name,
            "color": state.color,
            "state_category": state.state_category,
            "order": state.order,
            "hidden": state.hidden if hasattr(state, "hidden") else False,
            "url": state.url,
        }

        return json.dumps(formatted_state, indent=2)
    except Exception as e:
        return f"Error retrieving state: {str(e)}"


@tool
def create_state(
    process_id: str,
    wit_ref_name: str,
    name: str,
    color: str,
    state_category: str,
    order: int | None = None,
    hidden: bool = False,
) -> str:
    """
    Create a new state for a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type
        name (str): The name of the state
        color (str): The color of the state (hex code without #)
        state_category (str): The category of the state (Proposed, InProgress, Resolved, Completed)
        order (Optional[int]): The order of the state
        hidden (bool): Whether the state is hidden

    Returns:
        str: JSON string containing the created state details
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Create state model
        state_model = {
            "name": name,
            "color": color,
            "stateCategory": state_category,
        }

        if order is not None:
            state_model["order"] = order

        if hidden:
            state_model["hidden"] = hidden

        # Create state
        created_state = process_client.create_state(state_model, process_id, wit_ref_name)

        # Format for display
        formatted_state = {
            "id": created_state.id,
            "name": created_state.name,
            "color": created_state.color,
            "state_category": created_state.state_category,
            "order": created_state.order,
            "hidden": created_state.hidden if hasattr(created_state, "hidden") else False,
            "url": created_state.url,
        }

        return json.dumps(formatted_state, indent=2)
    except Exception as e:
        return f"Error creating state: {str(e)}"


@tool
def update_state(
    process_id: str,
    wit_ref_name: str,
    state_id: str,
    name: str | None = None,
    color: str | None = None,
    state_category: str | None = None,
    order: int | None = None,
    hidden: bool | None = None,
) -> str:
    """
    Update a state for a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type
        state_id (str): The ID of the state to update
        name (Optional[str]): The new name of the state
        color (Optional[str]): The new color of the state (hex code without #)
        state_category (Optional[str]): The new category of the state
        order (Optional[int]): The new order of the state
        hidden (Optional[bool]): Whether the state is hidden

    Returns:
        str: JSON string containing the updated state details
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Create state update model
        state_model = {}

        if name is not None:
            state_model["name"] = name

        if color is not None:
            state_model["color"] = color

        if state_category is not None:
            state_model["stateCategory"] = state_category

        if order is not None:
            state_model["order"] = order

        if hidden is not None:
            state_model["hidden"] = hidden

        # If no updates, return error
        if not state_model:
            return "Error: No update parameters provided."

        # Update state
        updated_state = process_client.update_state(state_model, process_id, wit_ref_name, state_id)

        # Format for display
        formatted_state = {
            "id": updated_state.id,
            "name": updated_state.name,
            "color": updated_state.color,
            "state_category": updated_state.state_category,
            "order": updated_state.order,
            "hidden": updated_state.hidden if hasattr(updated_state, "hidden") else False,
            "url": updated_state.url,
        }

        return json.dumps(formatted_state, indent=2)
    except Exception as e:
        return f"Error updating state: {str(e)}"


@tool
def delete_state(process_id: str, wit_ref_name: str, state_id: str) -> str:
    """
    Delete a state from a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type
        state_id (str): The ID of the state to delete

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Delete state
        process_client.delete_state(process_id, wit_ref_name, state_id)

        # Format for display
        formatted_result = {"message": f"State with ID {state_id} has been deleted successfully."}

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error deleting state: {str(e)}"


@tool
def get_work_item_type_states(project_name: str, type: str) -> str:
    """
    Get all states for a work item type in a project.

    NOTE: This function is using the regular Work Item Tracking API, not the Process API.
    It is included here for completeness related to state management.

    Args:
        project_name (str): The name of the project
        type (str): The state name

    Returns:
        str: JSON string containing all states
    """
    try:
        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        states = wit_client.get_work_item_type_states(project_name, type)

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
def get_process_work_item_type_fields(process_id: str, wit_ref_name: str) -> str:
    """
    Get all fields for a work item type in a process.

    Args:
        process_id (str): The ID of the process
        wit_ref_name (str): The reference name of the work item type

    Returns:
        str: JSON string containing all fields
    """
    try:
        client = get_azure_devops_client()
        process_client = client.get_client("work_item_tracking_process")

        # Get fields
        fields = process_client.get_work_item_type_fields(process_id, wit_ref_name)

        # Format for display
        formatted_fields = []
        for field in fields:
            formatted_field = {
                "id": field.id,
                "name": field.name,
                "reference_name": field.reference_name,
                "type": field.type,
                "url": field.url,
            }
            formatted_fields.append(formatted_field)

        return json.dumps({"count": len(formatted_fields), "fields": formatted_fields}, indent=2)
    except Exception as e:
        return f"Error retrieving fields: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
work_item_tracking_process_tools = [
    get_processes,
    get_process,
    get_process_work_item_types,
    get_process_work_item_type,
    get_states,
    get_state,
    create_state,
    update_state,
    delete_state,
    get_work_item_type_states,
    get_process_work_item_type_fields,
]
