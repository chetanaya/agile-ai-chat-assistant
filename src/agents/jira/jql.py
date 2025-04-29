"""
JIRA JQL (Jira Query Language) API Functions

This module provides tools for working with JQL through the REST API.
It includes endpoints for autocomplete data, suggestions, parsing, and other JQL-specific operations.
"""

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
        str: Formatted JQL reference data information
    """
    client = get_jira_client()
    try:
        response = client.get("jql/autocompletedata")

        # Extract key information from the response
        jql_reserved_words = response.get("jqlReservedWords", [])
        visible_fields = response.get("visibleFieldNames", [])
        visible_functions = response.get("visibleFunctionNames", [])

        result = "JQL Reference Data:\n\n"

        # Reserved words
        result += "Reserved Words:\n"
        for word in jql_reserved_words:
            result += f"- {word}\n"
        result += "\n"

        # Fields
        result += f"Available Fields ({len(visible_fields)}):\n"
        for field in visible_fields[:10]:  # Limit to 10 fields for readability
            field_name = field.get("value", "Unknown")
            display_name = field.get("displayName", field_name)
            orderable = "Yes" if field.get("orderable") == "true" else "No"
            searchable = "Yes" if field.get("searchable") == "true" else "No"

            result += f"- {display_name} (Field: {field_name})\n"
            result += f"  Orderable: {orderable}, Searchable: {searchable}\n"

            operators = field.get("operators", [])
            if operators:
                result += f"  Operators: {', '.join(operators)}\n"

            result += "\n"

        if len(visible_fields) > 10:
            result += f"... and {len(visible_fields) - 10} more fields\n\n"

        # Functions
        result += f"Available Functions ({len(visible_functions)}):\n"
        for function in visible_functions[:10]:  # Limit to 10 functions for readability
            function_name = function.get("value", "Unknown")
            display_name = function.get("displayName", function_name)

            result += f"- {display_name} (Function: {function_name})\n"

        if len(visible_functions) > 10:
            result += f"... and {len(visible_functions) - 10} more functions\n"

        return result
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
        str: Filtered JQL reference data information
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

        # Extract key information from the response
        jql_reserved_words = response.get("jqlReservedWords", [])
        visible_fields = response.get("visibleFieldNames", [])
        visible_functions = response.get("visibleFunctionNames", [])

        result = "Filtered JQL Reference Data:\n\n"

        # Reserved words
        result += "Reserved Words:\n"
        for word in jql_reserved_words:
            result += f"- {word}\n"
        result += "\n"

        # Fields
        result += f"Fields ({len(visible_fields)}):\n"
        for field in visible_fields:
            field_name = field.get("value", "Unknown")
            display_name = field.get("displayName", field_name)
            orderable = "Yes" if field.get("orderable") == "true" else "No"
            searchable = "Yes" if field.get("searchable") == "true" else "No"

            result += f"- {display_name} (Field: {field_name})\n"
            result += f"  Orderable: {orderable}, Searchable: {searchable}\n"

            operators = field.get("operators", [])
            if operators:
                result += f"  Operators: {', '.join(operators)}\n"

            result += "\n"

        # Functions
        result += f"Functions ({len(visible_functions)}):\n"
        for function in visible_functions:
            function_name = function.get("value", "Unknown")
            display_name = function.get("displayName", function_name)

            result += f"- {display_name} (Function: {function_name})\n"

        return result
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
        str: Formatted autocomplete suggestions
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

        results = response.get("results", [])
        result = f"Autocomplete Suggestions for '{field_name}={field_value}':\n\n"

        if not results:
            return f"No suggestions found for '{field_name}={field_value}'"

        for suggestion in results:
            display_name = suggestion.get("displayName", "Unknown")
            value = suggestion.get("value", "Unknown")

            result += f"- {display_name} (Value: {value})\n"

        return result
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
        str: Sanitized JQL queries
    """
    client = get_jira_client()
    try:
        data = {"queries": queries}
        if account_id:
            data["accountId"] = account_id

        response = client.post("jql/sanitize", data)

        sanitized_queries = response.get("queries", [])
        result = "Sanitized JQL Queries:\n\n"

        for i, query_info in enumerate(sanitized_queries):
            initial_query = query_info.get("initialQuery", "Unknown")
            sanitized_query = query_info.get("sanitizedQuery", "Unknown")

            result += f"Query {i + 1}:\n"
            result += f"  Original: {initial_query}\n"
            result += f"  Sanitized: {sanitized_query}\n"

            errors = query_info.get("errors", {}).get("errorMessages", [])
            if errors:
                result += "  Errors:\n"
                for error in errors:
                    result += f"  - {error}\n"

            result += "\n"

        return result
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
        str: JQL queries with user identifiers converted to account IDs
    """
    client = get_jira_client()
    try:
        data = {"queries": queries}
        response = client.post("jql/pdcleaner", data)

        converted_queries = response.get("queryStrings", [])
        unknown_users = response.get("queriesWithUnknownUsers", [])

        result = "Converted JQL Queries:\n\n"

        for i, query in enumerate(converted_queries):
            result += f"Query {i + 1}:\n"
            result += f"  Converted: {query}\n\n"

        if unknown_users:
            result += "Queries with Unknown Users:\n"
            for i, unknown in enumerate(unknown_users):
                original = unknown.get("originalQuery", "Unknown")
                converted = unknown.get("convertedQuery", "Unknown")

                result += f"Query {i + 1}:\n"
                result += f"  Original: {original}\n"
                result += f"  Converted: {converted}\n\n"

        return result
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
        str: Detailed information about the parsed query structure
    """
    client = get_jira_client()
    try:
        data = {"queries": [query], "validation": validation_level}

        response = client.post("jql/parse", data)
        queries = response.get("queries", [])

        if not queries:
            return "Error parsing JQL query: No parse results returned"

        parsed = queries[0]

        result = f"Parse Results for JQL Query: {query}\n\n"

        # Check for errors
        errors = parsed.get("errors", [])
        if errors:
            result += "Errors:\n"
            for error in errors:
                result += f"- {error}\n"
            return result

        # Check if query was converted (typically for user identifiers)
        converted_query = parsed.get("convertedQuery")
        if converted_query:
            result += f"Converted Query: {converted_query}\n\n"

        # Get structure information if available
        structure = parsed.get("structure")
        if structure:
            result += "Query Structure:\n"
            result += format_jql_structure(structure, indent=2)

        return result
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
