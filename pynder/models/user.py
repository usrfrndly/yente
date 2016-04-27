import re
from datetime import date

import dateutil.parser
from six import text_type
from .message import Message
from .. import constants


class User(object):

    def __init__(self, data, session):
        self._session = session
        self._data = data
        self.id = data['_id']

        SIMPLE_FIELDS = ("name", "bio", "birth_date", "ping_time")
        for f in SIMPLE_FIELDS:
            setattr(self, f, data.get(f, ''))

        self.photos_obj = [p for p in data['photos']]
        self.birth_date = dateutil.parser.parse(self.birth_date) if self.birth_date else None
        self.schools = []
        self.jobs = []
        try:
            self.schools.extend([school["name"] for school in data['schools']])
            self.jobs.extend(["%s @ %s" % (job["title"]["name"], job["company"][
                             "name"]) for job in data['jobs'] if 'title' in job and 'company' in job])
            self.jobs.extend(["%s" % (job["company"]["name"],) for job in data[
                             'jobs'] if 'title' not in job and 'company' in job])
            self.jobs.extend(["%s" % (job["title"]["name"],) for job in data[
                             'jobs'] if 'title' in job and 'company' not in job])
        except ValueError:
            pass

    @property
    def instagram_username(self):
        """Return instagram username if found in _data["instagram_username"] else empty string."""
        if self._data.get("instagram"):
            return self._data['instagram']['username']
        return ""

    @property
    def instagram_photos(self):
        """Return a list of instagram photo links if _data["instagram"] else empty list."""
        if self._data.get("instagram"):
            return [p.get('link') for p in self._data['instagram']['photos']]
        return []

    @property
    def gender(self):
        """Return gender as a string if _data["gender"] else empty string."""
        if self._data.get("gender"):
            return constants.GENDER_MAP[int(self._data['gender'])]
        return ""

    @property
    def common_interests(self):
        """Return list of common interests if _data["common_interests"] else empty list."""
        if self._data.get("common_interests"):
            return [p for p in self._data['common_interests']]
        return []

    @property
    def common_connections(self):
        """Return list of common connections if _data["common_connections"] else empty list."""
        if self._data.get("common_connections"):
            return [p for p in self._data['common_connections']]
        return []

    @property
    def thumbnails(self):
        return self.get_photos(width="84")

    @property
    def photos(self):
        return self.get_photos()

    @property
    def distance_km(self):
        if self._data.get("distance_mi") or self._data.get("distance_km"):
            return self._data.get('distance_km', self._data['distance_mi'] * 1.60934)
        else:
            return 0

    @property
    def distance_mi(self):
        """Return distance in miles if self._data["distance_mi"] else 0."""
        return self._data.get("distance_mi", 0)

    @property
    def age(self):
        today = date.today()
        return (today.year - self.birth_date.year -
                ((today.month, today.day) <
                 (self.birth_date.month, self.birth_date.day)))

    @property
    def mentions_snapchat(self):
        """Return True if user refers to snapchat in their bio else False."""
        p1 = re.compile("snapchat", re.IGNORECASE)
        p2 = re.compile(r"(?<!\w)SC(?!\w)", re.ASCII)
        bio = getattr(self, 'bio', '')
        if bio:
            return any(bool(p.search(bio)) for p in (p1, p2))
        return False

    @property
    def mentions_kik(self):
        """Return True if user refers to kik in their bio else False."""
        pattern = re.compile(r"(?<!\w)kik(?!\w)", flags=re.ASCII|re.IGNORECASE)
        bio = getattr(self, 'bio', '')
        if bio:
            return bool(pattern.search(bio))
        return False

    @property
    def mentions_instagram(self):
        """Return true if user refers to instagram in their bio else False."""
        p1 = re.compile(r"instagram", re.IGNORECASE)
        p2 = re.compile(r"(?<!\w)insta(?!\w)", flags=re.ASCII|re.IGNORECASE)
        p3 = re.compile(r"(?<!\w)IG(?!\w)", re.ASCII)
        bio = getattr(self, 'bio', '')
        if bio:
            return any(bool(p.search(bio)) for p in (p1, p2, p3))
        return False


    def __str__(self):
        return u"{n} ({a})".format(n=self.name, a=self.age)

    def __repr__(self):
        return repr(self.name)

    def report(self, cause):
        return self._session._api.report(self.id, cause)

    def get_photos(self, width=None):
        photos_list = []
        for photo in self.photos_obj:
            if width is None:
                photos_list.append(photo.get("url"))
            else:
                sizes = ["84", "172", "320", "640"]
                if width not in sizes:
                    print("Only support these widths: %s" % sizes)
                    return None
                for p in photo.get("processedFiles", []):
                    if p.get("width", 0) == int(width):
                        photos_list.append(p.get("url", None))
        return photos_list

    def dict(self, keys=None, additional_keys=None):
        """
        Return a User object as a dictionary based on the keys attribute.

        The default keys are as follows:
          'name',
          'id',
          'instagram_username',
          'instagram_photos',
          'age',
          'distance_km',
          'mentions_kik',
          'mentions_snapchat',
          'mentions_instagram',
          'bio',
          'photos'

        You can extend the default keys using the additional_keys parameter.
        i.e. keys.extend(additional_keys)
        """
        keys = keys or ['name',
                       'id',
                       'instagram_username',
                       'instagram_photos',
                       'age',
                       'distance_mi', # who uses the metric system? pfft
                       'mentions_kik',
                       'mentions_snapchat',
                       'mentions_instagram',
                       'bio',
                       'photos']
        additional_keys = additional_keys or []
        keys.extend(additional_keys)

        dictionary = {}
        for key in keys:
            value = getattr(self, key, None)
            dictionary[key] = value

        total_failure = all(e is None for e in dictionary.values())
        return dictionary if not total_failure else {}


class Hopeful(User):

    def like(self):
        return self._session._api.like(self.id)['match']

    def superlike(self):
        return self._session._api.superlike(self.id)['match']

    def dislike(self):
        return self._session._api.dislike(self.id)


class Match(object):

    def __init__(self, match, _session):
        self._session = _session
        self.id = match["_id"]
        self.user, self.messages = None, []
        if 'person' in match:
            user_data = _session._api.user_info(
                match['person']['_id'])['results']
            user_data['_id'] = match['person']['_id']
            self.user = User(user_data, _session)
            self.messages = [Message(m, user=self.user)
                             for m in match['messages']]

    def message(self, body):
        return self._session._api.message(self.id, body)['_id']

    def delete(self):
        return self._session._api._request('DELETE', '/user/matches/' + self.id)

    def __repr__(self):
        return repr(self.user)
