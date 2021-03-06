import os
import re
import stat
import json
import datetime
import requests
import http.cookiejar
from . import constants
from .facebook import FacebookAuthRequest


def pull_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def get_facebook_user_id(fb_username):
    ''' Simple utility to pull the FB User ID for a given
        FB Username
    '''
    data = requests.get(
        'https://graph.facebook.com/{0}'.format(fb_username),
    ).json()
    return data['id']


def write_auth_to_file(auth, fname=constants.DEFAULT_AUTH_FILE_PATH):
    fname = os.path.expanduser(fname)
    json.dump({
        'fb_id': auth.fb_id,
        'fb_token': auth.fb_token,
        'tinder_token': auth.tinder_token,
    }, open(fname, 'w'))
    os.chmod(fname, stat.S_IMODE(0o600))


def read_auth_from_file(fname=constants.DEFAULT_AUTH_FILE_PATH):
    fname = os.path.expanduser(fname)
    return json.load(open(fname))


def load_auth_from_file(fname=constants.DEFAULT_AUTH_FILE_PATH):
    from . import api  # Circular
    data = read_auth_from_file(fname)
    auth = api.APIAuth(data['fb_id'], data['fb_token'])
    auth.tinder_token = data['tinder_token']
    return auth


def load_api_from_file(fname=constants.DEFAULT_AUTH_FILE_PATH):
    from . import api  # Circular
    auth = load_auth_from_file(fname)
    return api.API(auth_handler=auth)


def get_tinder_access_token(username=None, password=None, cookie_file=None):
    ''' Helper to login to your FB account and authorize
        the Tinder App to get an access token that will work
        with the Tinder API.
    '''
    if cookie_file is not None:
        use_cookies = http.cookiejar.LWPCookieJar(
            filename=os.path.expanduser(cookie_file),
        )
        try:
            use_cookies.load()
        except IOError:
            # Cookie file doesn't exist yet.
            pass

    fb_url = ('https://www.facebook.com/dialog/oauth?client_id=464891386855067'
              '&redirect_uri=https://www.facebook.com/connect/login_success.'
              'html&scope=basic_info,email,public_profile,user_about_me,'
              'user_activities,user_birthday,user_education_history,'
              'user_friends,user_interests,user_likes,user_location,'
              'user_photos,user_relationship_details&response_type=token')
    req = FacebookAuthRequest(username=username, password=password)
    if cookie_file is not None:
        req.session.cookies = use_cookies

    response = req.authorized_request(url=fb_url)
    if response.status_code != 200:
        raise ValueError('Error logging in {0}'.format(response.content))

    location = response.history[0].headers['location']
    res = re.search(r'.*access_token=(\w+)\&.*', location)
    if not res:
        raise ValueError('Unable to get access key {0}'.format(location))

    if cookie_file is not None:
        req.session.cookies.save()
    return res.groups()[0]
