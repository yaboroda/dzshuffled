import os
from unittest.mock import call, patch
import pytest
import pytest_mock
import dztoolset.dzshuffled_cli as dz_cli
from dztoolset.printer import Printer
from dztoolset.deezerconfig import DeezerConfig

assert callable(pytest_mock.mocker)


class TestDzshuffledCli(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'
        self.default_config_data = {
            'system': {
                'port': '8090',
                'editor': 'vim'
            },
            'auth': {
                'app_id': '123',
                'secret': 'test_secret',
                'token': 'test_token'
            },
            'pl_test1': {
                'title': 'Test shuffled playlist',
                'type': 'shuffled',
                'source':
                'playlist 1, playlist 2',
                'limit': '100'
            },
            'pl_test2': {
                'title': 'Test shuffled playlist 2',
                'type': 'shuffled',
                'source': 'playlist 3, playlist 4',
                'limit': '200'
            }
        }
        self.scenario_short_info = [
            '[0] pl_test1',
            '[1] pl_test2',
        ]

    def setup(self):
        assert not os.path.isfile(self.config_path)
        cfg_patcher = patch.object(
            DeezerConfig,
            '_get_default_data',
            return_value=self.default_config_data
        ).start()
        with pytest.raises(SystemExit):
            dz_cli.main([], self.config_path)
        cfg_patcher.stop()

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)

    def test_config_file_created(self):
        assert os.path.isfile(self.config_path)

    def test_show_list_of_scenarios_short(self, mocker):
        mocker.patch.object(Printer, 'print')

        # print short version, will use print method
        with pytest.raises(SystemExit):
            dz_cli.main(['-l'], self.config_path)

        Printer.print.assert_has_calls([
            call(self.scenario_short_info[0]),
            call(self.scenario_short_info[1]),
        ])

    def test_show_list_of_scenarios_verbous(self, mocker):
        mocker.patch.object(Printer, 'print')
        mocker.patch.object(Printer, 'pprint')

        # print verbouse version, will use both methods (print, pprint)
        with pytest.raises(SystemExit):
            dz_cli.main(['-lv'], self.config_path)

        Printer.print.assert_has_calls([
            call(self.scenario_short_info[0]),
            call(self.scenario_short_info[1]),
        ])

        Printer.pprint.assert_has_calls([
            call(self.default_config_data['pl_test1']),
            call(self.default_config_data['pl_test2']),
        ])

    def test_print_info_about_scenario_by_number(self, mocker):
        mocker.patch.object(Printer, 'print')
        mocker.patch.object(Printer, 'pprint')

        # will use both methods (print, pprint)
        with pytest.raises(SystemExit):
            dz_cli.main(['-i', '0'], self.config_path)

        Printer.print.assert_called_once_with(self.scenario_short_info[0])

        Printer.pprint.assert_called_once_with(
            self.default_config_data['pl_test1']
        )

    def test_print_info_about_scenario_by_name(self, mocker):
        mocker.patch.object(Printer, 'print')
        mocker.patch.object(Printer, 'pprint')

        # will use both methods (print, pprint)
        with pytest.raises(SystemExit):
            dz_cli.main(['-i', 'pl_test1'], self.config_path)

        Printer.print.assert_called_once_with('[0] pl_test1')

        Printer.pprint.assert_called_once_with(
            self.default_config_data['pl_test1']
        )