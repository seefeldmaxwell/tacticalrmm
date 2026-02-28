"""
Florida DBPR License Scraper Engine.

Scrapes the Florida Department of Business and Professional Regulation
(DBPR) website to retrieve license information for skilled trades.

Target: https://www.myfloridalicense.com
"""

import logging
import re
import time
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone

from .models import License, LicenseHistory, ScrapeLog, TradeCategory

logger = logging.getLogger("scraper")

# Florida DBPR license type codes for skilled trades
TRADE_LICENSE_TYPES = {
    "electrical": {
        "board": "Electrical Contractors",
        "code": "5102",
        "prefix": "EC",
    },
    "plumbing": {
        "board": "Plumbing",
        "code": "5901",
        "prefix": "CFC",
    },
    "hvac": {
        "board": "Air Conditioning",
        "code": "5001",
        "prefix": "CAC",
    },
    "general_contractor": {
        "board": "General Contractor",
        "code": "5301",
        "prefix": "CGC",
    },
    "building_contractor": {
        "board": "Building Contractor",
        "code": "5302",
        "prefix": "CBC",
    },
    "roofing": {
        "board": "Roofing Contractor",
        "code": "5303",
        "prefix": "CCC",
    },
    "pool_contractor": {
        "board": "Swimming Pool",
        "code": "5304",
        "prefix": "CPC",
    },
    "solar_contractor": {
        "board": "Solar Contractor",
        "code": "5305",
        "prefix": "CSC",
    },
    "underground_utility": {
        "board": "Underground Utility",
        "code": "5306",
        "prefix": "CUC",
    },
    "alarm_system": {
        "board": "Alarm System",
        "code": "5100",
        "prefix": "EF",
    },
    "glass_glazing": {
        "board": "Glass and Glazing",
        "code": "5307",
        "prefix": "SCC",
    },
    "mechanical": {
        "board": "Mechanical Contractor",
        "code": "5308",
        "prefix": "CMC",
    },
    "sheet_metal": {
        "board": "Sheet Metal Contractor",
        "code": "5309",
        "prefix": "SMC",
    },
    "pollutant_storage": {
        "board": "Pollutant Storage",
        "code": "5310",
        "prefix": "PCS",
    },
}

# Status mapping from DBPR text to our model
STATUS_MAP = {
    "current": "active",
    "current,active": "active",
    "active": "active",
    "clear": "active",
    "clear/active": "active",
    "inactive": "inactive",
    "suspended": "suspended",
    "revoked": "revoked",
    "expired": "expired",
    "delinquent": "delinquent",
    "null and void": "null_and_void",
    "null & void": "null_and_void",
    "voluntarily inactive": "voluntarily_inactive",
    "vol. inactive": "voluntarily_inactive",
    "pending": "pending",
}


class DBPRScraper:
    """Scrapes the Florida DBPR website for license data."""

    def __init__(self):
        self.base_url = getattr(settings, "FL_DBPR_BASE_URL", "https://www.myfloridalicense.com/wl11.asp")
        self.delay = getattr(settings, "SCRAPER_REQUEST_DELAY", 2.0)
        self.user_agent = getattr(
            settings,
            "SCRAPER_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        self.client = httpx.Client(
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=30.0,
            follow_redirects=True,
        )
        self.scrape_log = None

    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date strings from DBPR in various formats."""
        if not date_str or date_str.strip() in ("", "N/A", "None"):
            return None
        date_str = date_str.strip()
        for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%m/%d/%y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        logger.warning(f"Could not parse date: {date_str}")
        return None

    def _normalize_status(self, status_text: str) -> str:
        """Map DBPR status text to our model status choices."""
        if not status_text:
            return "unknown"
        normalized = status_text.strip().lower()
        return STATUS_MAP.get(normalized, "unknown")

    def _determine_category(self, license_type: str, license_number: str) -> Optional[TradeCategory]:
        """Determine trade category from license type or number prefix."""
        for trade_key, trade_info in TRADE_LICENSE_TYPES.items():
            prefix = trade_info["prefix"]
            if license_number.upper().startswith(prefix):
                cat, _ = TradeCategory.objects.get_or_create(
                    slug=trade_key,
                    defaults={
                        "name": trade_info["board"],
                        "dbpr_code": trade_info["code"],
                    },
                )
                return cat

        # Fallback: try matching board name
        if license_type:
            for trade_key, trade_info in TRADE_LICENSE_TYPES.items():
                if trade_info["board"].lower() in license_type.lower():
                    cat, _ = TradeCategory.objects.get_or_create(
                        slug=trade_key,
                        defaults={
                            "name": trade_info["board"],
                            "dbpr_code": trade_info["code"],
                        },
                    )
                    return cat
        return None

    def search_by_license_number(self, license_number: str) -> Optional[dict]:
        """
        Search DBPR for a specific license number.

        Returns parsed license data dict or None.
        """
        logger.info(f"Searching DBPR for license number: {license_number}")

        params = {
            "mode": "2",
            "search": "SearchNow",
            "SID": "",
            "bession": "",
            "licid": license_number.strip(),
            "licName": "",
            "licNum": license_number.strip(),
        }

        try:
            time.sleep(self.delay)
            response = self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_search_results(response.text, license_number)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching for {license_number}: {e}")
            return None

    def search_by_name(self, name: str, trade_type: str = "") -> list[dict]:
        """
        Search DBPR for licenses by name.

        Returns list of parsed license data dicts.
        """
        logger.info(f"Searching DBPR for name: {name}, trade: {trade_type}")

        params = {
            "mode": "2",
            "search": "SearchNow",
            "SID": "",
            "bession": "",
            "licName": name.strip(),
            "licNum": "",
        }

        if trade_type and trade_type in TRADE_LICENSE_TYPES:
            params["licType"] = TRADE_LICENSE_TYPES[trade_type]["code"]

        try:
            time.sleep(self.delay)
            response = self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_search_results_list(response.text)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching for {name}: {e}")
            return []

    def search_by_county(self, county: str, trade_type: str = "") -> list[dict]:
        """Search DBPR for licenses by Florida county."""
        logger.info(f"Searching DBPR for county: {county}, trade: {trade_type}")

        params = {
            "mode": "2",
            "search": "SearchNow",
            "SID": "",
            "bession": "",
            "licCounty": county.strip(),
            "licName": "",
            "licNum": "",
        }

        if trade_type and trade_type in TRADE_LICENSE_TYPES:
            params["licType"] = TRADE_LICENSE_TYPES[trade_type]["code"]

        try:
            time.sleep(self.delay)
            response = self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_search_results_list(response.text)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching county {county}: {e}")
            return []

    def _parse_search_results(self, html: str, license_number: str) -> Optional[dict]:
        """Parse DBPR search results HTML for a single license."""
        soup = BeautifulSoup(html, "lxml")
        result = self._extract_license_data(soup, license_number)
        return result

    def _parse_search_results_list(self, html: str) -> list[dict]:
        """Parse DBPR search results HTML for multiple licenses."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Look for result table rows
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    data = self._extract_row_data(cells)
                    if data and data.get("license_number"):
                        results.append(data)

        return results

    def _extract_license_data(self, soup: BeautifulSoup, license_number: str) -> Optional[dict]:
        """Extract detailed license data from a DBPR detail page."""
        data = {"license_number": license_number}

        # Extract from labeled fields
        field_mappings = {
            "License Number": "license_number",
            "Licensee Name": "licensee_name",
            "Name": "licensee_name",
            "DBA Name": "dba_name",
            "Business Name": "business_name",
            "License Type": "license_type",
            "Status": "status",
            "Rank": "rank",
            "Address": "address_line1",
            "City": "city",
            "State": "state",
            "Zip Code": "zip_code",
            "County": "county",
            "Phone": "phone",
            "Email": "email",
            "Original Issue Date": "original_issue_date",
            "Effective Date": "effective_date",
            "Expiration Date": "expiration_date",
            "Last Renewal": "last_renewal_date",
            "Qualifier": "qualifier_name",
        }

        for label_text, field_name in field_mappings.items():
            label = soup.find(string=re.compile(re.escape(label_text), re.IGNORECASE))
            if label:
                parent = label.find_parent("td") or label.find_parent("th")
                if parent:
                    sibling = parent.find_next_sibling("td")
                    if sibling:
                        value = sibling.get_text(strip=True)
                        if value and value not in ("N/A", ""):
                            data[field_name] = value

        if not data.get("licensee_name"):
            return None

        return data

    def _extract_row_data(self, cells) -> Optional[dict]:
        """Extract license data from a result table row."""
        try:
            data = {
                "license_number": cells[0].get_text(strip=True),
                "licensee_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                "license_type": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                "status": cells[3].get_text(strip=True) if len(cells) > 3 else "",
            }
            # Get detail link if available
            link = cells[0].find("a")
            if link and link.get("href"):
                data["dbpr_url"] = link["href"]
                if not data["dbpr_url"].startswith("http"):
                    data["dbpr_url"] = f"https://www.myfloridalicense.com/{data['dbpr_url']}"

            if data["license_number"] and not data["license_number"].startswith(("License", "Lic")):
                return data
        except (IndexError, AttributeError):
            pass
        return None

    def save_license(self, data: dict) -> Optional[License]:
        """Save or update a license record from scraped data."""
        license_number = data.get("license_number", "").strip()
        if not license_number:
            return None

        status = self._normalize_status(data.get("status", ""))
        category = self._determine_category(
            data.get("license_type", ""),
            license_number,
        )

        defaults = {
            "licensee_name": data.get("licensee_name", ""),
            "business_name": data.get("business_name", ""),
            "dba_name": data.get("dba_name", ""),
            "license_type": data.get("license_type", ""),
            "status": status,
            "rank": data.get("rank", ""),
            "category": category,
            "address_line1": data.get("address_line1", ""),
            "address_line2": data.get("address_line2", ""),
            "city": data.get("city", ""),
            "state": data.get("state", "FL"),
            "zip_code": data.get("zip_code", ""),
            "county": data.get("county", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "original_issue_date": self._parse_date(data.get("original_issue_date", "")),
            "effective_date": self._parse_date(data.get("effective_date", "")),
            "expiration_date": self._parse_date(data.get("expiration_date", "")),
            "last_renewal_date": self._parse_date(data.get("last_renewal_date", "")),
            "qualifier_name": data.get("qualifier_name", ""),
            "dbpr_url": data.get("dbpr_url", ""),
            "last_scraped": timezone.now(),
            "raw_html": data.get("raw_html", ""),
        }

        license_obj, created = License.objects.update_or_create(
            license_number=license_number,
            defaults=defaults,
        )

        if not created:
            # Track changes in history
            for field, new_value in defaults.items():
                if field in ("last_scraped", "raw_html", "updated_at"):
                    continue
                old_value = getattr(license_obj, field, None)
                if old_value and str(old_value) != str(new_value) and new_value:
                    LicenseHistory.objects.create(
                        license=license_obj,
                        field_changed=field,
                        old_value=str(old_value),
                        new_value=str(new_value),
                    )

        return license_obj

    def scrape_trade_category(self, trade_key: str, max_pages: int = 10) -> ScrapeLog:
        """
        Scrape all licenses for a given trade category.

        Returns a ScrapeLog with results.
        """
        self.scrape_log = ScrapeLog.objects.create(
            search_query=f"trade:{trade_key}",
        )

        if trade_key not in TRADE_LICENSE_TYPES:
            self.scrape_log.status = "failed"
            self.scrape_log.error_messages = f"Unknown trade type: {trade_key}"
            self.scrape_log.completed_at = timezone.now()
            self.scrape_log.save()
            return self.scrape_log

        trade_info = TRADE_LICENSE_TYPES[trade_key]
        category, _ = TradeCategory.objects.get_or_create(
            slug=trade_key,
            defaults={
                "name": trade_info["board"],
                "dbpr_code": trade_info["code"],
            },
        )
        self.scrape_log.category = category
        self.scrape_log.save()

        total_new = 0
        total_updated = 0
        total_errors = 0
        all_results = []

        try:
            results = self.search_by_name("", trade_type=trade_key)
            all_results.extend(results)
            self.scrape_log.total_found = len(all_results)

            for result_data in all_results:
                try:
                    license_obj = self.save_license(result_data)
                    if license_obj:
                        if license_obj.created_at == license_obj.updated_at:
                            total_new += 1
                        else:
                            total_updated += 1
                except Exception as e:
                    total_errors += 1
                    logger.error(f"Error saving license: {e}")

            self.scrape_log.status = "completed"
        except Exception as e:
            self.scrape_log.status = "failed"
            self.scrape_log.error_messages = str(e)
            logger.error(f"Scrape failed for {trade_key}: {e}")

        self.scrape_log.new_licenses = total_new
        self.scrape_log.updated_licenses = total_updated
        self.scrape_log.errors = total_errors
        self.scrape_log.completed_at = timezone.now()
        self.scrape_log.save()

        return self.scrape_log


# Convenience functions
def lookup_license(license_number: str) -> Optional[License]:
    """Look up a license by number. Checks DB first, then scrapes DBPR."""
    # Check local DB first
    try:
        license_obj = License.objects.get(license_number=license_number)
        # Re-scrape if data is older than 24 hours
        age = timezone.now() - license_obj.last_scraped
        if age.total_seconds() < 86400:
            return license_obj
    except License.DoesNotExist:
        pass

    # Scrape from DBPR
    scraper = DBPRScraper()
    data = scraper.search_by_license_number(license_number)
    if data:
        return scraper.save_license(data)
    return None


def search_licenses(name: str = "", county: str = "", trade_type: str = "") -> list[dict]:
    """Search for licenses by name, county, or trade type."""
    scraper = DBPRScraper()
    if county:
        return scraper.search_by_county(county, trade_type)
    if name:
        return scraper.search_by_name(name, trade_type)
    return []
