from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from therapy.models import Specialty


INITIAL_SPECIALTIES = [
    "Anxiety",
    "Depression",
    "Trauma",
    "CBT",
    "Family Therapy",
    "Psychotherapy",
]


class Command(BaseCommand):
    help = "Seed the initial therapy specialties used by discovery filters."

    def handle(self, *args, **options):
        created_count = 0

        for name in INITIAL_SPECIALTIES:
            _, created = Specialty.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name},
            )
            if created:
                created_count += 1

        cache.clear()

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} specialties; {len(INITIAL_SPECIALTIES)} total configured."
            )
        )
