from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.content.models import BlogPost, FAQItem, StaticPage
from apps.content.serializers import BlogPostSerializer, FAQSerializer, StaticPageSerializer


class BlogListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostSerializer
    pagination_class = None

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostSerializer
    lookup_field = "slug"
    queryset = BlogPost.objects.filter(is_published=True)


class FAQListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FAQSerializer
    pagination_class = None

    def get_queryset(self):
        return FAQItem.objects.filter(is_published=True)


class StaticPageDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaticPageSerializer
    lookup_field = "key"
    queryset = StaticPage.objects.filter(is_published=True)
