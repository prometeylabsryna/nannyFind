from django.core.management.base import BaseCommand

from apps.reviews.signals import refresh_all_nanny_ratings


class Command(BaseCommand):
    help = "Перерахувати rating_avg і review_count усіх нянь з опублікованих відгуків"

    def handle(self, *args, **options):
        refresh_all_nanny_ratings()
        self.stdout.write(self.style.SUCCESS("Рейтинги синхронізовано з відгуками."))
