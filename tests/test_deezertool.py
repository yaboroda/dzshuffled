import os
import pytest
import pytest_mock
from dztoolset.deezertool import DeezerTool, DeezerToolError
from dztoolset.deezerauth import DeezerAuth
from dztoolset.deezerapi import DeezerApi
from dztoolset.deezerconfig import DeezerConfig

assert callable(pytest_mock.mocker)


class TestDeezerTool(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'
        self.token = 'test_token'

    def setup(self):
        assert not os.path.isfile(self.config_path)
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        self.config = DeezerConfig(self.config_path)
        self.tool = DeezerTool(self.config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.config = None
        self.tool = None

    def test_init_instance(self):
        assert isinstance(self.tool.config, DeezerConfig)
        assert isinstance(self.tool.auth, DeezerAuth)
        assert isinstance(self.tool.api, DeezerApi)

    def test_user_prop(self, mocker):
        user_data = {"userdata": "data"}
        mocker.patch.object(DeezerAuth, 'user', return_value=user_data)

        user = self.tool.user()

        assert user == user_data
        DeezerAuth.user.assert_called_once()

    def test_check_and_update_token(self, mocker):
        mocker.patch.object(DeezerAuth, 'check_token',
                            side_effect=[True, False])
        mocker.patch.object(DeezerTool, '_update_token')

        self.tool.check_and_update_token()
        DeezerAuth.check_token.assert_called_once()
        DeezerTool._update_token.assert_not_called()

        DeezerAuth.check_token.reset_mock()
        self.tool.check_and_update_token()
        DeezerAuth.check_token.assert_called_once()
        DeezerTool._update_token.assert_called_once()

    def test__update_token(self, mocker):
        assert self.tool.config.get('auth', 'token') == ''
        assert self.tool.api.token == ''

        mocker.patch.object(DeezerAuth, 'authorize')
        mocker.patch.object(DeezerAuth, 'check_token', return_value=True)
        self.tool.auth.token = self.token

        self.tool._update_token()

        DeezerAuth.authorize.assert_called_once()
        DeezerAuth.check_token.assert_called_once()
        assert self.tool.config.get('auth', 'token') == self.token
        assert self.tool.api.token == self.token

    def test__update_token_error(self, mocker):
        assert self.tool.config.get('auth', 'token') == ''
        assert self.tool.api.token == ''

        mocker.patch.object(DeezerAuth, 'authorize')
        mocker.patch.object(DeezerAuth, 'check_token', return_value=False)
        self.tool.auth.token = self.token

        with pytest.raises(DeezerToolError):
            self.tool._update_token()

        DeezerAuth.authorize.assert_called_once()
        DeezerAuth.check_token.assert_called_once()
        assert self.tool.config.get('auth', 'token') == ''
        assert self.tool.api.token == ''

    def test_get_my_playlists_request(self, mocker):
        playlist_data_1 = {"data": "value1"}
        mocker.patch.object(DeezerApi, 'get_request',
                            return_value=playlist_data_1)

        data = self.tool.get_my_playlists()

        assert data == playlist_data_1
        DeezerApi.get_request.assert_called_once_with('/user/me/playlists',
                                                      'list')

    def test_get_my_playlists_cached(self, mocker):
        playlist_data_1 = {"data": "value1"}
        mocker.patch.object(DeezerApi, 'get_request')
        self.tool._myplaylists = playlist_data_1

        data = self.tool.get_my_playlists()

        assert data == playlist_data_1
        DeezerApi.get_request.assert_not_called()

    def test_get_my_playlists_forced(self, mocker):
        playlist_data_1 = {"data": "value1"}
        playlist_data_2 = {"data": "value1"}
        mocker.patch.object(DeezerApi, 'get_request',
                            return_value=playlist_data_2)
        self.tool._myplaylists = playlist_data_1

        data = self.tool.get_my_playlists(forced=True)

        assert data == playlist_data_2
        DeezerApi.get_request.assert_called_once_with(
            '/user/me/playlists', 'list'
        )

    def test_get_tracks_from_playlist(self, mocker):
        tracks_data = {"data": "value"}
        playlist_id = 77
        mocker.patch.object(DeezerApi, 'get_request', return_value=tracks_data)

        data = self.tool.get_tracks_from_playlist(playlist_id)

        assert data == tracks_data
        DeezerApi.get_request.assert_called_once_with(
            f'/playlist/{playlist_id}/tracks', 'list'
        )

    def test_create_playlist(self, mocker):
        user_id = 11
        new_playlist_id = 77
        playlist_title = 'some_title'
        mocker.patch.object(
            DeezerApi, 'post_request',
            return_value={"id": new_playlist_id}
        )
        mocker.patch.object(
            DeezerTool, 'user', new_callable=mocker.PropertyMock,
            return_value={"id": user_id}
        )
        data = self.tool.create_playlist(playlist_title)

        assert data == new_playlist_id
        DeezerApi.post_request.assert_called_once_with(
            f'/user/{user_id}/playlists',
            'single',
            {"title": playlist_title}
        )

    def test_remove_playlist(self, mocker):
        playlist_id = 77
        mocker.patch.object(DeezerApi, 'delete_request', return_value=True)

        result = self.tool.remove_playlist(playlist_id)

        assert result
        assert isinstance(result, bool)
        DeezerApi.delete_request.assert_called_once_with(
            f'/playlist/{playlist_id}', 'single'
        )

    def test_purge_playlist(self, mocker):
        tracks_data = [
            {"id": 3},
            {"id": 5},
            {"id": 8},
            {"id": 34},
            {"id": 46},
        ]
        tracks_ids_str = '3,5,8,34,46'
        playlist_id = 77
        mocker.patch.object(DeezerApi, 'get_request', return_value=tracks_data)
        mocker.patch.object(DeezerApi, 'delete_request')

        self.tool.purge_playlist(playlist_id)

        DeezerApi.get_request.assert_called_once_with(
            f'/playlist/{playlist_id}/tracks', 'list'
        )

        DeezerApi.delete_request.assert_called_once_with(
            f'/playlist/{playlist_id}/tracks', 'single',
            {"songs": tracks_ids_str}
        )

    def test_purge_playlist_by_chunks(self, mocker):
        self.tool._limit_items_delete = 3
        tracks_data = [
            {"id": 3},
            {"id": 5},
            {"id": 8},
            {"id": 34},
            {"id": 46},
        ]
        tracks_ids_str_1 = '3,5,8'
        tracks_ids_str_2 = '34,46'
        playlist_id = 77
        mocker.patch.object(DeezerApi, 'get_request', return_value=tracks_data)
        mocker.patch.object(DeezerApi, 'delete_request')

        self.tool.purge_playlist(playlist_id)

        DeezerApi.get_request.assert_called_once_with(
            f'/playlist/{playlist_id}/tracks', 'list'
        )

        DeezerApi.delete_request.assert_has_calls([
            mocker.call(
                f'/playlist/{playlist_id}/tracks', 'single',
                {"songs": tracks_ids_str_1}
            ),
            mocker.call(
                f'/playlist/{playlist_id}/tracks', 'single',
                {"songs": tracks_ids_str_2}
            ),
        ])

    def test_add_tracks_to_playlist(self, mocker):
        playlist_id = 77
        track_ids = [3, 7, 14]
        track_ids_str = '3,7,14'
        mocker.patch.object(DeezerApi, 'post_request')

        self.tool.add_tracks_to_playlist(track_ids, playlist_id)

        DeezerApi.post_request.assert_called_once_with(
            f'/playlist/{playlist_id}/tracks',
            'single',
            {"songs": track_ids_str}
        )

    def test_set_playlist_desctiption(self, mocker):
        playlist_id = 77,
        description = 'Some text',
        mocker.patch.object(DeezerApi, 'post_request')

        self.tool.set_playlist_desctiption(playlist_id, description)

        DeezerApi.post_request.assert_called_once_with(
            f'/playlist/{playlist_id}',
            'single',
            {"description": description}
        )
