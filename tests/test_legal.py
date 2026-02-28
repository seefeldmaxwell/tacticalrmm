"""Tests for the legal case module."""

from decimal import Decimal

from django.test import TestCase

from fl_license_scraper.legal.models import CaseDocument, CaseNote, LegalCase
from fl_license_scraper.scraper.models import License


class LegalCaseTests(TestCase):
    """Tests for legal case model."""

    def setUp(self):
        self.license = License.objects.create(
            license_number="EC13099999",
            licensee_name="Bad Contractor",
            status="active",
        )
        self.case = LegalCase.objects.create(
            license=self.license,
            case_number="2024-001234",
            case_type="disciplinary",
            status="open",
            severity="high",
            title="Unlicensed work performed",
            fine_amount=Decimal("5000.00"),
            restitution_amount=Decimal("2500.00"),
        )

    def test_case_str(self):
        assert "2024-001234" in str(self.case)

    def test_case_url(self):
        url = self.case.get_absolute_url()
        assert "2024-001234" in url

    def test_total_financial_penalty(self):
        assert self.case.total_financial_penalty == Decimal("7500.00")

    def test_total_penalty_no_restitution(self):
        self.case.restitution_amount = None
        assert self.case.total_financial_penalty == Decimal("5000.00")

    def test_total_penalty_no_fine(self):
        self.case.fine_amount = None
        self.case.restitution_amount = Decimal("1000.00")
        assert self.case.total_financial_penalty == Decimal("1000.00")

    def test_license_has_cases(self):
        assert self.license.has_legal_cases is True
        assert self.license.legal_case_count == 1


class CaseDocumentTests(TestCase):
    """Tests for case documents."""

    def test_create_document(self):
        license_obj = License.objects.create(
            license_number="CFC000001",
            licensee_name="Test",
            status="active",
        )
        case = LegalCase.objects.create(
            license=license_obj,
            case_number="DOC-001",
            case_type="complaint",
            title="Test case",
        )
        doc = CaseDocument.objects.create(
            case=case,
            title="Final Order",
            document_type="PDF",
            external_url="https://example.com/doc.pdf",
        )
        assert "Final Order" in str(doc)


class CaseNoteTests(TestCase):
    """Tests for case notes."""

    def test_create_note(self):
        license_obj = License.objects.create(
            license_number="CFC000002",
            licensee_name="Test",
            status="active",
        )
        case = LegalCase.objects.create(
            license=license_obj,
            case_number="NOTE-001",
            case_type="complaint",
            title="Test case",
        )
        note = CaseNote.objects.create(
            case=case,
            note="Hearing scheduled for next month",
            author="Admin",
        )
        assert "NOTE-001" in str(note)
