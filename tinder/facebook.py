# -*- coding: utf-8 -*-
''' This module will emulate a FB login

    Taken, and adapted, from django-oauth-tokens
    https://github.com/ramusus/django-oauth-tokens
'''
import requests
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractproperty, abstractmethod
from .exceptions import AccountLocked, ImproperlyConfigured

class AuthRequestBase(object, metaclass=ABCMeta):

    authorize_form_attributes = {}

    session = None
    headers = {}

    @abstractproperty
    def form_action_domain(self):
        pass

    def __init__(self, username, password):
        self.session = requests.Session()

        self.username = username
        self.password = password

    def authorized_request(self, method='get', **kwargs):
        if method not in ['get', 'post']:
            raise ValueError('Only `get` and `post` are allowed methods')

        if not self.session.cookies:
            self.authorize()

        if self.session.cookies:
            return getattr(self.session, method)(
                headers=kwargs.pop('headers', self.headers),
                **kwargs
            )
        else:
            raise ValueError('Session cookies are not defined')

    def authorize(self):
        ''' Authorize and set self.session for next requests and return
            response of last request
        '''
        response = self.session.get(self.login_url, headers=self.headers)

        method, action, data = self.get_form_data_from_content(
            response.content,
            **self.authorize_form_attributes
        )

        # submit auth form data
        return self.session.post(action, data, headers=self.headers)

    def get_form_data(self, form):
        data = {}
        for input in form.findAll('input'):
            if input.get('name'):
                data[input.get('name')] = input.get('value')

        self.add_data_credentials(data)

        action = form.get('action')
        if action[0] == '/':
            action = self.form_action_domain + action

        return (form.get('method').lower(), action, data)

    @abstractmethod
    def add_data_credentials(self, data):
        pass

    def get_form_data_from_content(self, content, **kwargs):
        bs = BeautifulSoup(content, "html.parser")
        form = self.get_form_from_bs_content(bs, **kwargs)
        return self.get_form_data(form)

    def get_form_from_bs_content(self, bs, **kwargs):
        form = bs.find('form', **kwargs)
        if not form:
            raise Exception('There is no any form in response')
        return form


class FacebookAuthRequest(AuthRequestBase):
    ''' Facebook authorized request class
    '''
    provider = 'facebook'
    form_action_domain = 'https://m.facebook.com'
    login_url = 'https://m.facebook.com/login.php'
    headers = {
        'User-Agent': ('Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 '
                       'Chrome/34.0.1847.116 Safari/537.36'),
        'Upgrade-Insecure-Requests': 1,
        'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
                   'image/webp,*/*;q=0.8'),
        'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.facebook.com',
    }

    account_locked_phrases = [
        'Ваш аккаунт временно заблокирован',
        ('Мы заблокировали ваш аккаунт в связи '
         'с попыткой входа из незнакомого '
         'места. Пожалуйста, помогите нам '
         'подтвердить, что попытка входа была i'
         'произведена вами.'),
        'Your account is temporarily locked.',
    ]

    def add_data_credentials(self, data):
        data['email'] = self.username
        data['pass'] = self.password

    def authorize(self):
        response = super(FacebookAuthRequest, self).authorize()

        if b'Cookies Required' in response.content:
            self.session.get(self.form_action_domain)
            response = super(FacebookAuthRequest, self).authorize()
            if b'Cookies Required' in response.content:
                raise Exception("Facebook 'Cookies required' error")

        if b'You are trying too often' in response.content:
            raise Exception(('Facebook authorization request returns error '
                             '\'You are trying too often\''))

        # TODO: move this to FacebookAcessToken class
        if b'API Error Code: 191' in response.content:
            raise (
                ('You must specify URL \'{0}\' in your facebook application '
                 'settings').format(self.redirect_uri)
            )

        for account_locked_phrase in self.account_locked_phrases:
            if bytes(account_locked_phrase,'utf-8') in response.content:
                raise AccountLocked(
                    ('Facebook errored \'Your account is temporarily locked.\''
                     ' Try to login via web browser')
                )

        return response
