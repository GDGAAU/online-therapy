from rest_framework import serializers
from .models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "summary",
            "category",
            "author",
            "posted_at",
            "reading_time",
        ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ["scraped_at", "content_hash"]