"""Custom user model for FL License Scraper."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with role support."""

    ROLE_CHOICES = [
        ("homeowner", "Homeowner"),
        ("contractor", "Contractor"),
        ("admin", "Administrator"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="homeowner")
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    email_notifications = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_contractor(self):
        return self.role == "contractor"

    @property
    def is_homeowner(self):
        return self.role == "homeowner"
