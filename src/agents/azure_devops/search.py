"""
Azure DevOps Search API Integration

This module provides functionality to interact with the Azure DevOps Search API.
"""

from typing import Any, Dict, Optional

from azure.devops.v7_1.search.models import (
    CodeSearchRequest,
    WikiSearchRequest,
    WorkItemSearchRequest,
)

from agents.azure_devops.utils import get_azure_devops_client


def get_search_client():
    """
    Get the Azure DevOps Search client.

    Returns:
        Client: The Azure DevOps Search client
    """
    client = get_azure_devops_client()
    return client.get_client("search")


def search_code(
    search_text: str,
    project_name: Optional[str] = None,
    repository_name: Optional[str] = None,
    file_path: Optional[str] = None,
    file_extension: Optional[str] = None,
    top: int = 100,
    skip: int = 0,
    include_matching_content: bool = True,
) -> Dict[str, Any]:
    """
    Search code repositories.

    Args:
        search_text: The search text.
        project_name: The project name to scope the search to.
        repository_name: The repository name to scope the search to.
        file_path: The file path to scope the search to.
        file_extension: The file extension to scope the search to.
        top: The number of results to return.
        skip: The number of results to skip.
        include_matching_content: Whether to include matching content in the response.

    Returns:
        Dict: The search results.
    """
    try:
        client = get_search_client()

        # Build filters
        filters = {}
        if project_name:
            filters["Project"] = project_name
        if repository_name:
            filters["Repository"] = repository_name
        if file_path:
            filters["Path"] = file_path
        if file_extension:
            filters["Extension"] = file_extension

        search_request = CodeSearchRequest(
            search_text=search_text,
            filters=filters,
            top=top,
            skip=skip,
            include_matching_content=include_matching_content,
        )

        results = client.fetch_code_search_results(search_request)

        # Format the results
        formatted_results = {
            "count": results.count,
            "code_results": [],
            "continuation_token": results.continuation_token,
        }

        for result in results.results:
            code_result = {
                "file_name": result.file_name,
                "path": result.path,
                "repository": result.repository.name,
                "project": result.project.name,
                "matches": [],
            }

            if result.matches:
                for match in result.matches:
                    code_result["matches"].append(
                        {
                            "line_number": match.line_number,
                            "line_text": match.line_text,
                            "content": match.content,
                        }
                    )

            formatted_results["code_results"].append(code_result)

        return formatted_results
    except Exception as e:
        client = get_azure_devops_client()
        return {"error": client.handle_response_error(e)}


def search_work_items(
    search_text: str,
    project_name: Optional[str] = None,
    work_item_type: Optional[str] = None,
    state: Optional[str] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
    top: int = 100,
    skip: int = 0,
) -> Dict[str, Any]:
    """
    Search work items.

    Args:
        search_text: The search text.
        project_name: The project name to scope the search to.
        work_item_type: The work item type to scope the search to.
        state: The work item state to scope the search to.
        assigned_to: The assigned to filter.
        created_by: The created by filter.
        top: The number of results to return.
        skip: The number of results to skip.

    Returns:
        Dict: The search results.
    """
    try:
        client = get_search_client()

        # Build filters
        filters = {}
        if project_name:
            filters["Project"] = project_name
        if work_item_type:
            filters["Work Item Type"] = work_item_type
        if state:
            filters["State"] = state
        if assigned_to:
            filters["Assigned To"] = assigned_to
        if created_by:
            filters["Created By"] = created_by

        search_request = WorkItemSearchRequest(
            search_text=search_text, filters=filters, top=top, skip=skip
        )

        results = client.fetch_work_item_search_results(search_request)

        # Format the results
        formatted_results = {
            "count": results.count,
            "work_items": [],
            "continuation_token": results.continuation_token,
        }

        for result in results.results:
            work_item = {
                "id": result.id,
                "title": result.fields.get("System.Title", ""),
                "work_item_type": result.fields.get("System.WorkItemType", ""),
                "state": result.fields.get("System.State", ""),
                "assigned_to": result.fields.get("System.AssignedTo", {}).get("displayName", "")
                if result.fields.get("System.AssignedTo")
                else "",
                "project": result.project.name,
                "url": result.url,
            }

            formatted_results["work_items"].append(work_item)

        return formatted_results
    except Exception as e:
        client = get_azure_devops_client()
        return {"error": client.handle_response_error(e)}


def search_wiki(
    search_text: str,
    project_name: Optional[str] = None,
    wiki_name: Optional[str] = None,
    path: Optional[str] = None,
    top: int = 100,
    skip: int = 0,
    include_content: bool = True,
) -> Dict[str, Any]:
    """
    Search wiki pages.

    Args:
        search_text: The search text.
        project_name: The project name to scope the search to.
        wiki_name: The wiki name to scope the search to.
        path: The path to scope the search to.
        top: The number of results to return.
        skip: The number of results to skip.
        include_content: Whether to include content in the response.

    Returns:
        Dict: The search results.
    """
    try:
        client = get_search_client()

        # Build filters
        filters = {}
        if project_name:
            filters["Project"] = project_name
        if wiki_name:
            filters["Wiki"] = wiki_name
        if path:
            filters["Path"] = path

        search_request = WikiSearchRequest(
            search_text=search_text,
            filters=filters,
            top=top,
            skip=skip,
            include_content=include_content,
        )

        results = client.fetch_wiki_search_results(search_request)

        # Format the results
        formatted_results = {
            "count": results.count,
            "wiki_results": [],
            "continuation_token": results.continuation_token,
        }

        for result in results.results:
            wiki_result = {
                "title": result.title,
                "path": result.path,
                "wiki_name": result.wiki.name,
                "project": result.project.name,
                "url": result.url,
            }

            if include_content and result.content:
                wiki_result["content"] = result.content

            formatted_results["wiki_results"].append(wiki_result)

        return formatted_results
    except Exception as e:
        client = get_azure_devops_client()
        return {"error": client.handle_response_error(e)}
