"""
JIRA API Integration Utilities
"""

import base64
import json
import os
from typing import Any

import requests

from core import settings


class JiraApiClient:
    """
    A client for interacting with the JIRA REST API.
    """

    def __init__(self, api_base_path: str = "rest/api/3/"):
        """Initialize the JIRA API client with authentication details from environment variables."""
        self.jira_url = (
            settings.JIRA_URL.get_secret_value()
            if hasattr(settings, "JIRA_URL")
            else os.environ.get("JIRA_URL")
        )
        self.jira_email = (
            settings.JIRA_EMAIL.get_secret_value()
            if hasattr(settings, "JIRA_EMAIL")
            else os.environ.get("JIRA_EMAIL")
        )
        self.jira_api_token = (
            settings.JIRA_API_TOKEN.get_secret_value()
            if hasattr(settings, "JIRA_API_TOKEN")
            else os.environ.get("JIRA_API_TOKEN")
        )

        if not all([self.jira_url, self.jira_email, self.jira_api_token]):
            raise ValueError("JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be set")

        # Ensure JIRA URL ends with trailing slash
        if not self.jira_url.endswith("/"):
            self.jira_url += "/"

        # Base API path
        # self.api_base_path = "rest/api/3/"
        self.api_base_path = api_base_path

        # Encode authentication credentials
        auth_str = f"{self.jira_email}:{self.jira_api_token}"
        self.auth_header = base64.b64encode(auth_str.encode()).decode()

        # Common headers
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and convert to JSON, handling errors appropriately.

        Args:
            response (requests.Response): Response from API call

        Returns:
            Dict[str, Any]: Response as dictionary

        Raises:
            ValueError: If the response contains an error
        """
        try:
            if response.status_code >= 400:
                error_message = f"JIRA API Error - Status: {response.status_code}"
                try:
                    error_body = response.json()
                    if "errorMessages" in error_body:
                        error_message += f" - {', '.join(error_body['errorMessages'])}"
                    elif "message" in error_body:
                        error_message += f" - {error_body['message']}"
                except Exception:
                    error_message += f" - {response.text}"

                raise ValueError(error_message)

            if response.status_code == 204:  # No content
                return {"success": True, "status_code": 204}

            return response.json()
        except json.JSONDecodeError:
            if response.status_code < 400:
                return {"success": True, "status_code": response.status_code, "text": response.text}
            raise ValueError(f"Invalid JSON response from JIRA API: {response.text}")

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make a GET request to the JIRA API.

        Args:
            endpoint (str): API endpoint to call
            params (Dict[str, Any], optional): Query parameters

        Returns:
            Dict[str, Any]: Response as dictionary
        """
        url = f"{self.jira_url}{self.api_base_path}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Make a POST request to the JIRA API.

        Args:
            endpoint (str): API endpoint to call
            data (Dict[str, Any]): Data to send

        Returns:
            Dict[str, Any]: Response as dictionary
        """
        url = f"{self.jira_url}{self.api_base_path}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        return self._handle_response(response)

    def put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Make a PUT request to the JIRA API.

        Args:
            endpoint (str): API endpoint to call
            data (Dict[str, Any]): Data to send

        Returns:
            Dict[str, Any]: Response as dictionary
        """
        url = f"{self.jira_url}{self.api_base_path}{endpoint}"
        response = requests.put(url, headers=self.headers, json=data)
        return self._handle_response(response)

    def delete(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make a DELETE request to the JIRA API.

        Args:
            endpoint (str): API endpoint to call
            params (Dict[str, Any], optional): Query parameters

        Returns:
            Dict[str, Any]: Response as dictionary
        """
        url = f"{self.jira_url}{self.api_base_path}{endpoint}"
        response = requests.delete(url, headers=self.headers, params=params)
        return self._handle_response(response)


def get_jira_client(api_base_path: str = "rest/api/3/") -> JiraApiClient:
    """
    Get a JIRA API client instance.

    Returns:
        JiraApiClient: JIRA API client
    """
    # return JiraApiClient()
    return JiraApiClient(api_base_path=api_base_path)
