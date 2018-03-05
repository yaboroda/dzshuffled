from dztoolset.deezerauth import DeezerAuth


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
