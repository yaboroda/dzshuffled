import pytest
import os
from dztoolset.deezerplaylist import DeezerPlaylist
from dztoolset.deezerconfig import DeezerConfig
from dztoolset.deezertool import DeezerTool
from dztoolset.printer import Printer


class TestDeezerPlaylist(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        config = DeezerConfig(self.config_path)
        self.pl = DeezerPlaylist(config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.pl = None

    def test_init_instance(self):
        assert isinstance(self.pl._dztool, DeezerTool)
        assert isinstance(self.pl.printer, Printer)
