from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from apps.messaging.models import Conversation


class Command(BaseCommand):
    help = "Delete empty conversations older than N days (default 7)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Delete empty conversations older than this many days.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print how many would be deleted.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timedelta(days=days)
        qs = (
            Conversation.objects.annotate(messages_count=Count("messages"))
            .filter(messages_count=0, updated_at__lt=cutoff)
        )
        count = qs.count()
        if options["dry_run"]:
            self.stdout.write(f"Would delete {count} empty conversation(s).")
            return
        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} empty conversation(s)."))
