import ast
import json

from django.db import transaction
from django.db.models import IntegerField, CharField, DateTimeField, \
    NullBooleanField, Model, TextField, FloatField, SubfieldBase, ForeignKey

from pynder.models.user import Hopeful


class ListField(TextField):
    __metaclass__ = SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class User(Model):
    _id = CharField(max_length=30, unique=True, null=False)
    _data = TextField(default="")
    bio = CharField(max_length=300)
    birth_date = DateTimeField()
    fuzzy_birth_date = NullBooleanField()
    common_friend_count = IntegerField(default=0)
    common_friends = TextField(default="")
    common_like_count = IntegerField(default=0)
    common_likes = TextField(default="")
    connection_count = IntegerField(default=0)
    seen = IntegerField(default=1)
    distance_km = FloatField(default=0)
    gender = CharField(max_length=15)
    name = CharField(max_length=100)
    photos = ListField()
    ping_time = DateTimeField()

    liked = NullBooleanField()

    age = Hopeful.age

    @transaction.atomic
    def like(self):
        self.liked = True
        self.save()
        History.objects.create(user=self, action="like")

    @property
    def data(self):
        return json.loads(self._data)

    def to_dct(self):
        return {
            'id': self._id,
            'name': self.name,
            'bio': self.bio,
            'age': self.age,
            'photos': [p['url'] for p in self.photos]
        }

    def __str__(self):
        return "{n} ({a})".format(n=repr(self.name), a=self.age)

    def __repr__(self):
        return "<{n} ({a}) #{i}>".format(n=repr(self.name), a=self.age, i=self._id)


class History(Model):
    user = ForeignKey(User)
    timestamp = DateTimeField(auto_now_add=True)
    action = CharField(max_length=20)
