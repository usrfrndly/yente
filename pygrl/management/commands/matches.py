from django.core.management.base import BaseCommand

from pygrl import connect


class Command(BaseCommand):
    help = "Show matches"
    SESSION = connect()

    def handle(self, *args, **options):
        for m in self.SESSION.matches():
            print m.user
