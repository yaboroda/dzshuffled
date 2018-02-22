from typing import Dict, List, Union


class DeezerPlaylist(object):
    """Manage Deezer playlists"""

    def __init__(self, dztool):
        self._dztool = dztool
        self._allplaylists = None

    def get_all_playlists(self, forced: bool = False):
        """Request all playlists from Deezer and cache it.

        On next calls playlists will be returned from cache.
        For forced request pass forced param.
        """
        if forced or not self._allplaylists:
            self._allplaylists = sefl._dztool.get_playlists()

        return self._allplaylists

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
        self.check_for_presence_of_playlists(source_pls, True)
        self.filter_playlists_by_titles(source_pls)

        print('Finding all tracks from playlists: '
              + ', '.join([pl['title'] for pl in self.playlists]))

        self.find_tracks_by_playlists()

        tracks_count = len(self.tracks)
        print('Found {0} tracks'.format(str(tracks_count)))

        # rid of duplicates
        self.rid_of_double_tracks()
        new_tracks_count = len(self.tracks)
        tracks_count_delta = tracks_count - new_tracks_count

        if tracks_count_delta > 0:
            print('Rid of {0} duplicates, {1} tracks left'
                  .format(tracks_count_delta, new_tracks_count))

        print('Shuffling')
        self.shuffle_tracks()
        self.filter_tracks_by_limit(limit)

        print('Adding {0} tracks to playlist {1}'
              .format(str(len(self.tracks)), title))

        self.add_tracks_to_playlist(self.target_playlist_id)

        print('Done')

        return self

    def get_playlists_by_titles(self, titles: Union[List, str]):
        """Get all playlists with title in list or same as string"""

        if isinstance(titles, str):
            titles = [titles]

        playlists = [pl for pl in self.get_all_playlists()
                     if pl['title'] in titles]
        return playlists

    def check_for_presence_of_playlists(self, target_titles: List[str],
                                        raise_exception: bool = False):
        """Check if playlist with title present in self.playlists"""
        all_titles = [pl['title'] for pl in self.get_all_playlists()]

        missing_titles = [title for title in target_titles
                          if title not in all_titles]

        if not missing_titles:
            return True

        # if reach here, title was not found
        elif raise_exception:
            raise DeezerPlaylistError(
                'Cant find playlists: "{0}"'
                .format('", "'.join(missing_titles))
            )
        else:
            return False

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


class DeezerPlaylistError(Exception):
    pass
