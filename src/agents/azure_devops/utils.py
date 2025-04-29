"""
Azure DevOps API Integration Utilities
"""

import os

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

    def get_client(self, client_type: str = "core"):
        """
        Get any Azure DevOps client dynamically by type name.

        Args:
            client_type (str): The type of client to get (e.g., 'git', 'work', 'core', etc.)
                               Default is 'core'

        Returns:
            Client: The requested Azure DevOps client

        Raises:
            AttributeError: If the requested client type doesn't exist
        """
        # Convert client_type to the method name in the Azure DevOps SDK
        method_name = f"get_{client_type}_client"

        # Check if the method exists in the clients collection
        if not hasattr(self.connection.clients_v7_1, method_name):
            raise AttributeError(f"Client type '{client_type}' is not supported")

        # Dynamically call the method
        return getattr(self.connection.clients_v7_1, method_name)()

    # def get_core_client(self):
    #     """
    #     Get a specific Azure DevOps client.

    #     Returns:
    #         Client: The requested Azure DevOps client
    #     """
    #     return self.connection.clients_v7_1.get_core_client()

    # def get_work_item_tracking_client(self):
    #     """
    #     Get a specific Azure DevOps client.

    #     Returns:
    #         Client: The requested Azure DevOps client
    #     """
    #     return self.connection.clients_v7_1.get_work_item_tracking_client()

    # def get_work_client(self):
    #     """
    #     Get the Azure DevOps Work client for iterations, backlogs, and boards.

    #     Returns:
    #         Client: The Azure DevOps Work client
    #     """
    #     return self.connection.clients_v7_1.get_work_client()

    # def get_work_item_tracking_process_client(self):
    #     """
    #     Get the Azure DevOps Work client for iterations, backlogs, and boards.

    #     Returns:
    #         Client: The Azure DevOps Work client
    #     """
    #     return self.connection.clients_v7_1.get_work_item_tracking_process_client()

    # def get_git_client(self):
    #     """
    #     Get the Azure DevOps Git client.

    #     Returns:
    #         Client: The Azure DevOps Git client
    #     """
    #     return self.connection.clients_v7_1.get_git_client()

    # def get_profile_client(self):
    #     """
    #     Get the Azure DevOps Profile client.

    #     Returns:
    #         Client: The Azure DevOps Profile client
    #     """
    #     return self.connection.clients_v7_1.get_profile_client()

    # def get_search_client(self):
    #     """
    #     Get the Azure DevOps Search client.

    #     Returns:
    #         Client: The Azure DevOps Search client
    #     """
    #     return self.connection.clients_v7_1.get_search_client()

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
