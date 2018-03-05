from dztoolset.config import Config


class DeezerConfig(Config):
    """Config class for DeezerTool object"""

    def _get_default_data(self):
        """Sets up default config data."""
        data = {
            'system': {
                'port': '8090',
                'editor': 'vim'
            },
            'auth': {
                'app_id': '',
                'secret': '',
                'token': ''
            },
            'pl_example': {
                'title': 'Example shuffled playlist',
                'type': 'shuffled',
                'source':
                'playlist 1, playlist 2',
                'limit': 1000
            }
        }

        return data
