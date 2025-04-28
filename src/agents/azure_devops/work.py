"""
Azure DevOps Work Management API Functions

This module provides tools for interacting with Azure DevOps iterations, sprints, boards, and team settings through the API.
"""

import json
from typing import Any, Dict, List, Optional

from azure.devops.v7_1.work.models import TeamContext
from langchain_core.tools import tool

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_team_iterations(project_name: str, team_name: str, timeframe: Optional[str] = None) -> str:
    """
    Get all iterations for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        timeframe (Optional[str]): A filter for which iterations are returned based on relative time. Only "current" is supported currently.

    Returns:
        str: JSON string containing all iterations for the team
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get iterations
        context = TeamContext(project=project_name, team=team_name)
        iterations = work_client.get_team_iterations(team_context=context, timeframe=timeframe)

        # Format for display
        formatted_iterations = []
        for iteration in iterations:
            formatted_iteration = {
                "id": iteration.id,
                "name": iteration.name,
                "attributes": {
                    "start_date": iteration.attributes.start_date.isoformat()
                    if iteration.attributes.start_date
                    else None,
                    "finish_date": iteration.attributes.finish_date.isoformat()
                    if iteration.attributes.finish_date
                    else None,
                }
                if iteration.attributes
                else None,
                "url": iteration.url,
            }
            formatted_iterations.append(formatted_iteration)

        return json.dumps(formatted_iterations, indent=2)
    except Exception as e:
        return f"Error retrieving team iterations: {str(e)}"


@tool
def get_team_current_iteration(project_name: str, team_name: str) -> str:
    """
    Get the current iteration for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing the current iteration details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current iteration
        context = TeamContext(project=project_name, team=team_name)
        iterations = work_client.get_team_iterations(team_context=context, timeframe="current")

        if not iterations:
            return json.dumps({"message": "No current iteration found"})

        iteration = iterations[0] if iterations else None

        if not iteration:
            return json.dumps({"message": "No current iteration found"})

        # Format for display
        formatted_iteration = {
            "id": iteration.id,
            "name": iteration.name,
            "path": iteration.path,
            "attributes": {
                "start_date": iteration.attributes.start_date.isoformat()
                if iteration.attributes.start_date
                else None,
                "finish_date": iteration.attributes.finish_date.isoformat()
                if iteration.attributes.finish_date
                else None,
                "time_frame": iteration.attributes.time_frame,
            }
            if iteration.attributes
            else None,
            "url": iteration.url,
        }

        return json.dumps(formatted_iteration, indent=2)
    except Exception as e:
        return f"Error retrieving current iteration: {str(e)}"


@tool
def add_team_iteration(project_name: str, team_name: str, iteration_id: str) -> str:
    """
    Add an iteration to a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        iteration_id (str): The ID of the iteration to add

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Add iteration
        team_iteration = work_client.post_team_iteration(
            {"id": iteration_id}, team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_iteration = {
            "id": team_iteration.id,
            "name": team_iteration.name,
            "path": team_iteration.path,
            "attributes": {
                "start_date": team_iteration.attributes.start_date.isoformat()
                if team_iteration.attributes.start_date
                else None,
                "finish_date": team_iteration.attributes.finish_date.isoformat()
                if team_iteration.attributes.finish_date
                else None,
                "time_frame": team_iteration.attributes.time_frame,
            }
            if team_iteration.attributes
            else None,
            "url": team_iteration.url,
        }

        return json.dumps(formatted_iteration, indent=2)
    except Exception as e:
        return f"Error adding team iteration: {str(e)}"


@tool
def remove_team_iteration(project_name: str, team_name: str, iteration_id: str) -> str:
    """
    Remove an iteration from a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        iteration_id (str): The ID of the iteration to remove

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Remove iteration
        work_client.delete_team_iteration(
            team_context={"project": project_name, "team": team_name}, id=iteration_id
        )

        return json.dumps({"message": f"Iteration {iteration_id} removed from team {team_name}"})
    except Exception as e:
        return f"Error removing team iteration: {str(e)}"


@tool
def get_project_iterations(project_name: str) -> str:
    """
    Get all iterations for a project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: JSON string containing all iterations for the project
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get iterations
        iterations = work_client.get_iterations(project=project_name)

        # Format for display
        formatted_iterations = []
        for iteration in iterations:
            formatted_iteration = {
                "id": iteration.id,
                "name": iteration.name,
                "path": iteration.path,
                "attributes": {
                    "start_date": iteration.attributes.start_date.isoformat()
                    if iteration.attributes.start_date
                    else None,
                    "finish_date": iteration.attributes.finish_date.isoformat()
                    if iteration.attributes.finish_date
                    else None,
                }
                if iteration.attributes
                else None,
                "url": iteration.url,
            }
            formatted_iterations.append(formatted_iteration)

        return json.dumps(formatted_iterations, indent=2)
    except Exception as e:
        return f"Error retrieving project iterations: {str(e)}"


@tool
def create_iteration(
    project_name: str,
    name: str,
    start_date: Optional[str] = None,
    finish_date: Optional[str] = None,
    path: Optional[str] = None,
) -> str:
    """
    Create a new iteration in a project.

    Args:
        project_name (str): The name of the project
        name (str): The name of the iteration
        start_date (str, optional): The start date of the iteration (ISO format: YYYY-MM-DD)
        finish_date (str, optional): The finish date of the iteration (ISO format: YYYY-MM-DD)
        path (str, optional): The path for the iteration (e.g., "\\ProjectName\\Iteration\\Release1")

    Returns:
        str: JSON string containing the created iteration details
    """
    try:
        # Prepare attributes if dates are provided
        attributes = None
        if start_date or finish_date:
            attributes = {}
            if start_date:
                attributes["startDate"] = start_date
            if finish_date:
                attributes["finishDate"] = finish_date

        client = get_azure_devops_client()
        wit_client = client.get_client("work_item_tracking")

        # Create the node data
        from azure.devops.v7_1.work_item_tracking.models import WorkItemClassificationNode

        node = WorkItemClassificationNode(name=name, structure_type="iteration")
        # Add attributes if provided
        if attributes:
            node.attributes = attributes

        return wit_client.create_or_update_classification_node(
            posted_node=node, project=project_name, structure_group="iterations", path=path
        )
    except Exception as e:
        return f"Error creating iteration: {str(e)}"


@tool
def get_team_backlog(project_name: str, team_name: str) -> str:
    """
    Get the backlog configuration for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing the team's backlog configuration
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get backlog configuration
        backlog_config = work_client.get_backlog_configurations(
            team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_config = {
            "backlog_fields": {
                "type_fields": {
                    field.reference_name: field.name
                    for field in backlog_config.backlog_fields.type_fields
                }
            }
            if backlog_config.backlog_fields
            else None,
            "backlogs": [
                {
                    "id": backlog.id,
                    "name": backlog.name,
                    "work_item_types": [
                        {"name": wit.name, "reference_name": wit.reference_name}
                        for wit in backlog.work_item_types
                    ]
                    if backlog.work_item_types
                    else [],
                }
                for backlog in backlog_config.backlogs
            ]
            if backlog_config.backlogs
            else [],
            "portfolio_backlogs": [
                {
                    "id": backlog.id,
                    "name": backlog.name,
                    "work_item_types": [
                        {"name": wit.name, "reference_name": wit.reference_name}
                        for wit in backlog.work_item_types
                    ]
                    if backlog.work_item_types
                    else [],
                }
                for backlog in backlog_config.portfolio_backlogs
            ]
            if backlog_config.portfolio_backlogs
            else [],
            "requirement_backlog": {
                "id": backlog_config.requirement_backlog.id,
                "name": backlog_config.requirement_backlog.name,
                "work_item_types": [
                    {"name": wit.name, "reference_name": wit.reference_name}
                    for wit in backlog_config.requirement_backlog.work_item_types
                ]
                if backlog_config.requirement_backlog.work_item_types
                else [],
            }
            if backlog_config.requirement_backlog
            else None,
        }

        return json.dumps(formatted_config, indent=2)
    except Exception as e:
        return f"Error retrieving team backlog configuration: {str(e)}"


@tool
def get_team_settings(project_name: str, team_name: str) -> str:
    """
    Get the settings for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing the team's settings
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get team settings
        team_settings = work_client.get_team_settings(
            team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_settings = {
            "backlog_iteration": {
                "id": team_settings.backlog_iteration.id,
                "name": team_settings.backlog_iteration.name,
                "path": team_settings.backlog_iteration.path,
            }
            if team_settings.backlog_iteration
            else None,
            "backlog_visibilities": team_settings.backlog_visibilities,
            "bugs_behavior": team_settings.bugs_behavior,
            "default_iteration": {
                "id": team_settings.default_iteration.id,
                "name": team_settings.default_iteration.name,
                "path": team_settings.default_iteration.path,
            }
            if team_settings.default_iteration
            else None,
            "working_days": team_settings.working_days,
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error retrieving team settings: {str(e)}"


@tool
def update_team_settings(
    project_name: str,
    team_name: str,
    backlog_iteration_id: Optional[str] = None,
    default_iteration_id: Optional[str] = None,
    bugs_behavior: Optional[str] = None,
    working_days: Optional[List[str]] = None,
    backlog_visibilities: Optional[Dict[str, bool]] = None,
) -> str:
    """
    Update settings for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        backlog_iteration_id (str, optional): The ID of the backlog iteration
        default_iteration_id (str, optional): The ID of the default iteration
        bugs_behavior (str, optional): How bugs are tracked (e.g., "asRequirements", "asTasks", "off")
        working_days (List[str], optional): List of working days (e.g., ["monday", "tuesday"])
        backlog_visibilities (Dict[str, bool], optional): Visibility settings for backlogs

    Returns:
        str: JSON string containing the updated team settings
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current settings
        current_settings = work_client.get_team_settings(
            team_context={"project": project_name, "team": team_name}
        )

        # Create patch document
        patch = {}

        if backlog_iteration_id:
            patch["backlogIteration"] = {"id": backlog_iteration_id}

        if default_iteration_id:
            patch["defaultIteration"] = {"id": default_iteration_id}

        if bugs_behavior:
            patch["bugsBehavior"] = bugs_behavior

        if working_days:
            patch["workingDays"] = working_days

        if backlog_visibilities:
            patch["backlogVisibilities"] = backlog_visibilities

        # Update settings
        updated_settings = work_client.update_team_settings(
            patch, team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_settings = {
            "backlog_iteration": {
                "id": updated_settings.backlog_iteration.id,
                "name": updated_settings.backlog_iteration.name,
                "path": updated_settings.backlog_iteration.path,
            }
            if updated_settings.backlog_iteration
            else None,
            "backlog_visibilities": updated_settings.backlog_visibilities,
            "bugs_behavior": updated_settings.bugs_behavior,
            "default_iteration": {
                "id": updated_settings.default_iteration.id,
                "name": updated_settings.default_iteration.name,
                "path": updated_settings.default_iteration.path,
            }
            if updated_settings.default_iteration
            else None,
            "working_days": updated_settings.working_days,
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error updating team settings: {str(e)}"


@tool
def get_team_board(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get details for a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing the board details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board
        board = work_client.get_board(
            team_context={"project": project_name, "team": team_name}, board=board_name
        )

        # Format for display
        formatted_board = {"id": board.id, "name": board.name, "url": board.url}

        return json.dumps(formatted_board, indent=2)
    except Exception as e:
        return f"Error retrieving team board: {str(e)}"


@tool
def get_team_boards(project_name: str, team_name: str) -> str:
    """
    Get all boards for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing all boards for the team
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get boards
        boards = work_client.get_boards(team_context={"project": project_name, "team": team_name})

        # Format for display
        formatted_boards = []
        for board in boards:
            formatted_boards.append({"id": board.id, "name": board.name, "url": board.url})

        return json.dumps(formatted_boards, indent=2)
    except Exception as e:
        return f"Error retrieving team boards: {str(e)}"


@tool
def get_board_columns(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get columns for a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing the board columns
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board columns
        columns = work_client.get_columns(
            team_context={"project": project_name, "team": team_name}, board=board_name
        )

        # Format for display
        formatted_columns = []
        for column in columns:
            formatted_columns.append(
                {
                    "id": column.id,
                    "name": column.name,
                    "order": column.order,
                    "stateMappings": column.state_mappings,
                    "itemLimit": column.item_limit,
                    "columnType": column.column_type,
                }
            )

        return json.dumps(formatted_columns, indent=2)
    except Exception as e:
        return f"Error retrieving board columns: {str(e)}"


@tool
def get_board_work_items(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get work items on a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing the work items on the board
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board work items
        board_items = work_client.get_board_card_settings(
            team_context={"project": project_name, "team": team_name}, board=board_name
        )

        # Format for display
        formatted_board_items = {
            "cards": {
                "card_rules": [
                    {
                        "rule": rule.rule,
                        "state": rule.state,
                        "filter": rule.filter,
                    }
                    for rule in board_items.cards.card_rules
                ]
                if board_items.cards.card_rules
                else [],
                "card_settings": [
                    {
                        "background_color": cs.background_color,
                        "title_color": cs.title_color,
                        "is_enabled": cs.is_enabled,
                        "tag": cs.tag,
                    }
                    for cs in board_items.cards.card_settings
                ]
                if board_items.cards.card_settings
                else [],
            }
            if board_items.cards
            else {}
        }

        return json.dumps(formatted_board_items, indent=2)
    except Exception as e:
        return f"Error retrieving board work items: {str(e)}"


@tool
def get_team_capacity(project_name: str, team_name: str, iteration_id: str) -> str:
    """
    Get capacity for a team for a specific iteration.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        iteration_id (str): The ID of the iteration

    Returns:
        str: JSON string containing the team capacity
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get team capacity
        capacities = work_client.get_capacities(
            team_context={"project": project_name, "team": team_name}, iteration_id=iteration_id
        )

        # Format for display
        formatted_capacities = []
        for capacity in capacities:
            formatted_capacities.append(
                {
                    "team_member": {
                        "id": capacity.team_member.id,
                        "display_name": capacity.team_member.display_name,
                        "unique_name": capacity.team_member.unique_name,
                    }
                    if capacity.team_member
                    else None,
                    "activities": [
                        {"capacity_per_day": activity.capacity_per_day, "name": activity.name}
                        for activity in capacity.activities
                    ]
                    if capacity.activities
                    else [],
                    "days_off": [
                        {
                            "start": day_off.start.isoformat() if day_off.start else None,
                            "end": day_off.end.isoformat() if day_off.end else None,
                        }
                        for day_off in capacity.days_off
                    ]
                    if capacity.days_off
                    else [],
                }
            )

        return json.dumps(formatted_capacities, indent=2)
    except Exception as e:
        return f"Error retrieving team capacity: {str(e)}"


@tool
def get_iteration_work_items(project_name: str, team_name: str, iteration_id: str) -> str:
    """
    Get work items in a specific iteration for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        iteration_id (str): The ID of the iteration

    Returns:
        str: JSON string containing the work items in the iteration
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")
        wit_client = client.get_client("work_item_tracking")

        # Get iteration work items
        work_item_refs = work_client.get_iteration_work_items(
            team_context={"project": project_name, "team": team_name}, iteration_id=iteration_id
        )

        if not work_item_refs or not work_item_refs.work_item_relations:
            return json.dumps({"count": 0, "work_items": []})

        # Get work item IDs
        work_item_ids = [relation.target.id for relation in work_item_refs.work_item_relations]

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
        return f"Error retrieving iteration work items: {str(e)}"


@tool
def get_backlogs(project_name: str, team_name: str) -> str:
    """
    Get all backlogs for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing all backlogs for the team
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get backlogs
        backlogs = work_client.get_backlogs(
            team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_backlogs = []
        for backlog in backlogs:
            formatted_backlog = {
                "id": backlog.id,
                "name": backlog.name,
                "rank": backlog.rank,
                "is_hidden": backlog.is_hidden,
                "category_reference_name": backlog.category_reference_name,
                "url": backlog.url,
            }
            formatted_backlogs.append(formatted_backlog)

        return json.dumps(formatted_backlogs, indent=2)
    except Exception as e:
        return f"Error retrieving team backlogs: {str(e)}"


@tool
def get_backlog_items(project_name: str, team_name: str, backlog_id: str) -> str:
    """
    Get work items in a specified backlog.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        backlog_id (str): The ID of the backlog

    Returns:
        str: JSON string containing the work items in the backlog
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")
        wit_client = client.get_client("work_item_tracking")

        # Get backlog work items
        backlog_work_items = work_client.get_backlog_level_work_items(
            team_context={"project": project_name, "team": team_name}, backlog_id=backlog_id
        )

        if not backlog_work_items.work_items:
            return json.dumps({"count": 0, "work_items": []})

        # Get work item IDs
        work_item_ids = [
            item.target.id for item in backlog_work_items.work_items if hasattr(item, "target")
        ]

        if not work_item_ids:
            return json.dumps({"count": 0, "work_items": []})

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
        return f"Error retrieving backlog items: {str(e)}"


@tool
def get_single_backlog(project_name: str, team_name: str, backlog_id: str) -> str:
    """
    Get details for a specific backlog.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        backlog_id (str): The ID of the backlog

    Returns:
        str: JSON string containing the backlog details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get backlog
        backlog = work_client.get_backlog(
            team_context={"project": project_name, "team": team_name}, id=backlog_id
        )

        # Format for display
        formatted_backlog = {
            "id": backlog.id,
            "name": backlog.name,
            "rank": backlog.rank,
            "is_hidden": backlog.is_hidden,
            "category_reference_name": backlog.category_reference_name,
            "work_item_types": [
                {"name": wit.name, "reference_name": wit.reference_name}
                for wit in backlog.work_item_types
            ]
            if backlog.work_item_types
            else [],
            "url": backlog.url,
        }

        return json.dumps(formatted_backlog, indent=2)
    except Exception as e:
        return f"Error retrieving backlog details: {str(e)}"


@tool
def get_backlog_levels(project_name: str, team_name: str) -> str:
    """
    Get all backlog levels for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team

    Returns:
        str: JSON string containing all backlog levels for the team
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get backlog configuration
        backlog_config = work_client.get_backlog_configurations(
            team_context={"project": project_name, "team": team_name}
        )

        # Format the portfolio backlogs (levels)
        formatted_levels = []

        # Add requirement backlog (typically user stories/PBIs)
        if backlog_config.requirement_backlog:
            formatted_levels.append(
                {
                    "id": backlog_config.requirement_backlog.id,
                    "name": backlog_config.requirement_backlog.name,
                    "rank": 0,  # Lowest level
                    "is_default": True,
                    "work_item_types": [
                        {"name": wit.name, "reference_name": wit.reference_name}
                        for wit in backlog_config.requirement_backlog.work_item_types
                    ]
                    if backlog_config.requirement_backlog.work_item_types
                    else [],
                }
            )

        # Add portfolio backlogs (like features, epics)
        if backlog_config.portfolio_backlogs:
            for i, backlog in enumerate(backlog_config.portfolio_backlogs):
                formatted_levels.append(
                    {
                        "id": backlog.id,
                        "name": backlog.name,
                        "rank": i + 1,  # Higher levels
                        "is_default": False,
                        "work_item_types": [
                            {"name": wit.name, "reference_name": wit.reference_name}
                            for wit in backlog.work_item_types
                        ]
                        if backlog.work_item_types
                        else [],
                    }
                )

        return json.dumps(formatted_levels, indent=2)
    except Exception as e:
        return f"Error retrieving backlog levels: {str(e)}"


@tool
def update_backlog_item_position(
    project_name: str,
    team_name: str,
    work_item_id: int,
    successor_id: Optional[int] = None,
    predecessor_id: Optional[int] = None,
) -> str:
    """
    Update the position of a work item in the backlog.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        work_item_id (int): The ID of the work item to reposition
        successor_id (int, optional): The ID of the work item that should come after the repositioned item
        predecessor_id (int, optional): The ID of the work item that should come before the repositioned item

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Validate input
        if successor_id is None and predecessor_id is None:
            return "Error: Either successor_id or predecessor_id must be provided"

        # Create position object
        position = {}
        if successor_id:
            position["successorId"] = successor_id
        if predecessor_id:
            position["predecessorId"] = predecessor_id

        # Update position
        result = work_client.update_work_item_position(
            position=position,
            team_context={"project": project_name, "team": team_name},
            id=work_item_id,
        )

        # Format for display
        formatted_result = {
            "id": result.id,
            "url": result.url,
            "message": f"Work item {work_item_id} repositioned successfully",
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error updating work item position: {str(e)}"


@tool
def get_backlog_work_items_with_hierarchy(
    project_name: str, team_name: str, backlog_id: str
) -> str:
    """
    Get work items in a backlog with their hierarchy.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        backlog_id (str): The ID of the backlog

    Returns:
        str: JSON string containing the work items with their hierarchy
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get backlog work items with hierarchy
        backlog_work_items = work_client.get_backlog_level_work_items(
            team_context={"project": project_name, "team": team_name}, backlog_id=backlog_id
        )

        if not backlog_work_items or not backlog_work_items.work_items:
            return json.dumps({"count": 0, "work_items": []})

        # Format for display
        formatted_structure = []

        # Process top-level items and their children
        for backlog_item in backlog_work_items.work_items:
            # Skip if no target (shouldn't happen, but just in case)
            if not hasattr(backlog_item, "target"):
                continue

            target = backlog_item.target
            formatted_item = {"id": target.id, "url": target.url, "children": []}

            # Add children if any
            if hasattr(backlog_item, "children") and backlog_item.children:
                for child in backlog_item.children:
                    if hasattr(child, "target"):
                        formatted_item["children"].append(
                            {"id": child.target.id, "url": child.target.url}
                        )

            formatted_structure.append(formatted_item)

        return json.dumps(
            {"count": len(formatted_structure), "work_items": formatted_structure}, indent=2
        )
    except Exception as e:
        return f"Error retrieving backlog items with hierarchy: {str(e)}"


@tool
def update_board_columns(
    project_name: str,
    team_name: str,
    board_name: str,
    columns: List[Dict[str, Any]],
) -> str:
    """
    Update columns for a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board
        columns (List[Dict[str, Any]]): List of column definitions to update
            Each column should include: name, order, and optionally itemLimit, stateMappings, columnType

    Returns:
        str: JSON string containing the updated board columns
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Update board columns
        updated_columns = work_client.update_columns(
            columns,
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_columns = []
        for column in updated_columns:
            formatted_columns.append(
                {
                    "id": column.id,
                    "name": column.name,
                    "order": column.order,
                    "stateMappings": column.state_mappings,
                    "itemLimit": column.item_limit,
                    "columnType": column.column_type,
                }
            )

        return json.dumps(formatted_columns, indent=2)
    except Exception as e:
        return f"Error updating board columns: {str(e)}"


@tool
def update_board_card_settings(
    project_name: str,
    team_name: str,
    board_name: str,
    card_settings: Dict[str, Any],
) -> str:
    """
    Update card settings for a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board
        card_settings (Dict[str, Any]): Card settings to update, may include card_rules and card_settings lists

    Returns:
        str: JSON string containing the updated card settings
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Update board card settings
        updated_settings = work_client.update_board_card_settings(
            card_settings,
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_settings = {
            "cards": {
                "card_rules": [
                    {
                        "rule": rule.rule,
                        "state": rule.state,
                        "filter": rule.filter,
                    }
                    for rule in updated_settings.cards.card_rules
                ]
                if updated_settings.cards.card_rules
                else [],
                "card_settings": [
                    {
                        "background_color": cs.background_color,
                        "title_color": cs.title_color,
                        "is_enabled": cs.is_enabled,
                        "tag": cs.tag,
                    }
                    for cs in updated_settings.cards.card_settings
                ]
                if updated_settings.cards.card_settings
                else [],
            }
            if updated_settings.cards
            else {}
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error updating board card settings: {str(e)}"


@tool
def create_board(
    project_name: str,
    team_name: str,
    name: str,
    description: Optional[str] = None,
) -> str:
    """
    Create a new board for a team.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        name (str): The name of the new board
        description (str, optional): The description of the board

    Returns:
        str: JSON string containing the created board details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Create board object
        board_data = {"name": name}
        if description:
            board_data["description"] = description

        # Create board
        created_board = work_client.create_board(
            board_data, team_context={"project": project_name, "team": team_name}
        )

        # Format for display
        formatted_board = {
            "id": created_board.id,
            "name": created_board.name,
            "url": created_board.url,
            "description": created_board.description,
        }

        return json.dumps(formatted_board, indent=2)
    except Exception as e:
        return f"Error creating board: {str(e)}"


@tool
def get_board_chart(
    project_name: str,
    team_name: str,
    board_name: str,
    chart_name: str,
) -> str:
    """
    Get a chart for a specific board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board
        chart_name (str): The name of the chart to retrieve

    Returns:
        str: JSON string containing the chart data
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board chart
        chart = work_client.get_chart(
            team_context={"project": project_name, "team": team_name},
            board=board_name,
            name=chart_name,
        )

        # Format for display
        formatted_chart = {
            "name": chart.name,
            "dimensions": chart.dimensions.__dict__ if chart.dimensions else None,
            "chart_type": chart.chart_type,
        }

        return json.dumps(formatted_chart, indent=2)
    except Exception as e:
        return f"Error retrieving board chart: {str(e)}"


@tool
def get_board_charts(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get all charts for a specific board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing all charts for the board
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board charts
        charts = work_client.get_charts(
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_charts = []
        for chart in charts:
            formatted_charts.append(
                {
                    "name": chart.name,
                    "dimensions": chart.dimensions.__dict__ if chart.dimensions else None,
                    "chart_type": chart.chart_type,
                }
            )

        return json.dumps(formatted_charts, indent=2)
    except Exception as e:
        return f"Error retrieving board charts: {str(e)}"


@tool
def get_card_field_settings(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get card field settings for a board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing the card field settings
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get card field settings
        settings = work_client.get_board_card_settings(
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_settings = {
            "cards": {
                "fields": [
                    {
                        "field_identifier": field.field_identifier,
                        "display_format": field.display_format,
                        "is_enabled": field.is_enabled,
                    }
                    for field in settings.cards.fields
                ]
                if settings.cards and settings.cards.fields
                else [],
            }
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error retrieving card field settings: {str(e)}"


@tool
def update_card_field_settings(
    project_name: str,
    team_name: str,
    board_name: str,
    field_settings: List[Dict[str, Any]],
) -> str:
    """
    Update card field settings for a board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board
        field_settings (List[Dict[str, Any]]): List of field settings to update
            Each setting should include: fieldIdentifier, displayFormat, isEnabled

    Returns:
        str: JSON string containing the updated card field settings
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Prepare settings object
        settings_data = {"cards": {"fields": field_settings}}

        # Update card field settings
        updated_settings = work_client.update_board_card_settings(
            settings_data,
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_settings = {
            "cards": {
                "fields": [
                    {
                        "field_identifier": field.field_identifier,
                        "display_format": field.display_format,
                        "is_enabled": field.is_enabled,
                    }
                    for field in updated_settings.cards.fields
                ]
                if updated_settings.cards and updated_settings.cards.fields
                else [],
            }
        }

        return json.dumps(formatted_settings, indent=2)
    except Exception as e:
        return f"Error updating card field settings: {str(e)}"


@tool
def get_board_rows(project_name: str, team_name: str, board_name: str) -> str:
    """
    Get rows for a team board (swimlanes).

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board

    Returns:
        str: JSON string containing the board rows (swimlanes)
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get board rows
        rows = work_client.get_rows(
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_rows = []
        for row in rows:
            formatted_rows.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "color": row.color,
                }
            )

        return json.dumps(formatted_rows, indent=2)
    except Exception as e:
        return f"Error retrieving board rows: {str(e)}"


@tool
def update_board_rows(
    project_name: str,
    team_name: str,
    board_name: str,
    rows: List[Dict[str, Any]],
) -> str:
    """
    Update rows (swimlanes) for a team board.

    Args:
        project_name (str): The name of the project
        team_name (str): The name of the team
        board_name (str): The name of the board
        rows (List[Dict[str, Any]]): List of row definitions to update
            Each row should include: id, name, and optionally color

    Returns:
        str: JSON string containing the updated board rows
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Update board rows
        updated_rows = work_client.update_rows(
            rows,
            team_context={"project": project_name, "team": team_name},
            board=board_name,
        )

        # Format for display
        formatted_rows = []
        for row in updated_rows:
            formatted_rows.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "color": row.color,
                }
            )

        return json.dumps(formatted_rows, indent=2)
    except Exception as e:
        return f"Error updating board rows: {str(e)}"


@tool
def get_plans(project_name: str) -> str:
    """
    Get all delivery plans for a project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: JSON string containing all delivery plans
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get all plans
        plans = work_client.get_plans(project=project_name)

        # Format for display
        formatted_plans = []
        for plan in plans:
            formatted_plan = {
                "id": plan.id,
                "name": plan.name,
                "type": plan.type,
                "creation_date": plan.creation_date.isoformat() if plan.creation_date else None,
                "description": plan.description,
                "modified_by": {
                    "id": plan.modified_by.id,
                    "display_name": plan.modified_by.display_name,
                }
                if plan.modified_by
                else None,
                "modified_date": plan.modified_date.isoformat() if plan.modified_date else None,
                "properties": plan.properties,
                "url": plan.url,
            }
            formatted_plans.append(formatted_plan)

        return json.dumps(formatted_plans, indent=2)
    except Exception as e:
        return f"Error retrieving plans: {str(e)}"


@tool
def get_plan(project_name: str, plan_id: str) -> str:
    """
    Get a specific delivery plan by ID.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan

    Returns:
        str: JSON string containing the plan details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get plan
        plan = work_client.get_plan(project=project_name, plan_id=plan_id)

        # Format for display
        formatted_plan = {
            "id": plan.id,
            "name": plan.name,
            "type": plan.type,
            "creation_date": plan.creation_date.isoformat() if plan.creation_date else None,
            "created_by": {
                "id": plan.created_by.id,
                "display_name": plan.created_by.display_name,
            }
            if plan.created_by
            else None,
            "description": plan.description,
            "modified_by": {
                "id": plan.modified_by.id,
                "display_name": plan.modified_by.display_name,
            }
            if plan.modified_by
            else None,
            "modified_date": plan.modified_date.isoformat() if plan.modified_date else None,
            "properties": plan.properties,
            "url": plan.url,
        }

        return json.dumps(formatted_plan, indent=2)
    except Exception as e:
        return f"Error retrieving plan: {str(e)}"


@tool
def create_plan(
    project_name: str,
    name: str,
    description: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new delivery plan.

    Args:
        project_name (str): The name of the project
        name (str): The name of the plan
        description (Optional[str]): The description of the plan
        properties (Optional[Dict[str, Any]]): Additional properties for the plan

    Returns:
        str: JSON string containing the created plan details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Create plan object
        plan_data = {
            "name": name,
            "type": "DeliveryTimelineView",  # Default type for delivery plans
        }

        if description:
            plan_data["description"] = description

        if properties:
            plan_data["properties"] = properties

        # Create plan
        created_plan = work_client.create_plan(plan_data, project=project_name)

        # Format for display
        formatted_plan = {
            "id": created_plan.id,
            "name": created_plan.name,
            "type": created_plan.type,
            "creation_date": created_plan.creation_date.isoformat()
            if created_plan.creation_date
            else None,
            "description": created_plan.description,
            "url": created_plan.url,
        }

        return json.dumps(formatted_plan, indent=2)
    except Exception as e:
        return f"Error creating plan: {str(e)}"


@tool
def update_plan(
    project_name: str,
    plan_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Update an existing delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan to update
        name (Optional[str]): The new name for the plan
        description (Optional[str]): The new description for the plan
        properties (Optional[Dict[str, Any]]): Updated properties for the plan

    Returns:
        str: JSON string containing the updated plan details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current plan
        current_plan = work_client.get_plan(project=project_name, plan_id=plan_id)

        # Create update object
        plan_data = {}

        if name:
            plan_data["name"] = name
        else:
            plan_data["name"] = current_plan.name

        if description is not None:
            plan_data["description"] = description
        elif current_plan.description:
            plan_data["description"] = current_plan.description

        if properties:
            plan_data["properties"] = properties
        elif current_plan.properties:
            plan_data["properties"] = current_plan.properties

        # Ensure type is preserved
        plan_data["type"] = current_plan.type

        # Update plan
        updated_plan = work_client.update_plan(plan_data, project=project_name, plan_id=plan_id)

        # Format for display
        formatted_plan = {
            "id": updated_plan.id,
            "name": updated_plan.name,
            "type": updated_plan.type,
            "description": updated_plan.description,
            "modified_date": updated_plan.modified_date.isoformat()
            if updated_plan.modified_date
            else None,
            "url": updated_plan.url,
        }

        return json.dumps(formatted_plan, indent=2)
    except Exception as e:
        return f"Error updating plan: {str(e)}"


@tool
def delete_plan(project_name: str, plan_id: str) -> str:
    """
    Delete a delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan to delete

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Delete the plan
        work_client.delete_plan(project=project_name, plan_id=plan_id)

        # Format for display
        formatted_result = {"message": f"Plan {plan_id} deleted successfully"}

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error deleting plan: {str(e)}"


@tool
def get_delivery_timeline_data(
    project_name: str,
    plan_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    Get the timeline data for a delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan
        start_date (Optional[str]): The start date for the timeline (ISO format: YYYY-MM-DD)
        end_date (Optional[str]): The end date for the timeline (ISO format: YYYY-MM-DD)

    Returns:
        str: JSON string containing the timeline data
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Prepare timeline request
        timeline_request = {}

        if start_date:
            timeline_request["startDate"] = start_date

        if end_date:
            timeline_request["endDate"] = end_date

        # Get timeline data
        timeline_data = work_client.get_delivery_timeline_data(
            project=project_name,
            plan_id=plan_id,
            timeline=timeline_request if timeline_request else None,
        )

        # Format for display
        formatted_data = {
            "start_date": timeline_data.start_date.isoformat()
            if timeline_data.start_date
            else None,
            "end_date": timeline_data.end_date.isoformat() if timeline_data.end_date else None,
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                    "iterations": [
                        {
                            "name": iteration.name,
                            "path": iteration.path,
                            "start_date": iteration.start_date.isoformat()
                            if iteration.start_date
                            else None,
                            "end_date": iteration.end_date.isoformat()
                            if iteration.end_date
                            else None,
                            "work_items": [
                                {
                                    "id": wi.id,
                                    "title": wi.name,
                                    "state": wi.state,
                                    "type": wi.type,
                                    "effort": wi.effort,
                                    "start_date": wi.start_date.isoformat()
                                    if wi.start_date
                                    else None,
                                    "end_date": wi.end_date.isoformat() if wi.end_date else None,
                                }
                                for wi in iteration.work_items
                            ]
                            if iteration.work_items
                            else [],
                        }
                        for iteration in team.iterations
                    ]
                    if team.iterations
                    else [],
                }
                for team in timeline_data.teams
            ]
            if timeline_data.teams
            else [],
        }

        return json.dumps(formatted_data, indent=2)
    except Exception as e:
        return f"Error retrieving delivery timeline data: {str(e)}"


@tool
def add_team_to_plan(project_name: str, plan_id: str, team_id: str) -> str:
    """
    Add a team to a delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan
        team_id (str): The ID of the team to add

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current plan to update its properties
        current_plan = work_client.get_plan(project=project_name, plan_id=plan_id)

        # If properties don't exist, create them
        properties = current_plan.properties if current_plan.properties else {}

        # Create or update the teams property
        if "teams" not in properties:
            properties["teams"] = []

        # Check if team already exists in the plan
        team_exists = False
        for team in properties["teams"]:
            if team.get("teamId") == team_id:
                team_exists = True
                break

        if not team_exists:
            properties["teams"].append({"teamId": team_id})

        # Update plan with new properties
        plan_data = {
            "name": current_plan.name,
            "type": current_plan.type,
            "properties": properties,
            "description": current_plan.description,
        }

        updated_plan = work_client.update_plan(plan_data, project=project_name, plan_id=plan_id)

        # Format for display
        formatted_result = {
            "id": updated_plan.id,
            "name": updated_plan.name,
            "message": f"Team {team_id} added to plan {plan_id}",
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error adding team to plan: {str(e)}"


@tool
def remove_team_from_plan(project_name: str, plan_id: str, team_id: str) -> str:
    """
    Remove a team from a delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan
        team_id (str): The ID of the team to remove

    Returns:
        str: JSON string containing the result of the operation
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current plan to update its properties
        current_plan = work_client.get_plan(project=project_name, plan_id=plan_id)

        # If properties don't exist or no teams, return early
        if not current_plan.properties or "teams" not in current_plan.properties:
            return json.dumps(
                {
                    "id": current_plan.id,
                    "name": current_plan.name,
                    "message": f"Team {team_id} not found in plan {plan_id}",
                },
                indent=2,
            )

        properties = current_plan.properties

        # Filter out the team to remove
        updated_teams = [team for team in properties["teams"] if team.get("teamId") != team_id]

        # If no team was removed, return early
        if len(updated_teams) == len(properties["teams"]):
            return json.dumps(
                {
                    "id": current_plan.id,
                    "name": current_plan.name,
                    "message": f"Team {team_id} not found in plan {plan_id}",
                },
                indent=2,
            )

        # Update the teams property
        properties["teams"] = updated_teams

        # Update plan with new properties
        plan_data = {
            "name": current_plan.name,
            "type": current_plan.type,
            "properties": properties,
            "description": current_plan.description,
        }

        updated_plan = work_client.update_plan(plan_data, project=project_name, plan_id=plan_id)

        # Format for display
        formatted_result = {
            "id": updated_plan.id,
            "name": updated_plan.name,
            "message": f"Team {team_id} removed from plan {plan_id}",
        }

        return json.dumps(formatted_result, indent=2)
    except Exception as e:
        return f"Error removing team from plan: {str(e)}"


@tool
def configure_plan_settings(
    project_name: str,
    plan_id: str,
    card_settings: Optional[Dict[str, Any]] = None,
    markers: Optional[List[Dict[str, Any]]] = None,
    field_criteria: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Configure the settings for a delivery plan.

    Args:
        project_name (str): The name of the project
        plan_id (str): The ID of the plan
        card_settings (Optional[Dict[str, Any]]): Settings for card display (fields, styles)
        markers (Optional[List[Dict[str, Any]]]): Timeline markers to display
        field_criteria (Optional[List[Dict[str, Any]]]): Work item field criteria for filtering

    Returns:
        str: JSON string containing the updated plan details
    """
    try:
        client = get_azure_devops_client()
        work_client = client.get_client("work")

        # Get current plan to update its properties
        current_plan = work_client.get_plan(project=project_name, plan_id=plan_id)

        # If properties don't exist, create them
        properties = current_plan.properties if current_plan.properties else {}

        # Update card settings if provided
        if card_settings:
            properties["cardSettings"] = card_settings

        # Update markers if provided
        if markers:
            properties["markers"] = markers

        # Update field criteria if provided
        if field_criteria:
            properties["fieldCriteria"] = field_criteria

        # Update plan with new properties
        plan_data = {
            "name": current_plan.name,
            "type": current_plan.type,
            "properties": properties,
            "description": current_plan.description,
        }

        updated_plan = work_client.update_plan(plan_data, project=project_name, plan_id=plan_id)

        # Format for display
        formatted_plan = {
            "id": updated_plan.id,
            "name": updated_plan.name,
            "type": updated_plan.type,
            "description": updated_plan.description,
            "properties": updated_plan.properties,
            "url": updated_plan.url,
        }

        return json.dumps(formatted_plan, indent=2)
    except Exception as e:
        return f"Error configuring plan settings: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
work_tools = [
    get_team_iterations,
    get_team_current_iteration,
    add_team_iteration,
    remove_team_iteration,
    get_project_iterations,
    create_iteration,
    get_team_backlog,
    get_team_settings,
    update_team_settings,
    get_team_board,
    get_team_boards,
    get_board_columns,
    get_board_work_items,
    get_team_capacity,
    get_iteration_work_items,
    get_backlogs,
    get_backlog_items,
    get_single_backlog,
    get_backlog_levels,
    update_backlog_item_position,
    get_backlog_work_items_with_hierarchy,
    update_board_columns,
    update_board_card_settings,
    create_board,
    get_board_chart,
    get_board_charts,
    get_card_field_settings,
    update_card_field_settings,
    get_board_rows,
    update_board_rows,
    # New plan-related tools
    get_plans,
    get_plan,
    create_plan,
    update_plan,
    delete_plan,
    get_delivery_timeline_data,
    add_team_to_plan,
    remove_team_from_plan,
    configure_plan_settings,
]
