"""Celery tasks for background scraping."""
import logging

from celery import shared_task

from .scraper_engine import DBPRScraper, TRADE_LICENSE_TYPES

logger = logging.getLogger("scraper")


@shared_task(bind=True, max_retries=3)
def scrape_trade_category(self, trade_key: str):
    """Scrape all licenses for a trade category in the background."""
    try:
        scraper = DBPRScraper()
        log = scraper.scrape_trade_category(trade_key)
        return {
            "status": log.status,
            "total_found": log.total_found,
            "new": log.new_licenses,
            "updated": log.updated_licenses,
            "errors": log.errors,
        }
    except Exception as exc:
        logger.error(f"Task failed for {trade_key}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def scrape_all_trades():
    """Scrape all trade categories. Intended for periodic scheduling."""
    results = {}
    for trade_key in TRADE_LICENSE_TYPES:
        scrape_trade_category.delay(trade_key)
        results[trade_key] = "queued"
    return results


@shared_task
def refresh_stale_licenses(hours: int = 48):
    """Re-scrape licenses that haven't been updated recently."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import License

    cutoff = timezone.now() - timedelta(hours=hours)
    stale = License.objects.filter(last_scraped__lt=cutoff, status="active")[:100]

    scraper = DBPRScraper()
    refreshed = 0
    for license_obj in stale:
        data = scraper.search_by_license_number(license_obj.license_number)
        if data:
            scraper.save_license(data)
            refreshed += 1

    return {"refreshed": refreshed, "total_stale": stale.count()}
