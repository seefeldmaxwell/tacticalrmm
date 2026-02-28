"""Celery configuration for FL License Scraper."""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fl_license_scraper.settings")

app = Celery("fl_license_scraper")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
