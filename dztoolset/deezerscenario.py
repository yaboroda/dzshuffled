import re
from typing import Dict
from dztoolset.deezerplaylist import DeezerPlaylist


class DeezerScenario(object):
    """Manages and executes scenarios from config."""

    def __init__(self, config):
        self.config = config
        self._dzplaylist = DeezerPlaylist(config)
        self._scenario_types = {
            'shuffled': self._exec_shuffled_scenario
        }

    def check_and_update_token(self):
        self._dzplaylist.check_and_update_token()

    def exec_scenario(self, scenario: str):
        """Execute scenrio from config by its name."""
        self._check_scenario_name_valid(scenario, True)

        scenario_config = self.config.get(scenario)

        self._scenario_types[scenario_config['type']](scenario_config)

        # if 'type' not in scenario_config or not scenario_config['type'] \
        #         or scenario_config['type'] not in self._valid_scenario_types:
        #     raise DeezerScenarioError('Scenario config section must'
        #                               ' contain valid type option')

    def get_list_of_scenarios(self):
        """Get list of scenarios names from config, return List of str"""
        scenarios = [key for key, val in self.config.get().items()
                     if self._check_scenario_name_valid(key)]

        return scenarios

    def get_scenario_name_by_index(self, n: int):
        """Get scenarios name by it order number in config, return str"""
        scenarios = self.get_list_of_scenarios()
        if len(scenarios) > n:
            return scenarios[n]
        else:
            raise DeezerScenarioError(
                'There is no scenario number {0}. Max number is {1}'
                .format(n, len(scenarios)-1)
            )

    def get_scenario_index_by_name(self, scenario: str):
        """Get scenario order number by it name, return int."""
        scenarios = self.get_list_of_scenarios()
        if scenario in scenarios:
            return scenarios.index(scenario)
        else:
            raise DeezerScenarioError('There is no scenario "{0}"'
                                      .format(scenario))

    def get_scenario_config(self, scenario: str):
        """Get scenario config, return Dict."""
        if self._check_scenario_name_valid(scenario, True):
            return self.config.get(scenario)

    def _exec_shuffled_scenario(self, scenario_config: Dict):
        if 'title' not in scenario_config or not scenario_config['title']:
            raise DeezerScenarioError('Scenario config section must'
                                      ' contain title option')
        else:
            title = scenario_config['title']

        if 'source' not in scenario_config or not scenario_config['source']:
            raise DeezerScenarioError('Scenario config section must'
                                      ' contain source option')
        else:
            source_pls = scenario_config['source'].split(', ')

        if 'limit' in scenario_config:
            limit = int(scenario_config['limit'])
        else:
            limit = None

        self._dzplaylist.make_shuffled_playlist(title, source_pls, limit)

        return self

    def _check_scenario_name_valid(self, scenario_name: str,
                                   raise_exception: bool = False):
        """Check if scenario_name is valid name for scenario, return bool

        If raise_exception is True, then instad of returning False
        it will raise exception.
        """
        check = bool(re.search('^pl_', scenario_name))

        if raise_exception and not check:
            raise DeezerScenarioError('Invalid scenario name: "{}"'
                                      .format(scenario_name))
        else:
            return check


class DeezerScenarioError(Exception):
    pass
