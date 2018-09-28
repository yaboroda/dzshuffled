import json
import http.server
import webbrowser
import re
from typing import Union

import requests


class DeezerAuth(object):
    """Authorization in Deezer.

    1. Fetching auth code for app with asking you for permission
    For getting answer, will be started web server on port from config.

    2. With code fetching temporary auth token. This token you must
    attach with each request to Deezer API
    """

    def __init__(self):
        self.token = ''
        self._user = None
        self._url_auth = (
            'https://connect.deezer.com/oauth/auth.php?app_id={0}'
            '&redirect_uri={1}'
            '&perms=basic_access,manage_library,delete_library'
        )
        self._url_token = (
            'https://connect.deezer.com/oauth/access_token.php?app_id={0}'
            '&secret={1}&code={2}&output=json'
        )
        self._url_redirect = 'http://localhost:{0}/authfinish'
        self._url_check_token = (
            'http://api.deezer.com/user/me?access_token={0}'
        )
        self.browser = webbrowser.Chromium('chromium')

    @property
    def user(self):
        """Return Dict with user info"""
        if self._user is None:
            self._fetch_user()

        return self._user

    def set_params(self, port: Union[int, str], secret: str,
                   app_id: Union[int, str], token: str = ''):
        """Set parameters for authorization.

        If you pass in token, it will be used instead of retriving new.

        Keyword arguments:
        params -- dictionary with obligatory keys:
            port - on this port will be started web server
            secret - secret of your Deezer app
            app_id - id of your Deezer app
        token -- auth token, if empty or invalid,
            it will be fetched (default '')
        """
        self._port = int(port)
        self._secret = secret
        self._app_id = str(app_id)
        self.token = token

    def authorize(self):
        """Authorize and get token."""
        if not self._app_id or not self._secret:
            raise DeezerAuthError(
                'You cant get authorization token without app_id '
                'and secret. Fill it in config file or write there '
                'valid token.'
            )
        self._fetch_code()
        self._fetch_token()

    def check_token(self):
        """Check auth token, fetching user info, return bool"""
        url = self._url_check_token.format(self.token)
        response = json.loads(requests.get(url).text)

        if 'error' in response:
            return False
        elif 'type' in response and response['type'] == 'user':
            self._user = response
            return True
        else:
            raise DeezerAuthError('Cant check auth token')

    def _fetch_code(self):
        """Fetch auth app code, it will be used to get token."""
        redirect = self._url_redirect.format(self._port)
        self.browser.open(self._url_auth.format(self._app_id, redirect))
        self._start_server()
        try:
            while True:
                self.server.handle_request()
        except _Authorization as auth:
            self.code = auth.code

    def _start_server(self):
        """Start web server to listen for response with auth code."""
        self.server = _AuthorizationServer('localhost', self._port)

    def _fetch_token(self):
        if not hasattr(self, 'code'):
            raise DeezerAuthError('You must fetch code before fetching token')

        """Fetch temporary auth token if you has auth code."""
        url = self._url_token.format(self._app_id, self._secret, self.code)
        response = json.loads(requests.get(url).text)

        if 'access_token' in response:
            self.token = response['access_token']
        else:
            raise DeezerAuthError('Cant get token from deezer')

    def _fetch_user(self):
        """Fetch info about logged in user. It heppens on token check.
        Info stored in self._user
        """
        if not self.check_token():
            raise DeezerAuthError('Cant fetch user info due failed'
                                  ' token check')


class _AuthorizationServer(http.server.HTTPServer):

    def __init__(self, host, port):
        http.server.HTTPServer.__init__(self, (host, port),
                                        _AuthorizationHandler)

    def handle_error(self, request, client_address):
        """Disable the default error handling."""
        raise


class _AuthorizationHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Read access_token and use an exception
        to kill the server listening...
        """
        if self.path.startswith('/authfinish?'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<script>close()</script>Thanks!'
                             b' You may now close this window.')
            raise _Authorization(re.search('code=([^&]+)', self.path).group(1))

        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Disable the default logging."""
        pass


class _Authorization(Exception):
    """
    this exception will be raised on successfull authorization
    """
    def __init__(self, code):
        self.code = code


class DeezerAuthError(Exception):
    pass
