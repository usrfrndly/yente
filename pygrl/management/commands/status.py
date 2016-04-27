from django.core.management.base import BaseCommand

from pygrl import connect
from time import sleep
from datetime import datetime
from sys import stdout


class Command(BaseCommand):
    help = "Show matches"
    SESSION = connect()

    def handle(self, *args, **options):
        while True:
            msg = "{d}\t{n} remaining likes\n".format(d=datetime.now(), n=self.SESSION.likes_remaining)
            stdout.write(msg)
            stdout.flush()
            sleep(300)
