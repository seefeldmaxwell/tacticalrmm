"""
Copyright (c) 2024-present Amidaware Inc.
This file is subject to the EE License Agreement.
For details, see: https://license.tacticalrmm.com/ee

Modified for y12.ai - Google OAuth as primary authentication
"""

import pyotp
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.core.exceptions import PermissionDenied

from accounts.models import Role
from core.tasks import sync_mesh_perms_task
from core.utils import token_is_valid
from tacticalrmm.logger import logger
from tacticalrmm.utils import get_core_settings


class Y12SocialAdapter(DefaultSocialAccountAdapter):
    """
    Social account adapter for y12.ai with Google OAuth as the primary authentication method.
    """

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # For Google OAuth, extract user info
        if sociallogin.account.provider == "google":
            extra_data = sociallogin.account.extra_data
            if "given_name" in extra_data:
                user.first_name = extra_data.get("given_name", "")
            if "family_name" in extra_data:
                user.last_name = extra_data.get("family_name", "")
            if "email" in extra_data:
                user.email = extra_data.get("email", "")

        try:
            provider = sociallogin.account.get_provider()
            provider_settings = SocialApp.objects.get(provider_id=provider).settings
            user.role = Role.objects.get(pk=provider_settings["role"])
        except Exception:
            logger.debug(
                "Provider settings or Role not found. Continuing with blank permissions."
            )

        user.totp_key = pyotp.random_base32()  # not actually used for Google OAuth
        user.is_sso_user = True  # Mark as SSO user
        sync_mesh_perms_task.delay()
        return user

    def is_open_for_signup(self, request, sociallogin):
        # For Google OAuth only mode, always allow signup
        google_auth_only = getattr(settings, "GOOGLE_AUTH_ONLY", False)

        if google_auth_only and sociallogin.account.provider == "google":
            return True

        _, valid = token_is_valid()
        if not valid:
            raise PermissionDenied()

        return super().is_open_for_signup(request, sociallogin)

    def list_providers(self, request):
        core_settings = get_core_settings()
        google_auth_only = getattr(settings, "GOOGLE_AUTH_ONLY", False)

        # In Google auth only mode, always show Google provider
        if google_auth_only:
            providers = super().list_providers(request)
            # Filter to only show Google provider
            return [p for p in providers if p.id == "google"]

        if not core_settings.sso_enabled:
            return []

        return super().list_providers(request)

    def get_login_redirect_url(self, request):
        """Redirect to dashboard after successful login."""
        return "/"


# Backwards compatibility alias
TacticalSocialAdapter = Y12SocialAdapter
