import os
from typing import Dict, List
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

    def test_get_list_of_scenarios(self, mocker):
        test_sc_1_name = 'pl_test_1'
        test_sc_1_data = {'data': 'test_value_1'}
        test_sc_2_name = 'pl_test_2'
        test_sc_2_data = {'data': 'test_value_2'}
        config_data = {
            'system': {'data': 'value'},
            'auth': {'data': 'value'},
            test_sc_1_name: test_sc_1_data,
            test_sc_2_name: test_sc_2_data,
        }
        mocker.patch.object(DeezerConfig, 'get', return_value=config_data)

        scenarios = self.sc.get_list_of_scenarios()

        DeezerConfig.get.assert_called_once()
        assert isinstance(scenarios, List)
        for sc_name in scenarios:
            assert isinstance(sc_name, str)
        assert len(scenarios) == 2
        assert test_sc_1_name in scenarios
        assert test_sc_2_name in scenarios

    def test__check_scenario_name_valid(self):
        valid_name1 = 'pl_test'
        invalid_name1 = 'test_pl'
        invalid_name2 = '123'
        assert self.sc._check_scenario_name_valid(valid_name1)
        assert not self.sc._check_scenario_name_valid(invalid_name1)
        assert not self.sc._check_scenario_name_valid(invalid_name2)
        with pytest.raises(DeezerScenarioError):
            assert not self.sc._check_scenario_name_valid(
                invalid_name1, raise_exception=True
            )

    def test_get_scenario_name_by_index(self, mocker):
        cs_count = 10
        sc_name_tpl = 'pl_test_{0}'
        scenarios = [sc_name_tpl.format(n) for n in range(cs_count)]
        mocker.patch.object(DeezerScenario, 'get_list_of_scenarios',
                            return_value=scenarios)

        for n in range(cs_count):
            assert (self.sc.get_scenario_name_by_index(n)
                    == sc_name_tpl.format(n))

        with pytest.raises(DeezerScenarioError):
            self.sc.get_scenario_name_by_index(cs_count)

    def test_get_scenario_index_by_name(self, mocker):
        cs_count = 10
        sc_name_tpl = 'pl_test_{0}'
        wrong_name = 'wrong_name'
        scenarios = [sc_name_tpl.format(n) for n in range(cs_count)]
        mocker.patch.object(DeezerScenario, 'get_list_of_scenarios',
                            return_value=scenarios)

        for n in range(cs_count):
            name = sc_name_tpl.format(n)
            assert self.sc.get_scenario_index_by_name(name) == n

        with pytest.raises(DeezerScenarioError):
            self.sc.get_scenario_index_by_name(wrong_name)
