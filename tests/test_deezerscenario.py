import os
from typing import Dict
import pytest
from dztoolset.deezerscenario import DeezerScenario
from dztoolset.deezerplaylist import DeezerPlaylist
from dztoolset.deezerconfig import DeezerConfig


class TestDezeerScanario(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        config = DeezerConfig(self.config_path)
        self.sc = DeezerScenario(config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.sc = None

    def test_init_instance(self):
        assert isinstance(self.sc._dzplaylist, DeezerPlaylist)
        assert isinstance(self.sc.config, DeezerConfig)
        assert isinstance(self.sc._scenario_types, Dict)