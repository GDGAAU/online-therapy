from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from blog.models import Article


class Command(BaseCommand):
    help = "Scrape full article content (Stage 2)"

    def handle(self, *args, **kwargs):
        articles = list(Article.objects.filter(content=""))

        self.stdout.write(f"Found {len(articles)} articles to process")

        updated_articles = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for article in articles:
                try:
                    self.stdout.write(f"Processing: {article.title}")

                    page.goto(article.source_url, timeout=60000)

                    page.wait_for_selector(".field-name-body")

                    paragraphs = page.query_selector_all(".field-name-body p")

                    content_list = []

                    for p_tag in paragraphs:
                        text = p_tag.inner_text().strip()

                        if text and "advertisement" not in text.lower():
                            content_list.append(text)

                    full_content = "\n\n".join(content_list)

                    article._scraped_content = full_content
                    updated_articles.append(article)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))

            browser.close()

        for article in updated_articles:
            try:
                article.content = article._scraped_content
                article.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Updated: {article.title}")
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"DB Error: {e}"))