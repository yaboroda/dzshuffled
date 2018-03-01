import requests
import pytest
import pytest_mock
from unittest.mock import call
from dztoolset.deezerapi import (DeezerApi, DeezerApiError,
                                 DeezerApiRequestError)

assert callable(pytest_mock.mocker)


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

    def test_get_request_list(self, mocker):
        mock_response1 = MockResponse()
        mock_response1.text = (
            '{"data": [{"test_data1":"test1"}], "next":"next_url"}'
        )
        mock_response2 = MockResponse()
        mock_response2.text = '{"data": [{"test_data2":"test2"}]}'
        mocker.patch('requests.get',
                     side_effect=[mock_response1, mock_response2])

        data = self.api.get_request(self.test_uri, 'list', self.test_params)

        requests.get.assert_has_calls([
            call(
                self.base_url+self.test_uri,
                self.test_params_after_add_required
            ),
            call(
                'next_url'
            )
        ])
        assert data == [{"test_data1": "test1"}, {"test_data2": "test2"}]

    def test_get_request_boolean_response(self, mocker):
        mock_response = MockResponse()
        mock_response.text = 'true'
        mocker.patch('requests.get', return_value=mock_response)

        data = self.api.get_request(self.test_uri, 'single', self.test_params)
        requests.get.assert_called_once_with(
            self.base_url+self.test_uri,
            self.test_params_after_add_required
        )
        assert isinstance(data, bool)
        assert data

    def test_prepare_response_errors(self, mocker):
        mock_response1 = MockResponse()
        mock_response1.text = '{"test_data":"test"}'
        mock_response2 = MockResponse()
        mock_response2.text = (
            '{"error":{"message":"Error message", "code": "errorcode"}}'
        )
        mocker.patch('requests.get',
                     side_effect=[mock_response1, mock_response2])

        with pytest.raises(DeezerApiError):
            self.api.get_request(self.test_uri, 'list', self.test_params)

        with pytest.raises(DeezerApiRequestError):
            self.api.get_request(self.test_uri, 'list', self.test_params)

        requests.get.assert_has_calls([
            call(
                self.base_url+self.test_uri,
                self.test_params_after_add_required
            ),
            call(
                self.base_url+self.test_uri,
                self.test_params_after_add_required
            )
        ])
