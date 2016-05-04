# config.py

from authomatic.providers import oauth2, oauth1,openid

CONFIG = {

    'fb': {

        'class_': oauth2.Facebook,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '1679708478963527',
        'consumer_secret': '38169c157e0b7f926e8ef5bddf88703b',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['user_about_me','public_profile', 'email', 'publish_actions'],
    },

    'oi': {

        # OpenID provider dependent on the python-openid package.
        'class_': openid.OpenID,
    }
}
