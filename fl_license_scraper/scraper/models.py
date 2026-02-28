"""Models for Florida license data scraped from DBPR."""

from django.db import models
from django.urls import reverse
from django.utils import timezone


class TradeCategory(models.Model):
    """Skilled trade categories (Electrical, Plumbing, HVAC, etc.)."""

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    dbpr_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="DBPR license type code used for scraping",
    )
    icon = models.CharField(
        max_length=50,
        default="wrench",
        help_text="Icon class name for display",
    )

    class Meta:
        verbose_name_plural = "Trade categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("scraper:category_detail", kwargs={"slug": self.slug})


class License(models.Model):
    """A Florida skilled trade license from DBPR."""

    STATUS_CHOICES = [
        ("active", "Active / Current"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
        ("revoked", "Revoked"),
        ("expired", "Expired"),
        ("delinquent", "Delinquent"),
        ("null_and_void", "Null and Void"),
        ("voluntarily_inactive", "Voluntarily Inactive"),
        ("pending", "Pending"),
        ("unknown", "Unknown"),
    ]

    RANK_CHOICES = [
        ("journeyman", "Journeyman"),
        ("master", "Master"),
        ("contractor", "Contractor"),
        ("registered", "Registered"),
        ("certified", "Certified"),
        ("specialty", "Specialty"),
    ]

    # Core license info
    license_number = models.CharField(max_length=50, unique=True, db_index=True)
    license_type = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="unknown", db_index=True)
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, blank=True)
    category = models.ForeignKey(
        TradeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="licenses",
    )

    # Licensee info
    licensee_name = models.CharField(max_length=300, db_index=True)
    business_name = models.CharField(max_length=300, blank=True)
    dba_name = models.CharField(max_length=300, blank=True, verbose_name="DBA Name")

    # Contact / Address
    address_line1 = models.CharField(max_length=300, blank=True)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True, db_index=True)
    state = models.CharField(max_length=2, default="FL")
    zip_code = models.CharField(max_length=10, blank=True)
    county = models.CharField(max_length=100, blank=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Dates
    original_issue_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    last_renewal_date = models.DateField(null=True, blank=True)

    # Qualifiers / Additional data
    qualifier_name = models.CharField(max_length=300, blank=True)
    primary_qualifier = models.BooleanField(default=False)
    alternate_names = models.TextField(
        blank=True,
        help_text="Comma-separated alternate names",
    )

    # Scraper metadata
    dbpr_url = models.URLField(max_length=500, blank=True)
    last_scraped = models.DateTimeField(default=timezone.now)
    scrape_source = models.CharField(max_length=50, default="dbpr")
    raw_html = models.TextField(blank=True, help_text="Raw scraped HTML for debugging")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_scraped"]
        indexes = [
            models.Index(fields=["license_number"]),
            models.Index(fields=["licensee_name"]),
            models.Index(fields=["status", "category"]),
            models.Index(fields=["city", "county"]),
        ]

    def __str__(self):
        return f"{self.license_number} - {self.licensee_name}"

    def get_absolute_url(self):
        return reverse("scraper:license_detail", kwargs={"license_number": self.license_number})

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_expired(self):
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return self.status == "expired"

    @property
    def has_legal_cases(self):
        return self.legal_cases.exists()

    @property
    def legal_case_count(self):
        return self.legal_cases.count()


class LicenseHistory(models.Model):
    """Track changes to a license over time."""

    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name="history")
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "License histories"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.license.license_number} - {self.field_changed} changed on {self.changed_at}"


class ScrapeLog(models.Model):
    """Log of scraping operations."""

    STATUS_CHOICES = [
        ("started", "Started"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("partial", "Partial"),
    ]

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="started")
    category = models.ForeignKey(
        TradeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    search_query = models.CharField(max_length=500, blank=True)
    total_found = models.IntegerField(default=0)
    new_licenses = models.IntegerField(default=0)
    updated_licenses = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    error_messages = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Scrape {self.started_at.strftime('%Y-%m-%d %H:%M')} - {self.status}"
