import os
import pytest
import pytest_mock
from dztoolset.deezertool import DeezerTool
from dztoolset.deezerauth import DeezerAuth
from dztoolset.deezerapi import DeezerApi
from dztoolset.deezerconfig import DeezerConfig

assert callable(pytest_mock.mocker)


class TestDeezerTool(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        self.config = DeezerConfig(self.config_path)
        self.tool = DeezerTool(self.config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.config = None
        self.tool = None

    def test_init_instance(self):
        assert isinstance(self.tool.config, DeezerConfig)
        assert isinstance(self.tool.auth, DeezerAuth)
        assert isinstance(self.tool.api, DeezerApi)

    def test_user_prop(self, mocker):
        user_data = {"userdata": "data"}
        mocker.patch.object(DeezerAuth, 'user', return_value=user_data)

        user = self.tool.user()

        assert user == user_data
        DeezerAuth.user.assert_called_once()
