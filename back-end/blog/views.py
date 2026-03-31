from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Article
from .serializers import ArticleListSerializer


class ArticleListAPIView(ListAPIView):
    queryset = Article.objects.all().order_by("-posted_at")
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "summary", "content", "author"]