"""
Azure DevOps API Integration Utilities
"""

import os
from typing import Any, Dict, List, Optional, Union

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from core import settings


class AzureDevOpsClient:
    """
    A client for interacting with the Azure DevOps API.
    """

    def __init__(self):
        """Initialize the Azure DevOps API client with authentication details from environment variables."""
        self.azure_devops_org_url = (
            settings.AZURE_DEVOPS_ORG_URL.get_secret_value()
            if hasattr(settings, "AZURE_DEVOPS_ORG_URL")
            else os.environ.get("AZURE_DEVOPS_ORG_URL")
        )
        self.azure_devops_pat = (
            settings.AZURE_DEVOPS_PAT.get_secret_value()
            if hasattr(settings, "AZURE_DEVOPS_PAT")
            else os.environ.get("AZURE_DEVOPS_PAT")
        )

        if not all([self.azure_devops_org_url, self.azure_devops_pat]):
            raise ValueError("AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PAT must be set")

        # Ensure organization URL doesn't end with a trailing slash
        if self.azure_devops_org_url.endswith("/"):
            self.azure_devops_org_url = self.azure_devops_org_url[:-1]

        # Create a connection to Azure DevOps
        credentials = BasicAuthentication("", self.azure_devops_pat)
        self.connection = Connection(base_url=self.azure_devops_org_url, creds=credentials)

    def get_client(self):
        """
        Get a specific Azure DevOps client.

        Returns:
            Client: The requested Azure DevOps client
        """
        return self.connection.clients_v7_1.get_core_client()

    def handle_response_error(self, error):
        """
        Format error message from Azure DevOps API response.

        Args:
            error: The error from the Azure DevOps API

        Returns:
            str: Formatted error message
        """
        error_message = f"Azure DevOps API Error: {str(error)}"
        return error_message


def get_azure_devops_client() -> AzureDevOpsClient:
    """
    Get an Azure DevOps API client instance.

    Returns:
        AzureDevOpsClient: Azure DevOps API client
    """
    return AzureDevOpsClient()
