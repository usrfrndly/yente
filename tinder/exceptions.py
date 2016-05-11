class TinderError(Exception):
    pass


class AuthorizationError(Exception):
    pass

class ImproperlyConfigured(Exception):
    pass

class AccountLocked(Exception):
    pass

class RequestError(Exception):
    def __init__(self, json_data, *args, **kwargs):
        self._json_data = json_data
        super(RequestError, self).__init__(*args, **kwargs)
