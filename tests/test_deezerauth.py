import webbrowser
import requests
from http.server import HTTPServer
import pytest_mock
import pytest
from dztoolset.deezerauth import (
    DeezerAuth, DeezerAuthError, _AuthorizationHandler, _AuthorizationServer,
    _Authorization
)

assert callable(pytest_mock.mocker)


class MockResponse(object):

    def __init__(self):
        self.text = ''


class MockWfile(object):

    def __init__(self):
        self.write_data = None

    def write(self, data):
        self.write_data = data


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

    def test__fetch_token(self, mocker):
        mock_response = MockResponse()
        mock_response.text = f'{{"access_token": "{self.token}"}}'

        mocker.patch('requests.get', return_value=mock_response)

        self.auth.code = self.test_code
        self.auth._fetch_token()

        url = self.auth._url_token.format(
            self.app_id, self.secret, self.test_code
        )
        requests.get.assert_called_once_with(url)

    def test__fetch_token_error_no_code(self):
        assert not hasattr(self.auth, 'code')
        with pytest.raises(DeezerAuthError):
            self.auth._fetch_token()

    def test__fetch_token_error_fetching(self, mocker):
        mock_response = MockResponse()
        mock_response.text = '{"error": "error_message"}'

        mocker.patch('requests.get', return_value=mock_response)

        self.auth.code = self.test_code
        with pytest.raises(DeezerAuthError):
            self.auth._fetch_token()

    def test__AuthorizationHandler(self, mocker):
        mocker.patch.object(_AuthorizationHandler, '__init__',
                            return_value=None)
        mocker.patch.object(_AuthorizationHandler, 'send_response')
        mocker.patch.object(_AuthorizationHandler, 'send_header')
        mocker.patch.object(_AuthorizationHandler, 'end_headers')

        auth_handler = _AuthorizationHandler()
        auth_handler.path = f'/authfinish?code={self.test_code}'
        mock_wfile = MockWfile()
        auth_handler.wfile = mock_wfile

        with pytest.raises(_Authorization) as auth_exception_info:
            auth_handler.do_GET()
        assert auth_exception_info.value.code == self.test_code

        _AuthorizationHandler.send_response.assert_called_once()
        _AuthorizationHandler.send_header.assert_called_once_with(
            'Content-Type', 'text/html'
        )
        _AuthorizationHandler.end_headers.assert_called_once()
        assert '<script>close()</script>' in str(mock_wfile.write_data)

    def test__AuthorizationHandler_error404(self, mocker):
        mocker.patch.object(_AuthorizationHandler, '__init__',
                            return_value=None)
        mocker.patch.object(_AuthorizationHandler, 'send_response')
        mocker.patch.object(_AuthorizationHandler, 'send_error')

        auth_handler = _AuthorizationHandler()
        auth_handler.path = f'/some_path'

        auth_handler.do_GET()
        _AuthorizationHandler.send_error.assert_called_once_with(404)

    def test_check_token(self, mocker):
        mock_response = MockResponse()
        mock_response.text = '{"type": "user", "data": "value"}'
        mocker.patch('requests.get', return_value=mock_response)

        self.auth.token = self.token
        check = self.auth.check_token()

        assert check
        assert isinstance(check, bool)

        url = self.auth._url_check_token.format(self.token)
        requests.get.assert_called_once_with(url)

    def test_check_token_fails(self, mocker):
        mock_response = MockResponse()
        mock_response.text = '{"error": "error_data"}'
        mocker.patch('requests.get', return_value=mock_response)

        self.auth.token = self.token
        check = self.auth.check_token()

        assert not check
        assert isinstance(check, bool)

        url = self.auth._url_check_token.format(self.token)
        requests.get.assert_called_once_with(url)

    def test_check_token_error(self, mocker):
        mock_response = MockResponse()
        mock_response.text = '{"garbage_data": "data"}'
        mocker.patch('requests.get', return_value=mock_response)

        self.auth.token = self.token
        with pytest.raises(DeezerAuthError):
            self.auth.check_token()

        url = self.auth._url_check_token.format(self.token)
        requests.get.assert_called_once_with(url)
