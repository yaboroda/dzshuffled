import os
import pytest
from typing import Dict
from dztoolset.deezerconfig import DeezerConfig


class TestDeezerConfig(object):

    def setup(self):
        self.path = './tests/testcfg.ini'
        with pytest.raises(SystemExit):
            DeezerConfig(self.path)
        self.cfg = DeezerConfig(self.path)

    def teardown(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

    def test_default_data(self):
        # assert data is not empty Dict
        assert self.cfg.get()
        assert isinstance(self.cfg.get(), Dict)
