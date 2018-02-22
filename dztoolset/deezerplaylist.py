from typing import Dict, List, Union
from random import shuffle

from dztoolset.deezertool import DeezerTool


class DeezerPlaylist(object):
    """Manage Deezer playlists"""

    def __init__(self, config_path):
        self._dztool = DeezerTool(config_path)

    def make_shuffled_playlist(self, title: str, source_pls: List,
                                limit: int):
        """Create shuffled playlist with `title`.

        If it exests then purge it from tracks,
        then populate it from your playlists wich titles listed
        in `source_pls`, shufflig them before it
        """

        print('Resetting playlist {0}'.format(title))

        # reset playlist by title and get its id
        target_playlist_id = self._reset_playlist_by_title(title)
        self._dztool.set_playlist_desctiption(
            target_playlist_id,
            'Resetted '+datetime.today().strftime('%H:%M %d.%m.%Y')
        )

        # check if playlists from source_pls presence in library
        # find all tracks from playlists from source_pls,
        # suffle it and cut to limit, then shove to target playlist
        self.check_for_absence_of_playlists(source_pls, True)
        playlists = self.get_playlists_by_titles(source_pls)

        print('Finding all tracks from playlists: '
              + ', '.join([pl['title'] for pl in self.playlists]))

        tracks = set()
        duplicates_count = 0
        tracks_count = 0

        for pl in playlists:
            for track in self._dztool.get_tracks_from_playlist(pl['id']):
                tracks_count += 1
                if track['id'] not in tracks:
                    tracks.add(track['id'])
                else:
                    duplicates_count += 1

        print('Found {0} tracks'.format(tracks_count))

        if duplicates_count > 0:
            print('Rid of {0} duplicates, {1} tracks left'
                  .format(duplicates_count, len(tracks)))

        tracks = list(tracks)

        print('Shuffling')
        shuffle(tracks)
        tracks = tracks[:limit]

        print('Adding {0} tracks to playlist {1}'
              .format(str(len(self.tracks)), title))

        self._dztool.add_tracks_to_playlist(tracks, target_playlist_id)

        print('Done')

        return self

    def get_playlists_by_titles(self, titles: Union[List, str]):
        """Get all playlists with title in list or same as string"""

        if isinstance(titles, str):
            titles = [titles]

        playlists = [pl for pl in self._dztool.get_my_playlists()
                     if pl['title'] in titles]
        return playlists

    def check_for_absence_of_playlists(self, target_titles: List[str],
                                        raise_exception: bool = False):
        """Check if playlists with title absence in library.

        Returns list of missing titles or raise exception.
        If all titles presence return empty list.
        """
        all_titles = [pl['title'] for pl in self._dztool.get_my_playlists()]

        missing_titles = [title for title in target_titles
                          if title not in all_titles]

        if missing_titles and raise_exception:
            raise DeezerPlaylistError(
                'Cant find playlists: "{0}"'
                .format('", "'.join(missing_titles))
            )
        else:
            return missing_titles

    def reset_playlist_by_title(self, title: str):
        """Find playlist by title and remove all tracks from it.

        If there is several pl with title, it will remove them all
        and create one new.
        If there is no pl with title, it will create one.
        Return cleared or created playlists id
        """

        # find all playlists by title
        playlists = self.get_playlists_by_titles(title)

        # if there is more then one, remove it and create new
        if len(playlists) > 1:
            for pl in playlists:
                self._dztool.remove_playlist(pl['id'])
            target_playlist_id = self._dztool.create_playlist(title)

        # if there is only one, delete all tracks from it
        elif len(playlists) == 1:
            target_playlist_id = playlists[0]['id']
            self._dztool.purge_playlist(self.target_playlist_id)

        # if there is no one, create new
        else:
            target_playlist_id = self._dztool.create_playlist(title)

        return target_playlist_id

        def _check_scenario_name_valid(self, scenario_name: str,
                                      raise_exception: bool = False):
            """Check if scenario_name is valid name for scenario, return bool

            If raise_exception is True, then instad of returning False
            it will raise exception.
            """
            check = bool(re.search('^pl_', scenario_name))

            if raise_exception and not check:
                raise Exception('Invalid scenario name: "{}"'.format(scenario_name))
            else:
                return check

    def _rid_of_duplicates(self, list_of_dicts: List[Dict],
                                       field: str):
        """Remove duplicates from list_of_dicts,
        comparig them by field argument.
        """
        new_list = []
        unique_vals = []

        for el in list_of_dicts:
            if el[field] not in unique_vals:
                unique_vals.append(el[field])
                new_list.append(el)

        return new_list


class DeezerPlaylistError(Exception):
    pass
