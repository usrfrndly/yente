import datetime
from . import constants
from .utils import pull_date
from .exceptions import TinderError


class FieldDescriptor(object):
    def __init__(self, id):
        self.id = id

    def __get__(self, instance, owner):
        return getattr(self, 'value', instance._data[self.id])

    def __set__(self, instance, value):
        self.value = value
        instance._data[self.id] = value

    # Helpers

    def get_gender(self, value):
        if isinstance(value, str):
            value = constants.GENDER_MAP[value.lower()]

        if value not in constants.GENDER_MAP_REVERSE:
            raise ValueError('Invalid value assigned for Gender')

        return value


class GenderDescriptor(FieldDescriptor):
    def __get__(self, instance, owner):
        gender = super(GenderDescriptor, self).__get__(instance, owner)
        return constants.GENDER_MAP_REVERSE[gender]

    def __set__(self, instance, value):
        value = self.get_gender(value)
        return super(GenderDescriptor, self).__set__(instance, value)


class InterestedDescriptor(FieldDescriptor):
    def __get__(self, instance, owner):
        int_in = super(InterestedDescriptor, self).__get__(instance, owner)
        return [constants.GENDER_MAP_REVERSE[x] for x in int_in]

    def __set__(self, instance, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        int_in = [self.get_gender(x) for x in value]
        return super(InterestedDescriptor, self).__set__(instance, value)


class DateTimeDescriptor(FieldDescriptor):
    def __get__(self, instance, owner):
        date = super(DateTimeDescriptor, self).__get__(instance, owner)
        return pull_date(date)

    def __set__(self, instance, value):
        if isinstance(value, datetime.datetime):
            value = value.isoformat()
        return super(DateTimeDescriptor, self).__set__(instance, value)


class BaseModel(object):
    def __init__(self, data_dict, api):
        self._data = data_dict
        self._api = api
        self._populate()

    def __getattribute__(self, name):
        try:
            return super(BaseModel, self).__getattribute__(name)
        except AttributeError:
            try:
                return self._data[name]
            except KeyError:
                raise AttributeError

    def _populate(self):
        ''' Helper function to do custom data processing at class init.
        '''
        pass

    def _pull_date(self, value):
        return pull_date(self._data[value])

    @property
    def id(self):
        return self._data['_id']

    def __str__(self):
        return self.__unicode__()


class Photo(BaseModel):
    def __init__(self, data_dict, api, parent=None):
        super(Photo, self).__init__(data_dict, api)
        self.parent = parent

    @property
    def width(self):
        return self._data.get('width')

    @property
    def height(self):
        return self._data.get('height')

    @property
    def sized_photos(self):
        if 'processedFiles' in self._data:
            if not hasattr(self, '_sized_photos'):
                self._sized_photos = [
                    Photo(x, self._api, self) for x in self.processedFiles
                ]
            return self._sized_photos
        return []

    @property
    def facebook_id(self):
        return self._data.get('fbId')

    @property
    def filename(self):
        return str(self.url.split('/')[-1])

    def __unicode__(self):
        return self.filename


class InstagramPhoto(object):
    def __init__(self, data_dict):
        self._data = data_dict
        self.image = data_dict['image']
        self.link = data_dict['link']
        self.thumbnail = data_dict['thumbnail']
        self.timestamp = \
            datetime.datetime.fromtimestamp(float(data_dict['ts']))

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.image


class InstagramUser(object):
    def __init__(self, data_dict, tinder_user):
        self._data = data_dict
        self._tinder_user = tinder_user
        self.username = data_dict['username']
        self.profile_picture = data_dict['profile_picture']
        self.media_count = data_dict['media_count']
        self.last_fetch_time = pull_date(data_dict['last_fetch_time'])
        self.photos = [InstagramPhoto(x) for x in data_dict['photos']]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}: {1}'.format(self.username, self.profile_picture)


class User(BaseModel):
    bio = FieldDescriptor('bio')
    gender = GenderDescriptor('gender')
    birth_date = DateTimeDescriptor('birth_date')
    ping_time = DateTimeDescriptor('ping_time')

    @property
    def last_active(self):
        if 'ping_time' in self._data:
            secs_ago = (datetime.datetime.now() - self.ping_time).seconds
            if secs_ago > 86400:
                return '{days} days ago'.format(days=(secs_ago / 86400))
            elif secs_ago < 3600:
                return '{mins} mins ago'.format(mins=(secs_ago / 60))
            else:
                return '{hours} hours ago'.format(hours=(secs_ago / 3600))
        return '[unknown]'

    @property
    def age(self):
        if 'birth_date' in self._data:
            return (datetime.datetime.now() - self.birth_date).days / 365
        return 0

    def _get_photos(self):
        return self._data.get('photos', [])

    def _photos(self):
        photos = [{
            'main': x.get('main', False),
            'url': x['url'],
        } for x in self._get_photos()]
        return sorted(photos, key=lambda x: x['main'], reverse=True)

    @property
    def photos(self):
        return [Photo(x, self._api) for x in self._get_photos()]

    @property
    def num_photos(self):
        return len(self._get_photos())

    @property
    def distance(self):
        return self._data.get('distance_mi', self._data.get('distance_km', 0))

    @property
    def jobs(self):
        return [
            [
                job.get('title', {}).get('name', None),
                job['company']['name']
            ] for job in self._data.get('jobs', [])
        ]

    @property
    def jobs_pretty(self):
        return [
            '{0} @ {1}'.format(x[0] or 'Untitled', x[1]) for x in self.jobs
        ]

    @property
    def schools(self):
        return [x['name'] for x in self._data.get('schools', [])]

    @property
    def instagram(self):
        if 'instagram' not in self._data:
            return None
        return InstagramUser(self._data['instagram'], self)

    def like(self):
        return self._api.like(self.id)

    def super_like(self):
        return self._api.super_like(self.id)

    def nope(self):
        return self._api.nope(self.id)

    def __unicode__(self):
        return '{name} ({age}), {distance}mi, {ago}'.format(
            name=self.name,
            age=self.age,
            distance=self.distance,
            ago=self.last_active,
        )


class Profile(User):
    ''' Your own user profile.
    '''
    create_date = DateTimeDescriptor('create_date')
    interested_in = InterestedDescriptor('interested_in')
    discoverable = FieldDescriptor('discoverable')
    distance_filter = FieldDescriptor('distance_filter')
    age_filter_min = FieldDescriptor('age_filter_min')
    age_filter_max = FieldDescriptor('age_filter_max')

    def save(self):
        data = {}
        for field in constants.PROFILE_FIELDS:
            data[field] = self._data[field]
        self._api.update_profile(**data)

    def matches(self, since_date=None):
        return self._api.matches(since_date=since_date)

    def like(self):
        raise TinderError('You can\'t like yourself')

    def super_like(self):
        raise TinderError('You can\'t super like yourself')

    def nope(self):
        raise TinderError('You can\'t dislike yourself')

    def __unicode__(self):
        return 'Profile: {name}'.format(name=self.name)


class Message(BaseModel):
    sent_date = DateTimeDescriptor('sent_date')
    date_sent = DateTimeDescriptor('sent_date')  # Helper
    created_date = DateTimeDescriptor('created_date')

    def __init__(self, data_dict, api, match):
        super(Message, self).__init__(data_dict, api)
        self.match = match

    def _them_or_you(self, value):
        if self._data[value] == self.match.user.id:
            return self.match.user.name
        else:
            return 'You'

    @property
    def msg_to(self):
        return self._them_or_you('to')

    @property
    def msg_from(self):
        return self._them_or_you('from')

    def __unicode__(self):
        return 'Message: {0} -> {1} [{2}]'.format(
            self.msg_from,
            self.msg_to,
            self.match,
        )


class Match(BaseModel):
    created_date = DateTimeDescriptor('created_date')
    last_activity_date = DateTimeDescriptor('last_activity_date')

    def _populate(self):
        try:
            self.user = User(self._data['person'], self._api)
        except KeyError:
            # Usually happens when the match has their account
            # banned or removed by Tinder. The 'person' data
            # isn't sent but the match remains.
            self.user = None

    @property
    def id(self):
        return self._data['_id']

    @property
    def messages(self):
        return list(map(
            lambda x: Message(x, self._api, self),
            self._data['messages'],
        ))

    def message(self, body):
        res = self._api.message(self.id, body)
        self._data['messages'].append(res)  # Add new message to chain
        return res

    def unmatch(self):
        return self._api.unmatch(self.id)

    def __unicode__(self):
        return 'Match with {0} ({1})'.format(self.user.name, self.user.id)
