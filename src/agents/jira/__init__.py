"""
JIRA API Integration Module
"""

from agents.jira.backlog import backlog_tools
from agents.jira.boards import board_tools
from agents.jira.issue_comments import comment_tools
from agents.jira.issue_search import search_tools
from agents.jira.issue_types import issue_type_tools
from agents.jira.issue_worklogs import worklog_tools
from agents.jira.issues import issue_tools
from agents.jira.jql import jql_tools
from agents.jira.permissions import permission_tools
from agents.jira.projects import project_tools
from agents.jira.sprints import sprint_tools
from agents.jira.users import user_tools

# Consolidate all JIRA tools for easy import
# WARNING: This list exceeds OpenAI's limit of 128 tools per API call
# When using with OpenAI models, use a subset of these tools as done in jira_assistant.py
all_jira_tools = (
    issue_tools
    + comment_tools
    + search_tools
    + worklog_tools
    + jql_tools
    + permission_tools
    + project_tools
    + sprint_tools
    + user_tools
    + board_tools
    + backlog_tools
    + issue_type_tools
)
