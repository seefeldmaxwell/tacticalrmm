"""
Management command to scrape Florida DBPR licenses.

Usage:
    python manage.py scrape_licenses --trade electrical
    python manage.py scrape_licenses --trade all
    python manage.py scrape_licenses --license EC13012345
    python manage.py scrape_licenses --name "John Smith" --trade plumbing
"""

from django.core.management.base import BaseCommand

from fl_license_scraper.scraper.scraper_engine import (
    DBPRScraper,
    TRADE_LICENSE_TYPES,
    lookup_license,
    search_licenses,
)


class Command(BaseCommand):
    help = "Scrape Florida DBPR for skilled trade licenses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--trade",
            type=str,
            help="Trade type to scrape (e.g., electrical, plumbing, hvac, or 'all')",
        )
        parser.add_argument(
            "--license",
            type=str,
            help="Specific license number to look up",
        )
        parser.add_argument(
            "--name",
            type=str,
            help="Name to search for",
        )
        parser.add_argument(
            "--county",
            type=str,
            help="County to search in",
        )

    def handle(self, *args, **options):
        if options["license"]:
            self.stdout.write(f"Looking up license: {options['license']}")
            result = lookup_license(options["license"])
            if result:
                self.stdout.write(self.style.SUCCESS(
                    f"Found: {result.license_number} - {result.licensee_name} "
                    f"({result.get_status_display()})"
                ))
            else:
                self.stdout.write(self.style.WARNING("License not found"))
            return

        if options["name"]:
            self.stdout.write(f"Searching for: {options['name']}")
            results = search_licenses(
                name=options["name"],
                trade_type=options.get("trade", ""),
            )
            self.stdout.write(f"Found {len(results)} results")
            for r in results[:20]:
                self.stdout.write(f"  {r.get('license_number', 'N/A')} - {r.get('licensee_name', 'N/A')}")
            return

        if options["trade"]:
            scraper = DBPRScraper()
            if options["trade"] == "all":
                for trade_key in TRADE_LICENSE_TYPES:
                    self.stdout.write(f"\nScraping {trade_key}...")
                    log = scraper.scrape_trade_category(trade_key)
                    self.stdout.write(
                        f"  Status: {log.status} | "
                        f"Found: {log.total_found} | "
                        f"New: {log.new_licenses} | "
                        f"Updated: {log.updated_licenses}"
                    )
            elif options["trade"] in TRADE_LICENSE_TYPES:
                self.stdout.write(f"Scraping {options['trade']}...")
                log = scraper.scrape_trade_category(options["trade"])
                self.stdout.write(self.style.SUCCESS(
                    f"Status: {log.status} | "
                    f"Found: {log.total_found} | "
                    f"New: {log.new_licenses}"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Unknown trade: {options['trade']}. "
                    f"Available: {', '.join(TRADE_LICENSE_TYPES.keys())}"
                ))
            return

        self.stdout.write(
            "Usage: scrape_licenses --trade <type> | --license <num> | --name <name>\n"
            f"Available trades: {', '.join(TRADE_LICENSE_TYPES.keys())}"
        )
