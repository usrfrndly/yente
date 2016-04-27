from time import sleep
import json

from django.core.management.base import BaseCommand

from pynder.models.user import Hopeful
from pygrl import connect
from pygrl.models import User


class Command(BaseCommand):
    SESSION = connect()
    
    def add_arguments(self, parser):
        parser.add_argument("-n", type=int, default=5, help="Like this many users")

    def handle(self, **kwargs):
        users = User.objects.exclude(liked__isnull=False)
        matches = 0
        for i, user in enumerate(users):
            if i >= kwargs['n']:
                break
            matches += self._do_one(user)
        print "Liked {n} users, got {m} matches".format(n=i, m=matches)
    
    def _do_one(self, user):
        hopeful = Hopeful(user.data, self.SESSION)
        matched = hopeful.like()
        if matched is not False:
            print "Match: {u}".format(u=user)
        user.like()
        return matched is not False
