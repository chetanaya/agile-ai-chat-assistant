"""
Azure DevOps Git Repositories API Functions

This module provides tools for interacting with Azure DevOps Git repositories through the API.
"""

from typing import Any, Dict, List, Optional, Union
import json

from langchain_core.tools import BaseTool, tool

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_repositories(project_name: str) -> str:
    """
    Get all Git repositories in a project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: JSON string containing all repositories
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        repositories = git_client.get_repositories(project_name)

        # Format for display
        formatted_repos = []
        for repo in repositories:
            formatted_repos.append(
                {
                    "id": repo.id,
                    "name": repo.name,
                    "url": repo.url,
                    "default_branch": repo.default_branch,
                    "size": repo.size,
                    "web_url": repo.web_url,
                }
            )

        return json.dumps(formatted_repos, indent=2)
    except Exception as e:
        return f"Error retrieving repositories: {str(e)}"


@tool
def get_repository(project_name: str, repository_name: str) -> str:
    """
    Get details for a specific repository.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository

    Returns:
        str: JSON string containing repository details
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        repository = git_client.get_repository(repository_name, project_name)

        # Format for display
        formatted_repo = {
            "id": repository.id,
            "name": repository.name,
            "url": repository.url,
            "project": {"id": repository.project.id, "name": repository.project.name},
            "default_branch": repository.default_branch,
            "size": repository.size,
            "remote_url": repository.remote_url,
            "web_url": repository.web_url,
            "is_fork": repository.is_fork,
        }

        return json.dumps(formatted_repo, indent=2)
    except Exception as e:
        return f"Error retrieving repository: {str(e)}"


@tool
def create_repository(
    project_name: str, repository_name: str, description: Optional[str] = None
) -> str:
    """
    Create a new Git repository in a project.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository
        description (Optional[str]): The description of the repository

    Returns:
        str: JSON string containing the created repository details
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        # Create repository object
        repo_create = {"name": repository_name, "project": {"name": project_name}}

        # Add description if provided
        if description:
            repo_create["description"] = description

        # Create repository
        created_repo = git_client.create_repository(repo_create, project_name)

        # Format for display
        formatted_repo = {
            "id": created_repo.id,
            "name": created_repo.name,
            "url": created_repo.url,
            "project": {"id": created_repo.project.id, "name": created_repo.project.name},
            "default_branch": created_repo.default_branch,
            "size": created_repo.size,
            "remote_url": created_repo.remote_url,
            "web_url": created_repo.web_url,
        }

        return json.dumps(formatted_repo, indent=2)
    except Exception as e:
        return f"Error creating repository: {str(e)}"


@tool
def get_branches(
    project_name: str, repository_name: str, search_criteria: Optional[str] = None
) -> str:
    """
    Get branches in a repository, optionally filtered by search criteria.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository
        search_criteria (Optional[str]): Search criteria to filter branches

    Returns:
        str: JSON string containing branches
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        # Get branches
        branches = git_client.get_branches(repository_name, project_name, search_criteria)

        # Format for display
        formatted_branches = []
        for branch in branches:
            formatted_branches.append(
                {
                    "name": branch.name,
                    "object_id": branch.object_id,
                    "creator": {
                        "display_name": branch.creator.display_name,
                        "id": branch.creator.id,
                    }
                    if branch.creator
                    else None,
                    "is_base_version": branch.is_base_version,
                    "commit": {"commit_id": branch.commit.commit_id, "url": branch.commit.url}
                    if branch.commit
                    else None,
                }
            )

        return json.dumps(formatted_branches, indent=2)
    except Exception as e:
        return f"Error retrieving branches: {str(e)}"


@tool
def get_commits(
    project_name: str, repository_name: str, branch_name: Optional[str] = None, top: int = 20
) -> str:
    """
    Get commits in a repository, optionally filtered by branch name.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository
        branch_name (Optional[str]): Branch name to filter commits
        top (int, optional): Maximum number of commits to return

    Returns:
        str: JSON string containing commits
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        # Create search criteria
        search_criteria = None
        if branch_name:
            search_criteria = {"itemVersion": {"version": branch_name}}

        # Get commits
        commits = git_client.get_commits(
            repository_id=repository_name,
            project=project_name,
            search_criteria=search_criteria,
            top=top,
        )

        # Format for display
        formatted_commits = []
        for commit in commits:
            formatted_commits.append(
                {
                    "commit_id": commit.commit_id,
                    "author": {
                        "name": commit.author.name,
                        "email": commit.author.email,
                        "date": commit.author.date.isoformat() if commit.author.date else None,
                    },
                    "committer": {
                        "name": commit.committer.name,
                        "email": commit.committer.email,
                        "date": commit.committer.date.isoformat()
                        if commit.committer.date
                        else None,
                    },
                    "comment": commit.comment,
                    "url": commit.url,
                    "remote_url": commit.remote_url,
                }
            )

        return json.dumps(formatted_commits, indent=2)
    except Exception as e:
        return f"Error retrieving commits: {str(e)}"


@tool
def get_pull_requests(project_name: str, repository_name: str, status: str = "active") -> str:
    """
    Get pull requests in a repository.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository
        status (str, optional): Status filter. One of 'active', 'abandoned', 'completed', 'all'

    Returns:
        str: JSON string containing pull requests
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        # Validate status
        valid_statuses = {"active": 1, "abandoned": 2, "completed": 3, "all": 4}

        if status.lower() not in valid_statuses:
            return f"Invalid status: {status}. Must be one of {', '.join(valid_statuses.keys())}."

        # Create search criteria
        search_criteria = {
            "repository_id": repository_name,
            "status": valid_statuses[status.lower()],
        }

        # Get pull requests
        pull_requests = git_client.get_pull_requests(repository_name, search_criteria, project_name)

        # Format for display
        formatted_prs = []
        for pr in pull_requests:
            formatted_prs.append(
                {
                    "pull_request_id": pr.pull_request_id,
                    "title": pr.title,
                    "description": pr.description,
                    "status": pr.status,
                    "created_by": {
                        "display_name": pr.created_by.display_name,
                        "id": pr.created_by.id,
                    }
                    if pr.created_by
                    else None,
                    "creation_date": pr.creation_date.isoformat() if pr.creation_date else None,
                    "source_branch": pr.source_ref_name,
                    "target_branch": pr.target_ref_name,
                    "is_draft": pr.is_draft,
                    "url": pr.url,
                    "web_url": pr.web_url,
                }
            )

        return json.dumps(formatted_prs, indent=2)
    except Exception as e:
        return f"Error retrieving pull requests: {str(e)}"


@tool
def create_pull_request(
    project_name: str,
    repository_name: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: Optional[str] = None,
    reviewers: Optional[List[str]] = None,
    is_draft: bool = False,
) -> str:
    """
    Create a new pull request.

    Args:
        project_name (str): The name of the project
        repository_name (str): The name of the repository
        source_branch (str): Source branch name (should include 'refs/heads/' prefix if not provided)
        target_branch (str): Target branch name (should include 'refs/heads/' prefix if not provided)
        title (str): The title of the pull request
        description (Optional[str]): The description of the pull request
        reviewers (Optional[List[str]]): List of reviewer IDs to add
        is_draft (bool, optional): Whether this is a draft pull request

    Returns:
        str: JSON string containing the created pull request details
    """
    try:
        client = get_azure_devops_client()
        git_client = client.get_client("git")

        # Format branch names if needed
        if not source_branch.startswith("refs/heads/"):
            source_branch = f"refs/heads/{source_branch}"

        if not target_branch.startswith("refs/heads/"):
            target_branch = f"refs/heads/{target_branch}"

        # Create pull request object
        pr_create = {
            "sourceRefName": source_branch,
            "targetRefName": target_branch,
            "title": title,
            "isDraft": is_draft,
        }

        # Add description if provided
        if description:
            pr_create["description"] = description

        # Add reviewers if provided
        if reviewers:
            pr_create["reviewers"] = [{"id": reviewer_id} for reviewer_id in reviewers]

        # Create pull request
        created_pr = git_client.create_pull_request(pr_create, repository_name, project_name)

        # Format for display
        formatted_pr = {
            "pull_request_id": created_pr.pull_request_id,
            "title": created_pr.title,
            "description": created_pr.description,
            "status": created_pr.status,
            "created_by": {
                "display_name": created_pr.created_by.display_name,
                "id": created_pr.created_by.id,
            }
            if created_pr.created_by
            else None,
            "creation_date": created_pr.creation_date.isoformat()
            if created_pr.creation_date
            else None,
            "source_branch": created_pr.source_ref_name,
            "target_branch": created_pr.target_ref_name,
            "is_draft": created_pr.is_draft,
            "url": created_pr.url,
            "web_url": created_pr.web_url,
        }

        return json.dumps(formatted_pr, indent=2)
    except Exception as e:
        return f"Error creating pull request: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
git_tools = [
    get_repositories,
    get_repository,
    create_repository,
    get_branches,
    get_commits,
    get_pull_requests,
    create_pull_request,
]
