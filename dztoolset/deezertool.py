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

    def __init__(self, config_path):
        self._valid_scenario_types = ['shuffled']
        self._limit_items_delete = 500
        self._myplaylists = None

        self.config = DeezerConfig(config_path)
        self.auth = DeezerAuth()
        self.api = DeezerApi()
        self.auth.set_params(self.config.get('system', 'port'),
                             self.config.get('auth', 'secret'),
                             self.config.get('auth', 'app_id'),
                             self.config.get('auth', 'token'))
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

    def get_my_playlists(self, forced: bool = False):
        """Request all playlists from Deezer and cache it.

        On next calls playlists will be returned from cache.
        For forced request pass forced param.
        """
        if forced or not self._allplaylists:
            self._myplaylists = self.api.get_request('/user/me/playlists',
                                                     'list')

        return self._allplaylists

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

    def create_playlist(self, title: str):
        """Create playlist with title in your Deezer library.
        Return id of new playlist
        """
        uri = '/user/{0}/playlists'.format(self.user['id'])
        response = self.api.post_request(uri, 'single', {'title': title})
        new_playlist_id = response['id']
        return new_playlist_id

    def remove_playlist(self, id):
        """Remove playlist from your library by id.
        It will not warning you or ask, so think carefully.
        Return bool
        """
        uri = '/playlist/{0}'.format(id)
        response = self.api.delete_request(uri, 'single')
        return response

    def purge_playlist(self, id):
        """Remove all tracks from playlist by id.
        It will not warning you or ask, so think carefully.
        """
        uri = '/playlist/{0}/tracks'.format(id)
        track_ids = [track['id'] for track in self.get_tracks_from_playlist(id)]

        for chank in self._split_list_by_chanks(track_ids,
                                                self._limit_items_delete):
            self.api.delete_request(uri, 'single', {'songs': ','.join(chank)})

    def add_tracks_to_playlist(self, track_ids: List[int], playlist_id: int):
        """Add tracks by ids to playlist, return bool."""
        uri = '/playlist/{0}/tracks'.format(playlist_id)
        response = self.api.post_request(
            uri, 'single', {'songs': ','.join(track_ids)}
        )
        return response

    def set_playlist_desctiption(self, playlist_id: int, desctiption: str):
        """Set description to playlist with id from self.target_playlist_id"""
        uri = '/playlist/{0}'.format(playlist_id)
        self.api.post_request(uri, 'single', {'description': desctiption})

    def _split_list_by_chanks(self, list: List, chank_size: int):
        """Generator splits list by chnks of chank_size elements."""
        for i in range(0, len(items_list), limit):
            yield list[i:i+limit]

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
