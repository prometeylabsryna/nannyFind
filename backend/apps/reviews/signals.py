from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import Avg, Count

from apps.reviews.models import Review


def refresh_nanny_rating(nanny_id):
    """Перерахувати rating_avg / review_count лише з опублікованих відгуків."""
    from apps.nannies.models import NannyProfile

    stats = Review.objects.filter(nanny_id=nanny_id, is_published=True).aggregate(
        avg=Avg("rating"),
        cnt=Count("id"),
    )
    NannyProfile.objects.filter(pk=nanny_id).update(
        rating_avg=stats["avg"] or 0,
        review_count=stats["cnt"] or 0,
    )


def refresh_all_nanny_ratings():
    """Синхронізувати рейтинг усіх профілів з реальними відгуками."""
    from apps.nannies.models import NannyProfile

    for nanny_id in NannyProfile.objects.values_list("pk", flat=True):
        refresh_nanny_rating(nanny_id)


@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    refresh_nanny_rating(instance.nanny_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    refresh_nanny_rating(instance.nanny_id)
