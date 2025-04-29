"""
Azure DevOps Profile API Functions

This module provides tools for interacting with Azure DevOps user profiles through the API.
Based on the Profile client from the azure-devops-python-api library.
"""

import json

from langchain_core.tools import tool

from agents.azure_devops.utils import get_azure_devops_client


@tool
def get_my_profile() -> str:
    """
    Get the profile of the authenticated user.

    Returns:
        str: JSON string containing the user's profile information
    """
    try:
        client = get_azure_devops_client()
        profile_client = client.get_client("profile")

        # Get the authenticated user's profile
        my_profile = profile_client.get_profile(id="me", details=True)

        # Format profile for display
        formatted_profile = {
            "id": my_profile.id,
            "display_name": my_profile.display_name,
            "email_address": my_profile.email_address,
            "core_revision": my_profile.core_revision,
            "time_stamp": my_profile.time_stamp.isoformat() if my_profile.time_stamp else None,
            "profile_state": my_profile.profile_state,
        }

        return json.dumps(formatted_profile, indent=2)
    except Exception as e:
        return f"Error retrieving profile: {str(e)}"


@tool
def get_profile(user_id: str) -> str:
    """
    Get the profile of a specific user by ID.

    Args:
        user_id (str): The ID of the user to get the profile for

    Returns:
        str: JSON string containing the user's profile information
    """
    try:
        client = get_azure_devops_client()
        profile_client = client.get_client("profile")

        # Get the profile of the specified user
        profile = profile_client.get_profile_with_attributes(user_id)

        # Format profile for display
        formatted_profile = {
            "id": profile.id,
            "display_name": profile.display_name,
            "email_address": profile.email_address,
            "core_revision": profile.core_revision,
            "time_stamp": profile.time_stamp.isoformat() if profile.time_stamp else None,
            "profile_state": profile.profile_state,
            "country": profile.country,
            "email_address_domains": profile.email_address_domains,
        }

        return json.dumps(formatted_profile, indent=2)
    except Exception as e:
        return f"Error retrieving profile: {str(e)}"


@tool
def get_profiles(profile_ids: list) -> str:
    """
    Get profiles for multiple users by their IDs.

    Args:
        profile_ids (list): A list of user IDs to get profiles for

    Returns:
        str: JSON string containing the users' profile information
    """
    try:
        client = get_azure_devops_client()
        profile_client = client.get_client("profile")

        # Get profiles for the specified users
        profiles = profile_client.get_profiles_with_attributes(profile_ids)

        # Format profiles for display
        formatted_profiles = []
        for profile in profiles:
            formatted_profiles.append(
                {
                    "id": profile.id,
                    "display_name": profile.display_name,
                    "email_address": profile.email_address,
                    "core_revision": profile.core_revision,
                    "time_stamp": profile.time_stamp.isoformat() if profile.time_stamp else None,
                    "profile_state": profile.profile_state,
                    "country": profile.country,
                    "email_address_domains": profile.email_address_domains,
                }
            )

        return json.dumps(formatted_profiles, indent=2)
    except Exception as e:
        return f"Error retrieving profiles: {str(e)}"


@tool
def update_profile(
    display_name: str | None = None,
    email_address: str | None = None,
    contact_with_offers: bool | None = None,
) -> str:
    """
    Update the authenticated user's profile information.

    Args:
        display_name (Optional[str]): New display name for the user
        email_address (Optional[str]): New email address for the user
        contact_with_offers (Optional[bool]): Whether the user wants to receive offers

    Returns:
        str: JSON string containing the updated profile information
    """
    try:
        client = get_azure_devops_client()
        profile_client = client.get_client("profile")

        # Get current profile to use as a base for the update
        current_profile = profile_client.get_profile()

        # Create update object with current values as defaults
        profile_update = {
            "displayName": display_name
            if display_name is not None
            else current_profile.display_name,
            "emailAddress": email_address
            if email_address is not None
            else current_profile.email_address,
        }

        if contact_with_offers is not None:
            profile_update["contactWithOffers"] = contact_with_offers

        # Update the profile
        updated_profile = profile_client.update_profile(profile_update)

        # Format updated profile for display
        formatted_profile = {
            "id": updated_profile.id,
            "display_name": updated_profile.display_name,
            "email_address": updated_profile.email_address,
            "core_revision": updated_profile.core_revision,
            "time_stamp": updated_profile.time_stamp.isoformat()
            if updated_profile.time_stamp
            else None,
            "profile_state": updated_profile.profile_state,
        }

        return json.dumps(formatted_profile, indent=2)
    except Exception as e:
        return f"Error updating profile: {str(e)}"


# Export the tools for use in the Azure DevOps assistant
profile_tools = [
    get_my_profile,
    get_profile,
    get_profiles,
    update_profile,
]
