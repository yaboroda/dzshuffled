import re
from random import shuffle
from typing import Dict, List, Union
from datetime import datetime

from dztoolset.deezerconfig import DeezerConfig
from dztoolset.deezerauth import DeezerAuth
from dztoolset.deezerapi import DeezerApi


class DeezerTool(object):
    """This class manages playlists in your Deezer library.
    All actions related only to playlists and tracks, that added to it
    """

    def __init__(self, config: DeezerConfig, auth: DeezerAuth,
                 api: DeezerApi):
        self._valid_scenario_types = ['shuffled']
        self._limit_tracks = 1000
        self._limit_items_delete_per_request = 500

        self.config = config
        self.auth = auth
        self.auth.set_params(config.get('system', 'port'),
                             config.get('auth', 'secret'),
                             config.get('auth', 'app_id'),
                             config.get('auth', 'token'))
        self.api = api
        self.api.token = config.get('auth', 'token')

    @property
    def user(self):
        """Get info about current user, return Dict."""
        return self.auth.user

    def check_and_update_token(self):
        """Check auth token and update it if not valid."""
        if not self.auth.check_token():
            self._update_token()
        return self

    def get_all_play_lists(self):
        """Fetch info about all playlists, return list of Dicts."""
        playlists = self.api.get_request('/user/me/playlists', 'list')
        return playlists

    def get_tracks_from_playlist(self, playlist_id: int):
        uri = '/playlist/{0}/tracks'.format(playlist_id)
        tracks = self.api.get_request(uri, 'list')
        return tracks

    def _update_token(self):
        """Authorize in Deezer and write new token in config file."""
        self.auth.authorize()

        if self.auth.check_token():
            self.config.set('auth', 'token', self.auth.token)
            self.api.token = self.config.get('auth', 'token')
        else:
            raise DeezerToolError('Cant verify new token')

        return self

    

    def find_tracks_by_playlists(self):
        """Fetch info about all tracks, listed in playlists from
        self.playlists and store it in self.tracks.
        """
        self.tracks = []
        for pl in self.playlists:
            tracks = self.get_tracks_from_playlist(pl['id'])
            self.tracks += tracks

        return self

    def shuffle_tracks(self):
        """Shuffle self.tracks."""
        shuffle(self.tracks)
        return self

    def filter_tracks_by_limit(self, limit: int = None):
        """Left only first `limit` items from self.tracks,
        removing the rest. If limit is None
        than limit getting from self._limit_tracks.
        """
        if limit is None:
            limit = self._limit_tracks

        self.tracks = self.tracks[:limit]
        return self

    def create_playlist(self, title: str):
        """Create playlist with title in your Deezer library."""
        uri = '/user/{0}/playlists'.format(self.user['id'])
        response = self.api.post_request(uri, 'single', {'title': title})
        self.new_playlist_id = response['id']
        return self

    def remove_playlist_by_id(self, id):
        """Remove playlist from your library by id.

        It will not warning you or ask, so think carefully
        """
        uri = '/playlist/{0}'.format(id)
        self.api.delete_request(uri, 'single')
        return self

    def purge_playlist_by_id(self, id):
        """Remove all tracks from playlist by id.

        It will not warning you or ask, so think carefully.
        """
        uri = '/playlist/{0}/tracks'.format(id)
        groups = self.get_string_of_ids_by_groups(
            self.tracks,
            self._limit_items_delete_per_request
        )

        for track_ids in groups:
            self.api.delete_request(uri, 'single', {'songs': track_ids})

    def purge_playlist_by_title(self, title):
        """Remove all tracks from all playlists with this title.

        It will not warning you or ask, so think carefully
        """
        (self.find_all_play_lists()
            .filter_playlists_by_titles(title)
            .find_tracks_by_playlists())

        for pl in self.playlists:
            self.purge_playlist_by_id(pl['id'])

    def remove_playlist_by_title(self, title: str):
        """Remove all playlists from your library with this title.

        It will not warning you or ask, so think carefully
        """
        self.find_all_play_lists()
        self.filter_playlists_by_titles([title])

        for pl in self.playlists:
            self.remove_playlist_by_id(pl['id'])

        self.playlists = []
        return self

    def add_tracks_to_playlist(self, id):
        """Add tracks from self.tracks to playlist with this id,
        return bool.
        """
        uri = '/playlist/{0}/tracks'.format(id)
        track_ids = self.get_string_of_ids(self.tracks)
        response = self.api.post_request(uri, 'single', {'songs': track_ids})
        return response

    def add_tracks_to_new_playlist(self) -> bool:
        """Add tracks from self.tracks to playlist that was just created.

        (it takes id from self.new_playlist_id)
        """
        return self.add_tracks_to_playlist(self.new_playlist_id)

    def set_playlists_desctiption(self, desctiption):
        """Set description to playlist with id from self.target_playlist_id"""
        uri = '/playlist/{0}'.format(self.target_playlist_id)
        self.api.post_request(uri, 'single', {'description': desctiption})

    

    def get_string_of_ids(self, items_list: List[Dict]):
        """Get string of id of items in list."""
        items_ids = ','.join([str(item['id']) for item in items_list])
        return items_ids

    def get_string_of_ids_by_groups(self, items_list: List[Dict], limit: int):
        """Get list of strings of id of items in list,
        splitted by limit in each string, return List of str
        """
        groups = []
        for i in range(0, len(items_list), limit):
            groups.append(self.get_string_of_ids(items_list[i:i+limit]))

        return groups

    def check_scenario_name_valid(self, scenario_name: str,
                                  raise_exception: bool = False):
        """Check if scenario_name is valid name for scenario, return bool

        If raise_exception is True, then instad of returning False
        it will raise exception.
        """
        check = bool(re.search('^pl_', scenario_name))

        if raise_exception and not check:
            raise DeezerToolError('Invalid scenario name: "{}"'
                                  .format(scenario_name))
        else:
            return check

    def exec_scenario(self, scenario):
        """Execute scenrio from config by its name."""
        self.check_scenario_name_valid(scenario, True)

        scenario_config = self.config.get(scenario)

        if 'type' not in scenario_config or not scenario_config['type'] \
                or scenario_config['type'] not in self._valid_scenario_types:
            raise DeezerToolError('Scenario config section must'
                                  ' contain valid type option')

        if 'title' not in scenario_config or not scenario_config['title']:
            raise DeezerToolError('Scenario config section must'
                                  ' contain title option')
        else:
            title = scenario_config['title']

        if 'source' not in scenario_config or not scenario_config['source']:
            raise DeezerToolError('Scenario config section must'
                                  ' contain source option')
        else:
            source_pls = scenario_config['source'].split(', ')

        if 'limit' in scenario_config:
            limit = int(scenario_config['limit'])
        else:
            limit = None

        self.reset_shuffled_playlist(title, source_pls, limit)

        return self

    def get_list_of_scenarios(self):
        """Get list of scenarios names from config, return List of str"""
        scenarios = [key for key, val in self.config.get().items()
                     if self.check_scenario_name_valid(key)]

        return scenarios

    def get_scenario_name_by_index(self, n: int):
        """Get scenarios name by it order number in config, return str"""
        scenarios = self.get_list_of_scenarios()
        if len(scenarios) > n:
            return scenarios[n]
        else:
            raise DeezerToolError(
                'There is no scenario number {0}. Max number is {1}'
                .format(n, len(scenarios)-1)
            )

    def get_scenario_index_by_name(self, scenario):
        """Get scenario order number by it name, return int."""
        scenarios = self.get_list_of_scenarios()
        if scenario in scenarios:
            return scenarios.index(scenario)
        else:
            raise DeezerToolError('There is no scenario "{0}"'
                                  .format(scenario))

    def get_scenario_config(self, scenario: str):
        """Get scenario config, return Dict."""
        if self.check_scenario_name_valid(scenario, True):
            return self.config.get(scenario)

    def rid_of_double_tracks(self):
        """Remove duplicated items from self.tracks."""
        self.tracks = self.rid_of_doubles_in_list_of_dict(self.tracks)
        return self

    def rid_of_doubles_in_list_of_dict(self, list_of_dict: List[Dict],
                                       field: str = 'id'):
        """Remove duplicates from list_of_dict,
        comparig them by field argument.
        """
        new_list = []
        unique_vals = []

        for el in list_of_dict:
            if el[field] not in unique_vals:
                unique_vals.append(el[field])
                new_list.append(el)

        return new_list


class DeezerToolError(Exception):
    pass
