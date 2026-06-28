import logging
import argparse
import sys

from config import DATA_DIR
from storage.json_storage import JSONStorage
from scrapers.official_docs import OfficialDocsScraper, CreatorHubScraper
from scrapers.devforum import DevForumScraper
from scrapers.github_repos import GitHubScraper
from scrapers.examples import ExamplesScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

SCRAPERS = {
    "official_docs": (OfficialDocsScraper, "documentation", "engine_api"),
    "creator_hub": (CreatorHubScraper, "documentation", "creator_hub"),
    "devforum": (DevForumScraper, "community", "devforum"),
    "github": (GitHubScraper, "code", "github_repos"),
    "examples": (ExamplesScraper, "examples", "categorized"),
}


def run_all():
    storage = JSONStorage(DATA_DIR)
    total = 0

    for name, (cls, category, subcategory) in SCRAPERS.items():
        logger.info("=== Running scraper: %s ===", name)
        scraper = cls()
        try:
            items = scraper.scrape()
            if items:
                path = storage.save(category, subcategory, items)
                logger.info("Saved %d items to %s", len(items), path)
                total += len(items)
            else:
                logger.warning("No items returned from %s", name)
        except Exception as e:
            logger.error("Scraper %s failed: %s", name, e, exc_info=True)
            continue

    logger.info("Done. Total items collected: %d", total)
    logger.info("Output: %s", DATA_DIR)
    return total


def list_data():
    storage = JSONStorage(DATA_DIR)
    for cat in storage.list_categories():
        subcats = storage.list_subcategories(cat)
        for sub in subcats:
            data = storage.load(cat, sub)
            if data:
                print(f"  {cat}/{sub}: {data['meta']['count']} items")


def main():
    parser = argparse.ArgumentParser(description="Roblox Knowledge Base Scraper")
    parser.add_argument(
        "--action",
        choices=["scrape", "list"],
        default="scrape",
        help="Action to perform",
    )
    parser.add_argument(
        "--scraper",
        choices=list(SCRAPERS.keys()) + ["all"],
        default="all",
        help="Specific scraper to run",
    )

    args = parser.parse_args()

    if args.action == "list":
        list_data()
        return

    if args.scraper == "all":
        run_all()
    else:
        storage = JSONStorage(DATA_DIR)
        name = args.scraper
        cls, category, subcategory = SCRAPERS[name]
        logger.info("Running: %s", name)
        scraper = cls()
        items = scraper.scrape()
        if items:
            path = storage.save(category, subcategory, items)
            logger.info("Saved %d items to %s", len(items), path)
        else:
            logger.warning("No items returned from %s", name)


if __name__ == "__main__":
    main()
