
from django.core.management.base import BaseCommand
from listings.models import Listing
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample Listing data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding listings...')

        sample_titles = [
            "Oceanview Villa",
            "Dianibeach Apartment",
            "Mountain Cabin",
            "Sealavie Resort",
            "Kongoriver Bungalow"
        ]

        locations = ["Nairobi", "Mombasa", "Kisumu", "Diani", "Naivasha"]

        for i in range(5):
            Listing.objects.create(
                title=sample_titles[i],
                description=f"Beautiful {sample_titles[i]} located in {locations[i]}.",
                location=locations[i],
                price_per_night=random.randint(5000, 20000),
                available_from=date.today(),
                available_to=date.today() + timedelta(days=30),
            )

        self.stdout.write(self.style.SUCCESS(' Successfully seeded listings!'))
