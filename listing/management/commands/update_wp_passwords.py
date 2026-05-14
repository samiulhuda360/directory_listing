import json
from django.core.management.base import BaseCommand
from listing.models import APIConfig


class Command(BaseCommand):
    help = 'Update WordPress application passwords from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file with {domain: {user, password}} entries')

    def handle(self, *args, **options):
        with open(options['json_file'], 'r') as f:
            data = json.load(f)

        updated = 0
        not_found = 0
        for domain, creds in data.items():
            count = APIConfig.objects.filter(website=domain).update(
                user=creds['user'],
                password=creds['password'],
            )
            if count:
                updated += 1
                self.stdout.write(f"Updated: {domain}")
            else:
                not_found += 1
                self.stdout.write(self.style.WARNING(f"Not in DB: {domain}"))

        self.stdout.write(self.style.SUCCESS(f"\nDone — Updated: {updated}, Not in DB: {not_found}"))
