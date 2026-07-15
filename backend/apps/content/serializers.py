from rest_framework import serializers

from apps.content.models import BlogPost, FAQItem, StaticPage


class BlogPostSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="published_at", format="%Y-%m-%d")

    class Meta:
        model = BlogPost
        fields = ("slug", "title", "excerpt", "date", "category", "image", "content")

    image = serializers.URLField(source="image_url")


class FAQSerializer(serializers.ModelSerializer):
    q = serializers.CharField(source="question")
    a = serializers.CharField(source="answer")

    class Meta:
        model = FAQItem
        fields = ("q", "a")


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ("key", "title", "body_html")
