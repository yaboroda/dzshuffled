import pytest
import os
from typing import List
import pytest_mock
from dztoolset.deezerplaylist import DeezerPlaylist, DeezerPlaylistError
from dztoolset.deezerconfig import DeezerConfig
from dztoolset.deezertool import DeezerTool
from dztoolset.printer import Printer

assert callable(pytest_mock.mocker)


class TestDeezerPlaylist(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'
        self.test_playlists_set = [
            {"id": "0", "title": "playlist_0"},
            {"id": "1", "title": "playlist_1"},
            {"id": "2", "title": "playlist_2"},
            {"id": "3", "title": "playlist_3"},
            {"id": "4", "title": "playlist_4"},
            {"id": "5", "title": "playlist_5"},
            {"id": "6", "title": "playlist_double"},
            {"id": "7", "title": "playlist_double"},
        ]

    def setup(self):
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        config = DeezerConfig(self.config_path)
        self.pl = DeezerPlaylist(config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.pl = None

    def test_init_instance(self):
        assert isinstance(self.pl._dztool, DeezerTool)
        assert isinstance(self.pl.printer, Printer)

    def test_check_and_update_token(self, mocker):
        mocker.patch.object(DeezerTool, 'check_and_update_token')

        self.pl.check_and_update_token()

        DeezerTool.check_and_update_token.assert_called_once()

    def test_get_playlists_by_titles_single(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        title = self.test_playlists_set[1]['title']
        assert isinstance(title, str)

        data = self.pl.get_playlists_by_titles(title)

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(data, List)
        assert len(data) == 1
        assert data[0] == self.test_playlists_set[1]

    def test_get_playlists_by_titles_list(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        titles = [
            self.test_playlists_set[1]['title'],
            self.test_playlists_set[3]['title']
        ]

        data = self.pl.get_playlists_by_titles(titles)

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(data, List)
        assert len(data) == 2
        assert self.test_playlists_set[1] in data
        assert self.test_playlists_set[3] in data

    def test_get_playlists_by_titles_no_match(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        title = 'no_existing_title'

        data = self.pl.get_playlists_by_titles(title)

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(data, List)
        assert len(data) == 0

    def test_check_for_absence_of_playlists_list(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        non_existent_title_1 = 'non_existent_title_1'
        non_existent_title_2 = 'non_existent_title_2'

        titles = [
            self.test_playlists_set[1]['title'],
            non_existent_title_1,
            non_existent_title_2,
            self.test_playlists_set[2]['title'],
        ]

        missing_titles = self.pl.check_for_absence_of_playlists(titles)

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(missing_titles, List)
        assert len(missing_titles) == 2
        assert non_existent_title_1 in missing_titles
        assert non_existent_title_2 in missing_titles

    def test_check_for_absence_of_playlists_str(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        non_existent_title = 'non_existent_title'

        missing_titles = self.pl.check_for_absence_of_playlists(
            non_existent_title
        )

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(missing_titles, List)
        assert len(missing_titles) == 1
        assert missing_titles == [non_existent_title]

    def test_check_for_absence_of_playlists_no_match(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        titles = [
            self.test_playlists_set[1]['title'],
            self.test_playlists_set[2]['title'],
        ]

        missing_titles = self.pl.check_for_absence_of_playlists(titles)

        DeezerTool.get_my_playlists.assert_called_once()
        assert isinstance(missing_titles, List)
        assert len(missing_titles) == 0

    def test_check_for_absence_of_playlists_exception(self, mocker):
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)

        non_existent_title_1 = 'non_existent_title_1'
        non_existent_title_2 = 'non_existent_title_2'

        titles = [
            self.test_playlists_set[1]['title'],
            non_existent_title_1,
            non_existent_title_2,
            self.test_playlists_set[2]['title'],
        ]

        with pytest.raises(DeezerPlaylistError) as error_info:
            self.pl.check_for_absence_of_playlists(
                titles, raise_exception=True
            )

        DeezerTool.get_my_playlists.assert_called_once()
        error_message = error_info.value.args[0]
        assert non_existent_title_1 in error_message
        assert non_existent_title_2 in error_message
        assert self.test_playlists_set[1]['title'] not in error_message
        assert self.test_playlists_set[2]['title'] not in error_message

    def test_reset_playlist_by_title_single_match(self, mocker):
        """When there is single playlist with such title"""
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)
        mocker.patch.object(DeezerTool, 'remove_playlist')
        mocker.patch.object(DeezerTool, 'purge_playlist')
        mocker.patch.object(DeezerTool, 'create_playlist')

        self.pl.reset_playlist_by_title(self.test_playlists_set[2]['title'])

        DeezerTool.get_my_playlists.assert_called_once()
        DeezerTool.purge_playlist.assert_called_once_with(
            self.test_playlists_set[2]["id"]
        )
        DeezerTool.remove_playlist.assert_not_called()
        DeezerTool.create_playlist.assert_not_called()

    def test_reset_playlist_by_title_no_match(self, mocker):
        """When there is no playlist with such title"""
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)
        mocker.patch.object(DeezerTool, 'remove_playlist')
        mocker.patch.object(DeezerTool, 'purge_playlist')
        mocker.patch.object(DeezerTool, 'create_playlist')

        non_existent_title = 'non_existent_title'

        self.pl.reset_playlist_by_title(non_existent_title)

        DeezerTool.get_my_playlists.assert_called_once()
        DeezerTool.purge_playlist.assert_not_called()
        DeezerTool.remove_playlist.assert_not_called()
        DeezerTool.create_playlist.assert_called_once_with(non_existent_title)

    def test_reset_playlist_by_title_multiple_matches(self, mocker):
        """When there is several playlists with such title"""
        mocker.patch.object(DeezerTool, 'get_my_playlists',
                            return_value=self.test_playlists_set)
        mocker.patch.object(DeezerTool, 'remove_playlist')
        mocker.patch.object(DeezerTool, 'purge_playlist')
        mocker.patch.object(DeezerTool, 'create_playlist')

        self.pl.reset_playlist_by_title(self.test_playlists_set[6]['title'])

        DeezerTool.get_my_playlists.assert_called_once()
        DeezerTool.purge_playlist.assert_not_called()
        DeezerTool.remove_playlist.assert_has_calls([
            mocker.call(self.test_playlists_set[6]["id"]),
            mocker.call(self.test_playlists_set[7]["id"]),
        ])
        DeezerTool.create_playlist.assert_called_once_with(
            self.test_playlists_set[6]['title']
        )

    def test_make_shuffled_playlist(self, mocker):
        target_playlist_title = 'title'
        target_playlist_id = 11
        src_playlists = [
            self.test_playlists_set[1],
            self.test_playlists_set[3],
        ]
        src_playlists_titles = [
            pl["title"] for pl in src_playlists
        ]
        src_tracks_1 = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ]
        src_tracks_2 = [
            {"id": "4"},
            {"id": "3"},
            {"id": "5"},
        ]
        # getting list of unique ids from both lists
        src_tracks_ids = list(set([
            t["id"] for t in (src_tracks_1 + src_tracks_2)
        ]))
        mocker.patch.object(DeezerPlaylist, 'reset_playlist_by_title',
                            return_value=target_playlist_id)
        mocker.patch.object(DeezerTool, 'set_playlist_desctiption')
        mocker.patch.object(DeezerPlaylist, 'check_for_absence_of_playlists')
        mocker.patch.object(DeezerPlaylist, 'get_playlists_by_titles',
                            return_value=src_playlists)
        mocker.patch.object(DeezerTool, 'get_tracks_from_playlist',
                            side_effect=[src_tracks_1, src_tracks_2])
        mocker.patch.object(DeezerTool, 'add_tracks_to_playlist')

        self.pl.make_shuffled_playlist(
            target_playlist_title,
            src_playlists_titles,
            100
        )

        (DeezerPlaylist.reset_playlist_by_title
            .assert_called_once_with(target_playlist_title))
        DeezerTool.set_playlist_desctiption.assert_called_once()
        (DeezerPlaylist.check_for_absence_of_playlists
            .assert_called_once_with(src_playlists_titles, True))
        (DeezerPlaylist.get_playlists_by_titles
            .assert_called_once_with(src_playlists_titles))
        DeezerTool.get_tracks_from_playlist.assert_has_calls([
            mocker.call(pl["id"]) for pl in src_playlists
        ])

        # due to shuffled order of ids, get list of ids from mock call args,
        # and assert its length and each of src_tracks_ids
        DeezerTool.add_tracks_to_playlist.assert_called_once()
        (name, args, kwargs) = DeezerTool.add_tracks_to_playlist.mock_calls[0]
        (ids, pl_id_) = args
        assert len(ids) == len(src_tracks_ids)
        for id in src_tracks_ids:
            assert id in ids

    def test_make_shuffled_playlist_with_limit(self, mocker):
        limit = 3
        target_playlist_title = 'title'
        target_playlist_id = 11
        src_playlists = [
            self.test_playlists_set[1],
            self.test_playlists_set[3],
        ]
        src_playlists_titles = [
            pl["title"] for pl in src_playlists
        ]
        src_tracks_1 = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ]
        src_tracks_2 = [
            {"id": "4"},
            {"id": "3"},
            {"id": "5"},
        ]
        # getting list of unique ids from both lists
        src_tracks_ids = list(set([
            t["id"] for t in (src_tracks_1 + src_tracks_2)
        ]))
        mocker.patch.object(DeezerPlaylist, 'reset_playlist_by_title',
                            return_value=target_playlist_id)
        mocker.patch.object(DeezerTool, 'set_playlist_desctiption')
        mocker.patch.object(DeezerPlaylist, 'check_for_absence_of_playlists')
        mocker.patch.object(DeezerPlaylist, 'get_playlists_by_titles',
                            return_value=src_playlists)
        mocker.patch.object(DeezerTool, 'get_tracks_from_playlist',
                            side_effect=[src_tracks_1, src_tracks_2])
        mocker.patch.object(DeezerTool, 'add_tracks_to_playlist')

        self.pl.make_shuffled_playlist(
            target_playlist_title,
            src_playlists_titles,
            limit
        )

        (DeezerPlaylist.reset_playlist_by_title
            .assert_called_once_with(target_playlist_title))
        DeezerTool.set_playlist_desctiption.assert_called_once()
        (DeezerPlaylist.check_for_absence_of_playlists
            .assert_called_once_with(src_playlists_titles, True))
        (DeezerPlaylist.get_playlists_by_titles
            .assert_called_once_with(src_playlists_titles))
        DeezerTool.get_tracks_from_playlist.assert_has_calls([
            mocker.call(pl["id"]) for pl in src_playlists
        ])

        # due to shuffled order of ids, get list of ids from mock call args,
        # and assert its length and each of src_tracks_ids
        DeezerTool.add_tracks_to_playlist.assert_called_once()
        (name, args, kwargs) = DeezerTool.add_tracks_to_playlist.mock_calls[0]
        (ids, pl_id_) = args
        assert len(ids) == limit
        for id in ids:
            assert id in src_tracks_ids
