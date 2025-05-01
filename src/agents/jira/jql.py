"""
JIRA JQL (Jira Query Language) API Functions

This module provides tools for working with JQL through the REST API.
It includes endpoints for autocomplete data, suggestions, parsing, and other JQL-specific operations.
"""

import json
from typing import Any

from langchain_core.tools import tool

from agents.jira.utils import get_jira_client


@tool
def get_field_reference_data() -> str:
    """
    Returns reference data for JQL searches.

    Useful for getting information about available fields, operators, and other JQL reference data.
    This data can be used to build JQL queries programmatically.

    Returns:
        str: JSON string with JQL reference data
    """
    client = get_jira_client()
    try:
        response = client.get("jql/autocompletedata")
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving JQL reference data: {str(e)}"


@tool
def post_field_reference_data(
    field_names: list[str] | None = None,
    function_names: list[str] | None = None,
    field_ids: list[str] | None = None,
) -> str:
    """
    Returns reference data for JQL searches using POST method.

    Useful for getting specific field or function information for JQL queries.
    This endpoint allows filtering of fields and functions using the POST method.

    Args:
        field_names (List[str], optional): List of field names to get reference data for
        function_names (List[str], optional): List of function names to get reference data for
        field_ids (List[str], optional): List of field IDs to get reference data for

    Returns:
        str: JSON string with filtered JQL reference data
    """
    client = get_jira_client()
    try:
        data = {}
        if field_names:
            data["fieldNames"] = field_names
        if function_names:
            data["functionNames"] = function_names
        if field_ids:
            data["fieldIds"] = field_ids

        response = client.post("jql/autocompletedata", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving filtered JQL reference data: {str(e)}"


@tool
def get_field_autocomplete_suggestions(
    field_name: str,
    field_value: str,
    predicates: list[str] | None = None,
) -> str:
    """
    Returns auto-complete suggestions for JQL field values.

    Useful for getting suggestions for field values when building JQL queries.

    Args:
        field_name (str): The name of the field to get suggestions for
        field_value (str): The partial field value to get suggestions for
        predicates (List[str], optional): List of predicates to filter the suggestions

    Returns:
        str: JSON string with autocomplete suggestions
    """
    client = get_jira_client()
    try:
        params = {
            "fieldName": field_name,
            "fieldValue": field_value,
        }

        if predicates:
            params["predicates"] = ",".join(predicates)

        response = client.get("jql/autocompletedata/suggestions", params=params)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error retrieving JQL autocomplete suggestions: {str(e)}"


@tool
def sanitize_jql_queries(
    queries: list[str],
    account_id: str | None = None,
) -> str:
    """
    Converts readable details in one or more JQL queries to IDs.

    Useful for sanitizing JQL queries when a user doesn't have permission to view the entity
    whose details are readable or to improve query performance.

    Args:
        queries (List[str]): A list of JQL queries to sanitize
        account_id (str, optional): The account ID of the user for which sanitization occurs

    Returns:
        str: JSON string with sanitized JQL queries
    """
    client = get_jira_client()
    try:
        data = {"queries": queries}
        if account_id:
            data["accountId"] = account_id

        response = client.post("jql/sanitize", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error sanitizing JQL queries: {str(e)}"


@tool
def convert_user_ids_in_jql(queries: list[str]) -> str:
    """
    Converts user identifiers to account IDs in JQL queries.

    Useful for converting legacy username or user key references to account IDs
    in JQL queries for better compatibility with Atlassian's new user identity system.

    Args:
        queries (List[str]): A list of JQL queries to convert

    Returns:
        str: JSON string with converted JQL queries
    """
    client = get_jira_client()
    try:
        data = {"queries": queries}
        response = client.post("jql/pdcleaner", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error converting user IDs in JQL queries: {str(e)}"


@tool
def parse_jql_query(query: str, validation_level: str = "strict") -> str:
    """
    Parses a JQL query and returns information about its structure.

    Useful for validating JQL queries and understanding their structure. This is more
    detailed than the multi-query parse function and returns structural information.

    Args:
        query (str): The JQL query to parse
        validation_level (str, optional): Validation level: "strict", "warn", or "none". Defaults to "strict".

    Returns:
        str: JSON string with parsed JQL query data
    """
    client = get_jira_client()
    try:
        data = {"queries": [query], "validation": validation_level}
        response = client.post("jql/parse", data)
        return json.dumps(response, sort_keys=True, indent=4, separators=(",", ": "))
    except Exception as e:
        return f"Error parsing JQL query: {str(e)}"


def format_jql_structure(structure: dict[str, Any], indent: int = 0) -> str:
    """Helper function to format JQL structure in a readable way"""
    result = ""
    prefix = " " * indent

    # Handle different node types
    node_type = structure.get("type", "unknown")

    if node_type == "fieldValueOperand":
        field = structure.get("field", {}).get("name", "Unknown field")
        operator = structure.get("operator", "Unknown operator")
        value = "Unknown value"

        # Handle different value types
        operand = structure.get("operand", {})
        if operand:
            if "value" in operand:
                value = operand["value"]
            elif "values" in operand:
                value = ", ".join([str(v) for v in operand.get("values", [])])

        result += f"{prefix}{field} {operator} {value}\n"

    elif node_type in ["andClause", "orClause"]:
        clauses = structure.get("clauses", [])
        operator = "AND" if node_type == "andClause" else "OR"

        if clauses:
            result += f"{prefix}({operator} conditions)\n"
            for clause in clauses:
                result += format_jql_structure(clause, indent + 2)

    elif node_type == "notClause":
        result += f"{prefix}NOT\n"
        if "clause" in structure:
            result += format_jql_structure(structure["clause"], indent + 2)

    elif node_type == "orderBy":
        fields = structure.get("fields", [])
        result += f"{prefix}ORDER BY\n"
        for field in fields:
            name = field.get("field", {}).get("name", "Unknown")
            direction = field.get("direction", "ASC")
            result += f"{prefix}  {name} {direction}\n"

    else:
        # Generic handler for other node types
        result += f"{prefix}[{node_type}]\n"

    return result


# Export the tools for use in the JIRA assistant
jql_tools = [
    get_field_reference_data,
    post_field_reference_data,
    get_field_autocomplete_suggestions,
    parse_jql_query,
    convert_user_ids_in_jql,
    sanitize_jql_queries,
]
