from config import Config


class DeezerConfig(Config):
    """Config class for DeezerTool object"""

    def set_up_default_config(self):
        """Sets up default config data."""
        self.cfg['system'] = {
            'port': '8090',
            'editor': 'vim'
        }
        self.cfg['auth'] = {
            'app_id': '',
            'secret': '',
            'token': ''
        }
        self.cfg['pl_example'] = {
            'title': 'Example shuffled playlist',
            'type': 'shuffled',
            'source':
            'playlist 1, playlist 2',
            'limit': 1000
        }
