from dztoolset.deezerapi import DeezerApi
import requests


class MockResponse(object):

    def __init__(self):
        self.text = ''


class TestDeezerApi(object):

    def setup_class(self):
        self.token = 'test_token'
        self.base_url = 'http://api.deezer.com'
        self.test_uri = '/test-request'
        self.limit_results_per_request = 500
        self.test_params = {"param1": "value1"}
        self.test_params_after_add_required = {
            "param1": "value1",
            "access_token": self.token,
            "limit": self.limit_results_per_request
        }

    def setup(self):
        self.api = DeezerApi()
        self.api.token = self.token

    def teardown(self):
        self.api = None

    def test_init_api(self):
        assert self.api._base_url == self.base_url
        assert (self.api._limit_results_per_request
                == self.limit_results_per_request)

    def test_get_request_single(self, mocker):
        mock_response = MockResponse()
        mock_response.text = '{"test_data":"test"}'
        mocker.patch('requests.get', return_value=mock_response)

        data = self.api.get_request(self.test_uri, 'single', self.test_params)
        requests.get.assert_called_once_with(
            self.base_url+self.test_uri,
            self.test_params_after_add_required
        )
        assert data == {"test_data": "test"}
