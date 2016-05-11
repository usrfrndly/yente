import logging

from . import models
from . import constants
from .utils import pull_date
from .binder import bind_api
from .exceptions import AuthorizationError


log = logging.getLogger(__name__)


class APIAuth(object):
    fb_id = None
    fb_token = None
    tinder_token = None
    _data = None

    def __init__(self, fb_id, fb_token):
        self.fb_id = fb_id
        self.fb_token = fb_token

    @property
    def is_complete(self):
        return all([self.fb_id, self.fb_token, self.tinder_token])


class API(object):
    ''' Class used to map to all Tinder API endpoints
    '''
    def __init__(self, auth_handler=None, host='https://api.gotinder.com', debug=False):
        self.auth = auth_handler
        self.host = host
        self.debug = debug
        self.likes_remaining = -1
        self.super_likes_remaining = -1
        self.super_likes_allotment = -1
        self.super_likes_resets_at = None
        self.rate_limited_until = None

    def set_auth(self, fb_id, fb_token):
        self.auth = APIAuth(fb_id, fb_token)

    _authorize = bind_api(
        path='/auth',
        allowed_params=['facebook_token', 'facebook_id'],
        method='POST',
        require_auth=False,
    )

    def authorize(self):
        data = self._authorize(
            facebook_token=self.auth.fb_token,
            facebook_id=self.auth.fb_id,
        )
        if 'token' not in data:
            # Error authorizing.
            raise AuthorizationError(
                '{0}: {1}'.format(data['code'], data['error'])
            )
        self.auth.tinder_token = data['token']
        self.meta_update()
        return models.Profile(data['user'], self)

    ping = bind_api(
        path='/user/ping',
        allowed_param=['lat', 'lon'],
        method='POST',
    )

    recs = bind_api(
        path='/user/recs',
        allowed_param=['limit'],
        delete_param=['limit'],
        strict_delete_param=False,
        method='POST',
    )

    _like = bind_api(
        path='/like/{user_id}',
        allowed_param=['user_id'],
    )

    _super_like = bind_api(
        path='/like/{user_id}/super',
        allowed_param=['user_id'],
        method='POST',
    )

    nope = bind_api(
        path='/pass/{user_id}',
        allowed_param=['user_id'],
    )

    updates = bind_api(
        path='/updates',
        allowed_param=['last_activity_date'],
        delete_param=['last_activity_date'],
        strict_delete_param=False,
        method='POST',
    )

    profile = bind_api(
        path='/profile',
        data_model=models.Profile,
    )

    update_profile = bind_api(
        path='/profile',
        allowed_param=constants.PROFILE_FIELDS,
        method='POST',
    )

    user_info = bind_api(
        path='/user/{user_id}',
        allowed_param=['user_id'],
    )

    report = bind_api(
        path='/report/{user_id}',
        allowed_param=['user_id', 'cause'],
        delete_param=['user_id'],
        method='POST',
    )

    match  = bind_api(
        path='/user/matches/{match_id}',
        allowed_param=['match_id'],
    )

    message = bind_api(
        path='/user/matches/{match_id}',
        allowed_param=['match_id', 'message'],
        delete_param=['match_id'],
        method='POST',
    )

    unmatch = bind_api(
        path='/user/matches/{match_id}',
        allowed_param=['match_id'],
        method='DELETE',
    )

    meta = bind_api(
        path='/meta',
    )

    ## HELPERS ##

    def report_spam(self, user_id):
        return self.report(user_id=user_id, cause=constants.REPORT_CAUSE_SPAM)

    def report_inappropriate(self, user_id):
        return self.report(
            user_id=user_id,
            cause=constants.REPORT_CAUSE_INAPPROPRIATE,
        )

    def like(self, user_id):
        data = self._like(user_id)
        if 'rate_limited_until' in data:
            # User has ran out of likes
            # XXX rate_limited_until appears to be epoch but isn't valid
            #self.rate_limited_until = pull_date(data['rate_limited_until'])
            self.rate_limited_until = data['rate_limited_until']
            if self.debug:
                log.info(
                    'X Likes are rate limited until '
                    '{0}'.format(self.rate_limited_until)
                )
            return False

        if 'likes_remaining' in data:
            self.likes_remaining = data['likes_remaining']
            if self.debug:
                log.info('* Likes Remaining: {0}'.format(self.likes_remaining))

        return data.get('match', False)

    def super_like(self, user_id):
        '''
            Response (normal):
                {u'match': False,
                 u'status': 200,
                 u'super_likes': {u'allotment': 1,
                                  u'remaining': 0,
                                  u'resets_at': u'2015-11-07T13:27:23.748Z'}}

            Response (exceeded):
                {u'limit_exceeded': True,
                 u'status': 200,
                 u'super_likes': {u'allotment': 1,
                                  u'remaining': 0,
                                  u'resets_at': u'2015-11-07T13:27:24.146Z'}}
        '''
        data = self._super_like(user_id)
        if 'limit_exceeded' in data and self.debug:
            log.info('X You have no available Super Likes')

        self.update_likes_remaining(data)
        return data.get('match', False)

    def meta_update(self):
        data = self.meta()
        self.update_likes_remaining(data['rating'])

    def update_likes_remaining(self, data):
        try:
            self.likes_remaining = data['likes_remaining']
            if self.debug:
                log.info('* Likes Remaining: {0}'.format(self.likes_remaining))
        except (KeyError, TypeError):
            pass

        try:
            self.super_likes_remaining = \
                data['super_likes']['remaining']
            self.super_likes_allotment = \
                data['super_likes']['allotment']
            self.super_likes_resets_at = \
                data['super_likes']['resets_at']
            if self.debug:
                log.info('* Super Likes Remaining: {0} (out of {1})'.format(
                    self.super_likes_remaining,
                    self.super_likes_allotment,
                ))
        except (KeyError, TypeError):
            pass

    def nearby(self, limit=11):
        data = self.recs(limit=limit)
        if not 'results' in data:
            data['results'] = []

        if data['results']:
            if data['results'][0]['_id'].startswith('tinder_rate_limited_id_'):
                if self.debug:
                    log.info('X You\'re currently rate limited.')
                    return

        for res in data['results']:
            yield models.User(res, self)

    def update_location(self, lat, lon):
        return self.ping(lat, lon)

    def get_user(self, user_id):
        data = self.user_info(user_id=user_id)
        return models.User(data['results'], self)

    def matches(self, since_date=None):
        ''' Since date should be a datetime.datetime instance
            representing the start date to get updated from.
            This is useful if you want matches from a long
            time ago.
        '''
        lad = since_date.isoformat() if since_date is not None else since_date
        mlist =  list(map(
            lambda x: models.Match(x, self),
            self.updates(last_activity_date=lad)['matches'],
        ))
        return sorted(mlist, key=lambda x: x.last_activity_date, reverse=True)
