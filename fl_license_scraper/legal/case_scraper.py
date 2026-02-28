"""
Florida Legal Case Scraper.

Scrapes public legal/disciplinary actions from:
- Florida DBPR disciplinary actions
- Florida court records (public access)
"""

import logging
import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone

from fl_license_scraper.scraper.models import License

from .models import CaseNote, LegalCase

logger = logging.getLogger("scraper")

# DBPR disciplinary action search
DBPR_DISCIPLINE_URL = "https://www.myfloridalicense.com/dbpr/sto/file_download/EnforcementActionSearch.html"


class LegalCaseScraper:
    """Scrapes legal cases and disciplinary actions for Florida licenses."""

    def __init__(self):
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
            },
            timeout=30.0,
            follow_redirects=True,
        )

    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()

    def search_dbpr_disciplinary(self, license_number: str) -> list[dict]:
        """
        Search DBPR for disciplinary actions against a license.

        Queries the DBPR enforcement action database.
        """
        logger.info(f"Searching DBPR disciplinary actions for: {license_number}")

        try:
            time.sleep(self.delay)
            params = {
                "licenseNumber": license_number.strip(),
                "searchType": "licenseNumber",
            }
            response = self.client.get(DBPR_DISCIPLINE_URL, params=params)
            response.raise_for_status()
            return self._parse_disciplinary_results(response.text, license_number)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching disciplinary for {license_number}: {e}")
            return []

    def search_florida_courts(self, name: str, license_number: str = "") -> list[dict]:
        """
        Search Florida court records for cases involving a licensee.

        Uses publicly available court data.
        """
        logger.info(f"Searching FL courts for: {name}")

        results = []
        try:
            time.sleep(self.delay)
            # Search using the public court records interface
            fl_courts_url = getattr(
                settings,
                "FL_COURTS_SEARCH_URL",
                "https://www.flcourts.gov",
            )
            params = {"name": name.strip()}
            response = self.client.get(f"{fl_courts_url}/search", params=params)
            if response.status_code == 200:
                results = self._parse_court_results(response.text, license_number)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching courts for {name}: {e}")

        return results

    def _parse_disciplinary_results(self, html: str, license_number: str) -> list[dict]:
        """Parse DBPR disciplinary action search results."""
        soup = BeautifulSoup(html, "lxml")
        cases = []

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cells = row.find_all("td")
                if len(cells) >= 5:
                    case_data = self._extract_disciplinary_row(cells, license_number)
                    if case_data:
                        cases.append(case_data)

        # Also look for detail sections
        detail_sections = soup.find_all("div", class_=re.compile(r"case|action|enforcement", re.I))
        for section in detail_sections:
            case_data = self._extract_case_from_section(section, license_number)
            if case_data:
                cases.append(case_data)

        return cases

    def _extract_disciplinary_row(self, cells, license_number: str) -> Optional[dict]:
        """Extract case data from a disciplinary action table row."""
        try:
            case_number = cells[0].get_text(strip=True)
            if not case_number or case_number.startswith(("Case", "No.")):
                return None

            data = {
                "case_number": case_number,
                "license_number": license_number,
                "respondent_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                "case_type": self._classify_case_type(
                    cells[2].get_text(strip=True) if len(cells) > 2 else ""
                ),
                "title": cells[2].get_text(strip=True) if len(cells) > 2 else case_number,
                "filed_date": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                "status": self._classify_status(
                    cells[4].get_text(strip=True) if len(cells) > 4 else ""
                ),
                "outcome": cells[5].get_text(strip=True) if len(cells) > 5 else "",
            }

            # Extract fine amounts from outcome text
            if data["outcome"]:
                fine_match = re.search(r"\$[\d,]+\.?\d*", data["outcome"])
                if fine_match:
                    data["fine_amount"] = fine_match.group().replace("$", "").replace(",", "")

            # Get document link
            link = cells[0].find("a")
            if link and link.get("href"):
                href = link["href"]
                if not href.startswith("http"):
                    href = f"https://www.myfloridalicense.com/{href}"
                data["document_url"] = href

            return data
        except (IndexError, AttributeError):
            return None

    def _extract_case_from_section(self, section, license_number: str) -> Optional[dict]:
        """Extract case data from a detail section."""
        text = section.get_text(separator=" ", strip=True)
        if not text or len(text) < 20:
            return None

        case_num_match = re.search(r"(?:Case|No\.?|#)\s*[:\s]*([\w-]+)", text, re.I)
        if not case_num_match:
            return None

        return {
            "case_number": case_num_match.group(1),
            "license_number": license_number,
            "title": text[:200],
            "description": text,
            "case_type": "disciplinary",
            "source": "dbpr",
        }

    def _parse_court_results(self, html: str, license_number: str) -> list[dict]:
        """Parse Florida court search results."""
        soup = BeautifulSoup(html, "lxml")
        cases = []

        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                case_number = cells[0].get_text(strip=True)
                if case_number and not case_number.startswith(("Case", "No")):
                    cases.append({
                        "case_number": case_number,
                        "license_number": license_number,
                        "title": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "case_type": "lawsuit",
                        "filed_date": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        "status": self._classify_status(
                            cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        ),
                        "source": "court",
                    })

        return cases

    def _classify_case_type(self, text: str) -> str:
        """Classify case type from free text."""
        text = text.lower()
        type_map = {
            "complaint": "complaint",
            "disciplin": "disciplinary",
            "administrat": "administrative",
            "citation": "citation",
            "cease": "cease_desist",
            "emergency": "emergency_order",
            "consent": "consent_order",
            "final order": "final_order",
            "violation": "violation",
            "lawsuit": "lawsuit",
            "arbitrat": "arbitration",
            "mediat": "mediation",
        }
        for keyword, case_type in type_map.items():
            if keyword in text:
                return case_type
        return "other"

    def _classify_status(self, text: str) -> str:
        """Classify case status from free text."""
        text = text.lower()
        status_map = {
            "open": "open",
            "active": "open",
            "pending": "pending",
            "under review": "under_review",
            "hearing": "hearing_scheduled",
            "resolved": "resolved",
            "dismissed": "dismissed",
            "settled": "settled",
            "closed": "closed",
            "appeal": "appealed",
        }
        for keyword, status in status_map.items():
            if keyword in text:
                return status
        return "open"

    def save_case(self, data: dict) -> Optional[LegalCase]:
        """Save or update a legal case from scraped data."""
        case_number = data.get("case_number", "").strip()
        license_number = data.get("license_number", "").strip()

        if not case_number or not license_number:
            return None

        try:
            license_obj = License.objects.get(license_number=license_number)
        except License.DoesNotExist:
            logger.warning(f"License {license_number} not found for case {case_number}")
            return None

        # Parse fine amount
        fine_amount = None
        if data.get("fine_amount"):
            try:
                fine_amount = float(str(data["fine_amount"]).replace(",", ""))
            except (ValueError, TypeError):
                pass

        # Parse dates
        from fl_license_scraper.scraper.scraper_engine import DBPRScraper
        scraper = DBPRScraper()

        defaults = {
            "license": license_obj,
            "case_type": data.get("case_type", "other"),
            "status": data.get("status", "open"),
            "title": data.get("title", case_number),
            "description": data.get("description", ""),
            "violation_details": data.get("violation_details", ""),
            "respondent_name": data.get("respondent_name", ""),
            "filed_date": scraper._parse_date(data.get("filed_date", "")),
            "resolution_date": scraper._parse_date(data.get("resolution_date", "")),
            "outcome": data.get("outcome", ""),
            "fine_amount": fine_amount,
            "penalty_description": data.get("penalty_description", ""),
            "license_action": data.get("license_action", ""),
            "source": data.get("source", "dbpr"),
            "source_url": data.get("source_url", ""),
            "document_url": data.get("document_url", ""),
            "scraped_at": timezone.now(),
        }

        case_obj, created = LegalCase.objects.update_or_create(
            case_number=case_number,
            defaults=defaults,
        )

        return case_obj

    def scrape_cases_for_license(self, license_number: str) -> list[LegalCase]:
        """Scrape all available legal cases for a given license number."""
        saved_cases = []

        # Search DBPR disciplinary actions
        dbpr_cases = self.search_dbpr_disciplinary(license_number)
        for case_data in dbpr_cases:
            case_obj = self.save_case(case_data)
            if case_obj:
                saved_cases.append(case_obj)

        # Search Florida courts
        try:
            license_obj = License.objects.get(license_number=license_number)
            if license_obj.licensee_name:
                court_cases = self.search_florida_courts(
                    license_obj.licensee_name, license_number
                )
                for case_data in court_cases:
                    case_obj = self.save_case(case_data)
                    if case_obj:
                        saved_cases.append(case_obj)
        except License.DoesNotExist:
            pass

        return saved_cases


def lookup_cases(license_number: str) -> list[LegalCase]:
    """Look up legal cases for a license. Checks DB first, then scrapes."""
    existing = LegalCase.objects.filter(license__license_number=license_number)
    if existing.exists():
        # Check if we've scraped recently
        latest = existing.order_by("-scraped_at").first()
        if latest and latest.scraped_at:
            age = timezone.now() - latest.scraped_at
            if age.total_seconds() < 86400:
                return list(existing)

    scraper = LegalCaseScraper()
    return scraper.scrape_cases_for_license(license_number)
