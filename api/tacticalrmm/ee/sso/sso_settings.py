"""
Copyright (c) 2024-present Amidaware Inc.
This file is subject to the EE License Agreement.
For details, see: https://license.tacticalrmm.com/ee

Modified for y12.ai - Google OAuth as primary authentication
"""

import os

HEADLESS_ONLY = True
SOCIALACCOUNT_ONLY = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = "ee.sso.adapter.Y12SocialAdapter"
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_VERIFICATION = True

# Google OAuth Configuration for y12.ai
# Set these environment variables:
# GOOGLE_OAUTH_CLIENT_ID - Your Google OAuth Client ID
# GOOGLE_OAUTH_CLIENT_SECRET - Your Google OAuth Client Secret
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {"OAUTH_PKCE_ENABLED": True},
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "key": "",
        },
    },
}

# Google OAuth is the only authentication method
GOOGLE_AUTH_ONLY = os.environ.get("GOOGLE_AUTH_ONLY", "True").lower() == "true"

SESSION_COOKIE_SECURE = True
CORS_ALLOW_CREDENTIALS = True

# Cloudflare-specific settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
