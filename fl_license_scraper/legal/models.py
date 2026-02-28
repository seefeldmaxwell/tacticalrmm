"""Models for legal cases and disciplinary actions against licenses."""

from django.db import models
from django.urls import reverse

from fl_license_scraper.scraper.models import License


class LegalCase(models.Model):
    """A legal case, complaint, or disciplinary action against a license."""

    CASE_TYPE_CHOICES = [
        ("complaint", "Consumer Complaint"),
        ("disciplinary", "Disciplinary Action"),
        ("administrative", "Administrative Action"),
        ("citation", "Citation"),
        ("cease_desist", "Cease and Desist"),
        ("emergency_order", "Emergency Suspension Order"),
        ("consent_order", "Consent Order"),
        ("final_order", "Final Order"),
        ("violation", "Violation"),
        ("lawsuit", "Lawsuit"),
        ("arbitration", "Arbitration"),
        ("mediation", "Mediation"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("open", "Open / Active"),
        ("pending", "Pending Investigation"),
        ("under_review", "Under Review"),
        ("hearing_scheduled", "Hearing Scheduled"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
        ("settled", "Settled"),
        ("closed", "Closed"),
        ("appealed", "Appealed"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    SOURCE_CHOICES = [
        ("dbpr", "FL DBPR"),
        ("court", "Florida Courts"),
        ("bbb", "Better Business Bureau"),
        ("consumer", "Consumer Report"),
        ("manual", "Manual Entry"),
    ]

    # Relationships
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name="legal_cases",
    )

    # Case identifiers
    case_number = models.CharField(max_length=100, unique=True, db_index=True)
    case_type = models.CharField(max_length=30, choices=CASE_TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="medium")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="dbpr")

    # Case details
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    violation_details = models.TextField(blank=True)
    respondent_name = models.CharField(max_length=300, blank=True)
    complainant_type = models.CharField(max_length=100, blank=True)

    # Dates
    filed_date = models.DateField(null=True, blank=True)
    incident_date = models.DateField(null=True, blank=True)
    hearing_date = models.DateField(null=True, blank=True)
    resolution_date = models.DateField(null=True, blank=True)

    # Outcome
    outcome = models.TextField(blank=True)
    fine_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    penalty_description = models.TextField(blank=True)
    license_action = models.CharField(
        max_length=100,
        blank=True,
        help_text="Action taken on license (suspended, revoked, probation, etc.)",
    )
    probation_period = models.CharField(max_length=100, blank=True)
    restitution_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )

    # Source URLs
    source_url = models.URLField(max_length=500, blank=True)
    document_url = models.URLField(max_length=500, blank=True)

    # Metadata
    scraped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-filed_date"]
        indexes = [
            models.Index(fields=["case_number"]),
            models.Index(fields=["license", "status"]),
            models.Index(fields=["case_type", "status"]),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.title[:60]}"

    def get_absolute_url(self):
        return reverse("legal:case_detail", kwargs={"case_number": self.case_number})

    @property
    def total_financial_penalty(self):
        total = 0
        if self.fine_amount:
            total += self.fine_amount
        if self.restitution_amount:
            total += self.restitution_amount
        return total


class CaseDocument(models.Model):
    """Documents attached to a legal case."""

    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=300)
    document_type = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to="legal_documents/%Y/%m/", blank=True)
    external_url = models.URLField(max_length=500, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.case.case_number})"


class CaseNote(models.Model):
    """Notes and updates on a legal case."""

    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.case.case_number} - {self.created_at}"
