import pytest
import os
import configparser
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
        """Assert that config file creating and correct"""
        assert os.path.isfile(self.path)

        cfg2 = configparser.ConfigParser()
        cfg2.read(self.path)
        assert cfg2.get('config', 'example_option') == 'example_value'

    def test_get_option(self):
        assert (self.cfg.get('config', 'example_option')
                == self.default_data['config']['example_option'])

    def test_get_section(self):
        assert self.cfg.get('config') == self.default_data['config']

    def test_get_all(self):
        assert self.cfg.get() == self.default_data

    def test_set(self):
        new_value = '123'
        self.cfg.set('config', 'example_option', new_value)
        assert self.cfg.get('config', 'example_option') == new_value

        cfg2 = configparser.ConfigParser()
        cfg2.read(self.path)
        assert cfg2.get('config', 'example_option') == new_value
