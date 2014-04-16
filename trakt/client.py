from trakt.helpers import parse_credentials
from trakt.interfaces import construct_map
from trakt.request import TraktRequest

import requests


class TraktClient(object):
    base_url = 'http://api.trakt.tv'
    interfaces = None

    def __init__(self):
        self.api_key = None

        # Scrobbling parameters
        self.plugin_version = None
        self.media_center_version = None

        # Private
        self._session = requests.Session()

        self._get_credentials = None

        # Construct interfaces
        self.interfaces = construct_map(self)

    def request(self, path, params=None, data=None, credentials=None, **kwargs):
        request = TraktRequest(
            self,
            path=path,

            params=params,
            data=data,

            credentials=credentials,
            **kwargs
        )

        prepared = request.prepare()

        # TODO retrying requests on 502, 503 errors
        return self._session.send(prepared)

    def __getitem__(self, path):
        parts = path.strip('/').split('/')

        cur = self.interfaces

        while parts:
            key = parts.pop(0)
            if key not in cur:
                return None

            cur = cur[key]

        if type(cur) is dict:
            return cur.get(None)

        return cur


    @property
    def credentials(self):
        return parse_credentials(self._get_credentials())

    @credentials.setter
    def credentials(self, value):
        if hasattr(value, '__iter__'):
            self._get_credentials = lambda: value
        elif hasattr(value, '__call__'):
            self._get_credentials = value
        else:
            raise ValueError('(<username>, <password>) iterable, or function is required')
