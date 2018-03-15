import pytest
import os
from typing import List
import pytest_mock
from dztoolset.deezerplaylist import DeezerPlaylist
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
