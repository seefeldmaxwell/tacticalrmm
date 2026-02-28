"""
Management command to seed the database with sample data for development.

Usage:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from fl_license_scraper.scraper.models import License, TradeCategory
from fl_license_scraper.scraper.scraper_engine import TRADE_LICENSE_TYPES


class Command(BaseCommand):
    help = "Seed database with trade categories and sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding trade categories...")

        for trade_key, trade_info in TRADE_LICENSE_TYPES.items():
            cat, created = TradeCategory.objects.get_or_create(
                slug=trade_key,
                defaults={
                    "name": trade_info["board"],
                    "dbpr_code": trade_info["code"],
                    "description": f"Florida licensed {trade_info['board'].lower()} professionals.",
                },
            )
            status = "Created" if created else "Exists"
            self.stdout.write(f"  {status}: {cat.name}")

        # Florida counties for reference
        fl_counties = [
            "Miami-Dade", "Broward", "Palm Beach", "Hillsborough", "Orange",
            "Pinellas", "Duval", "Lee", "Polk", "Brevard", "Volusia",
            "Pasco", "Seminole", "Sarasota", "Manatee", "Collier",
            "Marion", "Leon", "Alachua", "St. Lucie", "Escambia",
            "St. Johns", "Clay", "Osceola", "Lake", "Martin",
        ]

        self.stdout.write(self.style.SUCCESS(
            f"\nSeeded {TradeCategory.objects.count()} trade categories."
        ))
        self.stdout.write(
            f"Florida counties for reference: {', '.join(fl_counties[:10])}..."
        )
        self.stdout.write(
            "\nRun 'python manage.py scrape_licenses --trade <type>' to populate license data."
        )
