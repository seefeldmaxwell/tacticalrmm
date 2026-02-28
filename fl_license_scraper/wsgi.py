"""WSGI config for FL License Scraper."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fl_license_scraper.settings")
application = get_wsgi_application()
