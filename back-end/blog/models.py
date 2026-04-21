import uuid
import hashlib

from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    CATEGORY_CHOICES = [
        ("anxiety", "Anxiety"),
        ("depression", "Depression"),
        ("stress", "Stress"),
        ("relationships", "Relationships"),
        ("self_care", "Self Care"),
        ("general", "General"),
    ]

    title = models.CharField(max_length=1000)
    slug = models.SlugField(unique=True, blank=True, max_length=300)

    summary = models.TextField()
    content = models.TextField()

    source_name = models.CharField(max_length=200)
    source_url = models.URLField(unique=True)

    author = models.CharField(max_length=200, null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default="general"
    )

    reading_time = models.PositiveIntegerField(
        help_text="Estimated reading time in minutes"
    )

    scraped_at = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=64, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:self._meta.get_field('slug').max_length]

        if not self.content_hash:
            hash_input = (self.title + self.content).encode('utf-8')
            self.content_hash = hashlib.sha256(hash_input).hexdigest()

        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title