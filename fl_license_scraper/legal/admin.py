"""Admin configuration for legal case models."""
from django.contrib import admin
from .models import CaseDocument, CaseNote, LegalCase


class CaseDocumentInline(admin.TabularInline):
    model = CaseDocument
    extra = 0


class CaseNoteInline(admin.StackedInline):
    model = CaseNote
    extra = 0


@admin.register(LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = [
        "case_number", "license", "case_type", "status",
        "severity", "filed_date", "fine_amount",
    ]
    list_filter = ["case_type", "status", "severity", "source"]
    search_fields = ["case_number", "title", "license__license_number", "respondent_name"]
    readonly_fields = ["scraped_at", "created_at", "updated_at"]
    inlines = [CaseDocumentInline, CaseNoteInline]
    date_hierarchy = "filed_date"
    raw_id_fields = ["license"]
