"""Реальне покриття каталогу: перевірені няні та міста з профілями."""

from django.db.models import Count, Q

from apps.geo.models import City
from apps.nannies.models import NannyProfile


def public_nanny_queryset():
    return NannyProfile.objects.filter(
        moderation_status=NannyProfile.ModerationStatus.APPROVED,
        is_verified=True,
    )


def _public_nanny_q():
    return Q(
        nannies__moderation_status=NannyProfile.ModerationStatus.APPROVED,
        nannies__is_verified=True,
    )


def cities_with_public_nannies():
    return (
        City.objects.filter(is_active=True)
        .annotate(nannies_count=Count("nannies", filter=_public_nanny_q(), distinct=True))
        .filter(nannies_count__gt=0)
        .prefetch_related("districts")
    )


def trust_count_label(nannies_count: int) -> str:
    return f"{nannies_count}+ перевірених нянь"


def trust_cities_label(cities_count: int) -> str:
    if cities_count == 1:
        return "У 1 місті України"
    return f"У {cities_count} містах України"


def catalog_coverage() -> dict:
    nannies_count = public_nanny_queryset().count()
    cities = list(cities_with_public_nannies())
    cities_count = len(cities)
    return {
        "nannies_count": nannies_count,
        "cities_count": cities_count,
        "cities": [
            {
                "name": c.name,
                "slug": c.slug,
                "nannies_count": c.nannies_count,
            }
            for c in cities
        ],
        "trust_count_label": trust_count_label(nannies_count),
        "trust_cities_label": trust_cities_label(cities_count),
    }
