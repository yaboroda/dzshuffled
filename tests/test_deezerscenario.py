import os
from typing import Dict
import pytest
import pytest_mock
from dztoolset.deezerscenario import DeezerScenario, DeezerScenarioError
from dztoolset.deezerplaylist import DeezerPlaylist
from dztoolset.deezerconfig import DeezerConfig

assert callable(pytest_mock.mocker)


class TestDezeerScanario(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            DeezerConfig(self.config_path)
        config = DeezerConfig(self.config_path)
        self.sc = DeezerScenario(config)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)
        self.sc = None

    def test_init_instance(self):
        assert isinstance(self.sc._dzplaylist, DeezerPlaylist)
        assert isinstance(self.sc.config, DeezerConfig)
        assert isinstance(self.sc._scenario_handlers, Dict)
        for key, method in self.sc._scenario_handlers.items():
            assert hasattr(self.sc, method)
            assert callable(getattr(self.sc, method))

    def test_check_and_update_token(self, mocker):
        mocker.patch.object(DeezerPlaylist, 'check_and_update_token')
        self.sc.check_and_update_token()
        DeezerPlaylist.check_and_update_token.assert_called_once()

    def test_exec_scenario(self, mocker):
        scenario_name = 'pl_test'
        scenario_config = {"type": "shuffled", "data": "value"}
        mocker.patch.object(DeezerScenario, '_check_scenario_name_valid')
        mocker.patch.object(DeezerConfig, 'get', return_value=scenario_config)
        mocker.patch.object(DeezerScenario, '_shuffled_scenario_handler')

        self.sc.exec_scenario(scenario_name)

        (DeezerScenario._check_scenario_name_valid
            .called_once_with(scenario_name))
        DeezerConfig.get.assert_called_once_with(scenario_name)
        (DeezerScenario._shuffled_scenario_handler
            .assert_called_once_with(scenario_config))

    def test_exec_scenario_wrong_type(self, mocker):
        scenario_name = 'pl_test'
        scenario_config = {"type": "wrong_type", "data": "value"}
        mocker.patch.object(DeezerScenario, '_check_scenario_name_valid')
        mocker.patch.object(DeezerConfig, 'get', return_value=scenario_config)
        mocker.patch.object(DeezerScenario, '_shuffled_scenario_handler')

        with pytest.raises(DeezerScenarioError):
            self.sc.exec_scenario(scenario_name)

        (DeezerScenario._check_scenario_name_valid
            .called_once_with(scenario_name))
        DeezerConfig.get.assert_called_once_with(scenario_name)
        DeezerScenario._shuffled_scenario_handler.assert_not_called()
