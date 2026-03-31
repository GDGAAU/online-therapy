import hashlib
from datetime import datetime

from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright

from blog.models import Article


class Command(BaseCommand):
    help = "Scrape PsychologyToday listing page (Stage 1)"

    def handle(self, *args, **kwargs):
        url = "https://www.psychologytoday.com/us"

        data_to_save = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            page.wait_for_selector(".teaser-listing-item")

            articles = page.query_selector_all(".teaser-listing-item")

            self.stdout.write(f"Found {len(articles)} articles")

            for item in articles:
                try:
                    title_el = item.query_selector("h2.teaser-lg__title a")
                    if not title_el:
                        continue

                    title = title_el.inner_text().strip()
                    relative_url = title_el.get_attribute("href")
                    source_url = f"https://www.psychologytoday.com{relative_url}"

                    summary_el = item.query_selector(".teaser-lg__summary")
                    summary = summary_el.inner_text().strip() if summary_el else ""

                    author_el = item.query_selector(".teaser-lg__byline a")
                    author = author_el.inner_text().strip() if author_el else None

                    date_el = item.query_selector(".teaser-lg__published_on")
                    posted_at = None
                    if date_el:
                        date_text = date_el.inner_text().strip()
                        posted_at = datetime.strptime(date_text, "%B %d, %Y")

                    category_el = item.query_selector(".teaser-lg__topic a")
                    category = (
                        category_el.inner_text().strip().lower()
                        if category_el else "general"
                    )

                    source_name = "Psychology Today"

                    hash_input = (title + source_url).encode("utf-8")
                    content_hash = hashlib.sha256(hash_input).hexdigest()

                    data_to_save.append({
                        "title": title,
                        "summary": summary,
                        "content": "",
                        "source_name": source_name,
                        "source_url": source_url,
                        "author": author,
                        "posted_at": posted_at,
                        "category": category,
                        "content_hash": content_hash,
                    })

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))

            browser.close()

        for data in data_to_save:
            try:
                if Article.objects.filter(content_hash=data["content_hash"]).exists():
                    self.stdout.write(f"Skipped (duplicate): {data['title']}")
                    continue

                Article.objects.create(
                    **data,
                    reading_time=1
                )

                self.stdout.write(self.style.SUCCESS(f"Saved: {data['title']}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"DB Error: {e}"))