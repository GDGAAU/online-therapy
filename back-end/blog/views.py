from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Article
from .serializers import ArticleListSerializer
from .serializers import ArticleDetailSerializer


class ArticleListAPIView(ListAPIView):
    queryset = Article.objects.all().order_by("-posted_at")
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "summary", "content", "author"]
    
class ArticleDetailAPIView(RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"