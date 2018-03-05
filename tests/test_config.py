import pytest
import os
import configparser
from dztoolset.config import Config


class MockPrinter(object):

    def __init__(self):
        self.print_pool = []

    def print(self, text):
        self.print_pool.append(text)


class TestConfig(object):

    def setup(self):
        self.path = './tests/testcfg.ini'
        self.default_data = {'section': {'test_option': 'test_value'}}
        with pytest.raises(SystemExit):
            Config(self.path, default_data=self.default_data)
        self.cfg = Config(self.path, default_data=self.default_data)

    def teardown(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

    def test_creating_file(self):
        """Test that config file creating and correct."""
        assert os.path.isfile(self.path)

        cfg2 = configparser.ConfigParser()
        cfg2.read(self.path)
        assert cfg2.get('section', 'test_option') == 'test_value'

    def test_printing(self):
        """Test print message on new file creating"""
        os.remove(self.path)
        test_printer = MockPrinter()
        with pytest.raises(SystemExit):
            Config(self.path, default_data=self.default_data,
                   printer=test_printer)
            assert len(test_printer.print_pool) == 1

    def test_create_config_from_default_data(self):
        """Tests that config will be created with default data
        if it is not providet for constructor
        """
        os.remove(self.path)
        with pytest.raises(SystemExit):
            Config(self.path)
        cfg = Config(self.path)

        assert cfg.get(), 'Empty default dataset'

    def test_get_list_of_sections(self):
        assert self.cfg.sections() == list(self.default_data.keys())

    def test_get_option(self):
        """Test getting options value."""
        assert (self.cfg.get('section', 'test_option')
                == self.default_data['section']['test_option'])

    def test_get_section(self):
        """Test getting section."""
        assert self.cfg.get('section') == self.default_data['section']

    def test_get_all(self):
        """Test getting whole config."""
        assert self.cfg.get() == self.default_data

    def test_set(self):
        """Test setting options value and updating config file."""
        new_value = '123'
        self.cfg.set('section', 'test_option', new_value)
        assert self.cfg.get('section', 'test_option') == new_value

        cfg2 = configparser.ConfigParser()
        cfg2.read(self.path)
        assert cfg2.get('section', 'test_option') == new_value

    def test_errors(self):
        section = 'new_test_section'
        option = 'new_test_option'

        with pytest.raises(configparser.NoSectionError):
            self.cfg.get(section, option)

        with pytest.raises(configparser.NoOptionError):
            self.cfg.get('section', option)

    def test_set_with_adding_section(self):
        """Test add value to non-existing section"""
        section = 'new_test_section'
        option = 'new_test_option'
        value = '123'

        # assert that there is no such section
        with pytest.raises(configparser.NoSectionError):
            self.cfg.get(section, option)

        # set new sections value and assert it
        self.cfg.set(section, option, value)
        assert self.cfg.get(section, option) == value
