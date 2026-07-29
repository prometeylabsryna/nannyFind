from rest_framework import serializers

from apps.content.models import BlogPost, FAQItem, StaticPage


class BlogPostSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="published_at", format="%Y-%m-%d")
    image = serializers.SerializerMethodField()
    image_alt = serializers.CharField(source="display_image_alt", read_only=True)

    class Meta:
        model = BlogPost
        fields = (
            "slug",
            "title",
            "excerpt",
            "date",
            "category",
            "image",
            "image_alt",
            "content",
        )

    def get_image(self, obj):
        return obj.display_image or ""


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
