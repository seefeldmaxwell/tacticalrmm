"""ASGI config for FL License Scraper."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fl_license_scraper.settings")
application = get_asgi_application()
