import json
from typing import Dict, List, Union
import http.server
import webbrowser
import re

import requests

class DeezerAuth(object):
    """Authorization in Deezer.

    1. Fetching auth code for app with asking you for permission
    For getting answer, will be started web server on port from config.

    2. With code fetching temporary auth token. This token you must
    attach with each request to Deezer API
    """

    URL_AUTH = ('https://connect.deezer.com/oauth/auth.php'
                '?app_id={0}&redirect_uri={1}'
                '&perms=basic_access,manage_library,delete_library')
    ULR_TOKEN = ('https://connect.deezer.com/oauth/access_token.php'
                 '?app_id={0}&secret={1}&code={2}&output=json')
    URL_REDIRECT = 'http://localhost:{0}/authfinish'
    URL_CHECK_TOKEN = 'http://api.deezer.com/user/me?access_token={0}'

    def __init__(self):
        self.user = None
        self.token = ''

    def get_token(self):
        return self.token

    def set_params(self, port, secret, app_id, token=''):
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
        self.port = int(port)
        self.secret = secret
        self.app_id = app_id
        self.token = token

    def set_token(self, token):
        """Set auth token to use it."""
        self.token = token

    def authorize(self):
        """Authorize and get token."""
        if not self.app_id or not self.secret:
            raise DeezerAuthError(
                'You cant get authorization token without app_id '
                'and secret. Fill it in config file or write there '
                'valid token.'
            )
        self.fetch_code()
        self.fetch_token()

    def fetch_code(self):
        """Fetch auth app code, it will be used to get token."""
        redirect = self.URL_REDIRECT.format(self.port)
        webbrowser.open(self.URL_AUTH.format(self.app_id, redirect))
        self.start_server()
        try:
            while True:
                self.server.handle_request()
        except _Authorization as auth:
            self.code = auth.code

    def start_server(self):
        """Start web server to listen for response with auth code."""
        self.server = _AuthorizationServer('localhost', self.port)

    def fetch_token(self):
        """Fetch temporary auth token if you has auth code."""
        url = self.ULR_TOKEN.format(self.app_id, self.secret, self.code)
        response = json.loads(requests.get(url).text)

        if 'access_token' in response:
            self.token = response['access_token']
        else:
            raise DeezerAuthError('Cant get token from deezer')

    def check_token(self):
        """Check auth token, fetching user info, return bool"""
        url = self.URL_CHECK_TOKEN.format(self.token)
        response = json.loads(requests.get(url).text)

        if 'error' in response:
            return False
        elif 'type' in response and response['type'] == 'user':
            self.user = response
            return True
        else:
            raise DeezerAuthError('Cant check auth token')

    def fetch_user(self):
        """Fetch info about logged in user. It heppens on token check.
        Info stored in self.user
        """
        if not self.check_token():
            raise DeezerAuthError('Cant fetch user info due failed'
                                      ' token check')

    def get_user(self) -> Dict:
        """Return Dict with user info"""
        if self.user is None:
            self.fetch_user()

        return self.user

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