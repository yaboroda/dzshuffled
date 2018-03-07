import pytest_mock
import pytest
from dztoolset.deezerauth import DeezerAuth, DeezerAuthError


class TestDeezerAuth(object):

    def setup_class(self):
        self.token = 'test_token'
        self.port = 8090
        self.secret = 'test_secret'
        self.app_id = 123

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
