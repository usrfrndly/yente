from tinder.browser import FacebookBrowser
from pynder.session import Session


def get_creds():
    try:
        from local_settings import EMAIL, PASS
        return EMAIL, PASS
    except ImportError:
        raise SystemExit("Please define `EMAIL` and `PASS` variables in a local_settings.py file")


def connect(email=None, passwd=None):
    if email is None or passwd is None:
        email, passwd = get_creds()
    fb = FacebookBrowser()
    fb.login(email, passwd)
    return Session(fb.info["id"], fb.access_token)
