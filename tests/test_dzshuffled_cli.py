import os
from unittest.mock import call
import pytest
import pytest_mock
import dztoolset.dzshuffled_cli as dz_cli
from dztoolset.printer import Printer

assert callable(pytest_mock.mocker)


class TestDzshuffledCli(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            dz_cli.main([], self.config_path)

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
            call('[0] pl_example'),
        ])

    def test_show_list_of_scenarios_verbous(self, mocker):
        mocker.patch.object(Printer, 'print')
        mocker.patch.object(Printer, 'pprint')

        # print verbouse version, will use both methods (print, pprint)
        with pytest.raises(SystemExit):
            dz_cli.main(['-lv'], self.config_path)

        Printer.print.assert_called_once_with('[0] pl_example')

        Printer.pprint.assert_called_once_with({
            'title': 'Example shuffled playlist', 
            'type': 'shuffled', 
            'source': 'playlist 1, playlist 2', 'limit': '1000'
        })
