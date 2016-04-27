from time import sleep, time
from datetime import datetime, timedelta
import json

import dateutil.parser
from django.core.management.base import BaseCommand

from pygrl import connect
from pygrl.models import User


LONG_AGO = datetime(1970, 1, 1)
META_REFRESH_INTERVAL = timedelta(0, 600)

class Command(BaseCommand):
    help = "Scrape nearby users"
    SESSION = connect()
    _last_hit_api = LONG_AGO
    
    def add_arguments(self, parser):
        parser.add_argument("-l", "--like", action="store_true", help="Like any new user")

    def handle(self, *args, **options):
        self._autolike = options["like"]
        while True:
            users = [u for u in self.SESSION.nearby_users() if not u.id.startswith('tinder')]
            new_users = self.add(users)
            print "{d}: {n} new users found".format(d=datetime.now(), n=new_users)
            self._wait(new_users)
        
    @property
    def likes_remaining(self):
        """
        Cached value of remaining likes. Avoids polling the API too often.
        """
        now = datetime.now()
        if self._last_hit_api + META_REFRESH_INTERVAL < now:
            self._last_hit_api = now
            self._likes_remaining = self.SESSION.likes_remaining
            print now, ": {l} likes remaining".format(l=self._likes_remaining)
        return self._likes_remaining
        
    def add(self, users):
        new_users = 0
        for u in users:
            user, created = self._update_or_create(u)
            new_users += created
            if self._autolike and self.likes_remaining > 1:
                self._like(user)
        return new_users

    def _like(self, user):
        if user.like():
            print u"Match: {u}".format(u=user.name)
        self._last_hit_api = datetime.now()
        self._likes_remaining -= 1
        
    @staticmethod
    def _update_or_create(u):
        FIELDS = [f.name for f in User._meta.get_fields()]
        dct = {k:v for k, v in u._data.items() if k in FIELDS}
        dct['_data'] = json.dumps(u._data)
        dct['birth_date'] = dateutil.parser.parse(dct['birth_date'])
        dct.pop("_id")
        return User.objects.update_or_create(_id=u.id, defaults=dct)
            
    def _wait(self, new_users):
        can_like_in = self.SESSION.can_like_in
        computed_wait_time = 600./(4 ** new_users)  # Heuristic
        wait_time = max(can_like_in, computed_wait_time)
        sleep(wait_time)
