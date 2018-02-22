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
        track_ids = [track['id'] for track
                     in self.get_tracks_from_playlist(id)]

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

    def _update_token(self):
        """Authorize in Deezer and write new token in config file."""
        self.auth.authorize()

        if self.auth.check_token():
            self.config.set('auth', 'token', self.auth.token)
            self.api.token = self.config.get('auth', 'token')
        else:
            raise DeezerToolError('Cant verify new token')

        return self


class DeezerToolError(Exception):
    pass
