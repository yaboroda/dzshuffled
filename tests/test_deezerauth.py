import webbrowser
from http.server import HTTPServer
import pytest_mock
import pytest
from dztoolset.deezerauth import (
    DeezerAuth, DeezerAuthError, _AuthorizationHandler, _AuthorizationServer,
    _Authorization
)

assert callable(pytest_mock.mocker)


class TestDeezerAuth(object):

    def setup_class(self):
        self.token = 'test_token'
        self.port = 8090
        self.secret = 'test_secret'
        self.app_id = 123
        self.test_code = 'testcode'

    def setup(self):
        self.auth = DeezerAuth()
        self.auth.set_params(self.port, self.secret, self.app_id, self.token)

    def teardown(self):
        self.auth = None

    def test_created_instance(self):
        assert self.auth._port == self.port
        assert self.auth._secret == self.secret
        assert self.auth._app_id == str(self.app_id)
        assert self.auth.token == self.token

    def test_authoruze_missing_secret_error(self):
        self.auth._secret = None
        with pytest.raises(DeezerAuthError):
            self.auth.authorize()

    def test_authoruze_missing_appid_error(self):
        self.auth._app_id = None
        with pytest.raises(DeezerAuthError):
            self.auth.authorize()

    def test_authorize(self, mocker):
        mocker.patch.object(DeezerAuth, '_fetch_code')
        mocker.patch.object(DeezerAuth, '_fetch_token')

        self.auth.authorize()

        DeezerAuth._fetch_code.assert_called_once()
        DeezerAuth._fetch_token.assert_called_once()

    def test__fetch_code(self, mocker):
        url_redirect = self.auth._url_redirect.format(self.port)
        url_auth = self.auth._url_auth.format(self.app_id, url_redirect)

        mocker.patch('webbrowser.open')
        mocker.patch.object(HTTPServer, '__init__', return_value=None)

        mocker.patch.object(_AuthorizationServer, 'handle_request',
                            side_effect=_Authorization(self.test_code))

        self.auth._fetch_code()

        webbrowser.open.assert_called_once_with(url_auth)
        HTTPServer.__init__.assert_called_once()

        # get and assert arguments
        args, kwargs = HTTPServer.__init__.call_args
        assert len(args) == 3
        self_arg, (host, port), error_handler = args

        assert host == 'localhost'
        assert port == self.port
        assert error_handler == _AuthorizationHandler
        _AuthorizationServer.handle_request.assert_called_once()

        assert self.auth.code == self.test_code
