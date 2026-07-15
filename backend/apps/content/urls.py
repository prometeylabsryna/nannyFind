from django.urls import path

from apps.content.views import BlogDetailView, BlogListView, FAQListView, StaticPageDetailView

urlpatterns = [
    path("blog/", BlogListView.as_view(), name="blog-list"),
    path("blog/<slug:slug>/", BlogDetailView.as_view(), name="blog-detail"),
    path("faq/", FAQListView.as_view(), name="faq-list"),
    path("pages/<str:key>/", StaticPageDetailView.as_view(), name="page-detail"),
]
