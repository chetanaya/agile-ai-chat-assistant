"""
Azure DevOps Search Tools

This module defines tools for searching in Azure DevOps.
"""

from typing import Annotated

from langchain_core.tools import tool

from agents.azure_devops.search import search_code, search_wiki, search_work_items

search_tools = []


@tool
def search_code_repositories(
    search_text: str,
    project_name: str | None = None,
    repository_name: str | None = None,
    file_path: str | None = None,
    file_extension: str | None = None,
    top: Annotated[int, "Number of results to return"] = 100,
    skip: Annotated[int, "Number of results to skip"] = 0,
):
    """
    Search code repositories in Azure DevOps.

    Args:
        search_text: The text to search for in code.
        project_name: Optional. The name of the project to search in.
        repository_name: Optional. The name of the repository to search in.
        file_path: Optional. The file path to search in.
        file_extension: Optional. The file extension to search for (e.g., 'cs', 'js', 'py').
        top: Optional. Number of results to return (default: 100).
        skip: Optional. Number of results to skip (default: 0).

    Returns:
        Search results containing code matches.
    """
    return search_code(
        search_text=search_text,
        project_name=project_name,
        repository_name=repository_name,
        file_path=file_path,
        file_extension=file_extension,
        top=top,
        skip=skip,
        include_matching_content=True,
    )


@tool
def search_work_items_tool(
    search_text: str,
    project_name: str | None = None,
    work_item_type: str | None = None,
    state: str | None = None,
    assigned_to: str | None = None,
    created_by: str | None = None,
    top: Annotated[int, "Number of results to return"] = 100,
    skip: Annotated[int, "Number of results to skip"] = 0,
):
    """
    Search for work items in Azure DevOps.

    Args:
        search_text: The text to search for in work items.
        project_name: Optional. The name of the project to search in.
        work_item_type: Optional. The type of work item to search for (e.g., 'Bug', 'User Story').
        state: Optional. The state of the work item (e.g., 'Active', 'Closed').
        assigned_to: Optional. The name of the person the work item is assigned to.
        created_by: Optional. The name of the person who created the work item.
        top: Optional. Number of results to return (default: 100).
        skip: Optional. Number of results to skip (default: 0).

    Returns:
        Search results containing matching work items.
    """
    return search_work_items(
        search_text=search_text,
        project_name=project_name,
        work_item_type=work_item_type,
        state=state,
        assigned_to=assigned_to,
        created_by=created_by,
        top=top,
        skip=skip,
    )


@tool
def search_wiki_pages(
    search_text: str,
    project_name: str | None = None,
    wiki_name: str | None = None,
    path: str | None = None,
    top: Annotated[int, "Number of results to return"] = 100,
    skip: Annotated[int, "Number of results to skip"] = 0,
):
    """
    Search for wiki pages in Azure DevOps.

    Args:
        search_text: The text to search for in wiki pages.
        project_name: Optional. The name of the project to search in.
        wiki_name: Optional. The name of the wiki to search in.
        path: Optional. The path within the wiki to search in.
        top: Optional. Number of results to return (default: 100).
        skip: Optional. Number of results to skip (default: 0).

    Returns:
        Search results containing matching wiki pages.
    """
    return search_wiki(
        search_text=search_text,
        project_name=project_name,
        wiki_name=wiki_name,
        path=path,
        top=top,
        skip=skip,
        include_content=True,
    )


search_tools.append(search_code_repositories)
search_tools.append(search_work_items_tool)
search_tools.append(search_wiki_pages)
