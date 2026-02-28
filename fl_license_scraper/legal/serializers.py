"""API serializers for legal case data."""
from rest_framework import serializers
from .models import CaseDocument, CaseNote, LegalCase


class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ["id", "title", "document_type", "external_url", "uploaded_at"]


class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ["id", "note", "author", "created_at"]


class LegalCaseSerializer(serializers.ModelSerializer):
    license_number = serializers.CharField(source="license.license_number", read_only=True)
    licensee_name = serializers.CharField(source="license.licensee_name", read_only=True)
    total_financial_penalty = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )

    class Meta:
        model = LegalCase
        fields = [
            "id", "case_number", "case_type", "status", "severity", "source",
            "license_number", "licensee_name",
            "title", "description", "violation_details",
            "respondent_name", "complainant_type",
            "filed_date", "incident_date", "hearing_date", "resolution_date",
            "outcome", "fine_amount", "penalty_description",
            "license_action", "probation_period", "restitution_amount",
            "total_financial_penalty",
            "source_url", "document_url",
            "created_at", "updated_at",
        ]


class LegalCaseDetailSerializer(LegalCaseSerializer):
    documents = CaseDocumentSerializer(many=True, read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)

    class Meta(LegalCaseSerializer.Meta):
        fields = LegalCaseSerializer.Meta.fields + ["documents", "notes"]
