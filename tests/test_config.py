import pytest
import os
from dztoolset.config import Config


class TestConfig(object):

    def setup(self):
        self.path = './tests/testcfg.ini'
        self.default_data = {'config': {'example_option': 'example_value'}}
        with pytest.raises(SystemExit):
            Config(self.path)
        self.cfg = Config(self.path)

    def teardown(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

    def test_creating_file(self):
        assert os.path.isfile(self.path)

    def test_get_option(self):
        assert (self.cfg.get('config', 'example_option')
                == self.default_data['config']['example_option'])

    def test_get_section(self):
        assert self.cfg.get('config') == self.default_data['config']

    def test_get_all(self):
        assert self.cfg.get() == self.default_data
