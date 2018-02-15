import configparser
import os
import sys


class Config(object):
    """Manage info from config .ini file."""

    def __init__(self, path: str):
        """Read file from path or create new one.

        Keyword arguments:
        path -- path to config file
        """
        self.path = path

        if not os.path.isfile(path):
            self.create_new_config_file()
            print('New config file was created in {}'.format(path))
            sys.exit()
        else:
            self.read()

    def set_up_default_config(self):
        """Sets up default config data,
        it should be redeclared in subclass.
        """
        self.cfg['config'] = {'example_config': 'example_value'}

    def create_new_config_file(self):
        """Create new config file from default config."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.cfg = configparser.ConfigParser()
        self.set_up_default_config()
        self.write()

    def write(self):
        """Write current config to file."""
        with open(self.path, 'w') as configfile:
            self.cfg.write(configfile)

    def read(self):
        """Read config from file, replacing current data."""
        self.cfg = configparser.ConfigParser()
        self.cfg.read(self.path)

    def get(self, section: str = None, option: str = None):
        """Get info from config.

        if option is None, will return section as dictionary
        if section is None, will return whole config as dictionary

        Keyword arguments:
        section -- section name of config (default None)
        option -- option name of config (default None)
        """
        if option is None and section is None:
            return self.get_all()
        elif option is None:
            return self.get_section(section)
        else:
            return self.get_option(section, option)

    def get_all(self):
        """Will return whole config as dictionary."""
        data = {}
        for cfg_section in self.cfg.sections():
            data[cfg_section] = {}
            for key, val in self.cfg.items(cfg_section):
                data[cfg_section][key] = val
        return data

    def get_section(self, section: str):
        """Will return section data as dictionary."""
        data = {}
        for key, val in self.cfg.items(section):
            data[key] = val
        return data

    def get_option(self, section: str, option: str):
        """Will return value of config option in section."""
        return self.cfg.get(section, option)

    def set(self, section: str, option: str, value):
        """Set option value and write change to config file.

        Keyword arguments:
        section -- section name of config (default None)
        option -- option name of config (default None)
        value -- value to put in option
        """
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)

        self.cfg.set(section, option, value)
        self.write()

    def sections(self):
        """Get list of sections in config."""
        return self.cfg.sections()
