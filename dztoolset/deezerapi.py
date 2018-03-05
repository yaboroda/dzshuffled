import json
from typing import Dict

import requests


class DeezerApi(object):
    """Send requests to Deezer api and get answers as dicts
    before use, set valid auth token into self.token
    """

    def __init__(self):
        self._base_url = 'http://api.deezer.com'
        self._limit_results_per_request = 500

    def get_request(self, uri: str, response_type: str = 'single',
                    params: Dict = {}):
        """Send GET request to Deezer API, return Dict or bool

        Keyword arguments:
        uri -- address without domain
        response_type -- 'single' or 'list'
        params -- Dict with parameters to add to request (default {})
        """
        params = self._add_required_params(params)
        response = requests.get(self._base_url + uri, params)
        return self._prepare_response(response, response_type)

    def get_request_strict(self, url: str, response_type: str = 'single'):
        """Send GET request strictly by url, return bool or Dict

        Url include domain and all parameters
        response_type -- 'single' or 'list'
        """
        response = requests.get(url)
        return self._prepare_response(response, response_type)

    def post_request(self, uri: str, response_type: str = 'single',
                     params: Dict = {}):
        """Send POST request to Deezer API, return bool or Dict.

        Keyword arguments:
        uri -- address without domain
        response_type -- 'single' or 'list'
        params -- Dict with parameters to add to request (default {})
        """
        params = self._add_required_params(params)
        response = requests.post(self._base_url + uri, params)
        return self._prepare_response(response, response_type)

    def delete_request(self, uri: str, response_type: str = 'single',
                       params: Dict = {}):
        """Send DELETE request to Deezer API, return bool or Dict.

        Keyword arguments:
        uri -- address without domain
        response_type -- 'single' or 'list'
        params -- Dict with parameters to add to request (default {})
        """
        params = self._add_required_params(params)
        uri += '?'+'&'.join([f'{key}={val}' for key, val in params.items()])

        response = requests.delete(self._base_url + uri)
        return self._prepare_response(response, response_type)

    def _process_api_error(self, error_data: Dict):
        """Raise exception by error sesponse from Deezer.

        Keyword arguments:
        error_data -- Dict with info about errror with keys:
            'message' - error message, str
            'code'    - error code, optional, str
        """
        code = error_data['code'] if 'code' in error_data else None
        raise DeezerApiRequestError(error_data['message'], code)

    def _prepare_response(self, response: requests.models.Response,
                          response_type: str):
        """Get data from response object.

        Keyword arguments:
        response -- response object from requests lib
        response_type -- 'list' or 'single'
        if 'list' then getting all paginated data with additional requests
        """
        response = json.loads(response.text)

        if isinstance(response, bool):
            return response

        if 'error' in response:
            return self._process_api_error(response['error'])

        if response_type == 'list':
            if 'data' not in response:
                raise DeezerApiError('Error occured on request'
                                     ' to Deezer api')

            nextPages = []
            if 'next' in response:
                nextPages = self.get_request_strict(response['next'], 'list')

            return response['data'] + nextPages

        elif response_type == 'single':
            return response

        else:
            raise DeezerApiError(
                'Unknown response type "{0}",'
                ' it can be either single or list'.format(response_type)
            )

    def _add_required_params(self, params: Dict):
        """Add token and limit to requests param. Return Dict"""
        if 'access_token' not in params:
            params['access_token'] = self.token

        if 'limit' not in params:
            params['limit'] = self._limit_results_per_request

        return params


class DeezerApiError(Exception):
    pass


class DeezerApiRequestError(DeezerApiError):
    def __init__(self, message, code):
        codeStr = 'code '+str(code) if code else ''
        exc_message = 'Deezer API error {1}: {0}'.format(message, codeStr)
        super(DeezerApiError, self).__init__(exc_message)
