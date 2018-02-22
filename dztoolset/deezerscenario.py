

class DeezerScenario(object):
    """Manages and executes scenarios from config."""

    def exec_scenario(self, scenario):
        """Execute scenrio from config by its name."""
        self._check_scenario_name_valid(scenario, True)

        scenario_config = self.config.get(scenario)

        if 'type' not in scenario_config or not scenario_config['type'] \
                or scenario_config['type'] not in self._valid_scenario_types:
            raise DeezerPlaylistError('Scenario config section must'
                                      ' contain valid type option')

        if 'title' not in scenario_config or not scenario_config['title']:
            raise DeezerPlaylistError('Scenario config section must'
                                      ' contain title option')
        else:
            title = scenario_config['title']

        if 'source' not in scenario_config or not scenario_config['source']:
            raise DeezerPlaylistError('Scenario config section must'
                                      ' contain source option')
        else:
            source_pls = scenario_config['source'].split(', ')

        if 'limit' in scenario_config:
            limit = int(scenario_config['limit'])
        else:
            limit = None

        self.reset_shuffled_playlist(title, source_pls, limit)

        return self

    def get_list_of_scenarios(self):
        """Get list of scenarios names from config, return List of str"""
        scenarios = [key for key, val in self.config.get().items()
                     if self.check_scenario_name_valid(key)]

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

    def get_scenario_index_by_name(self, scenario):
        """Get scenario order number by it name, return int."""
        scenarios = self.get_list_of_scenarios()
        if scenario in scenarios:
            return scenarios.index(scenario)
        else:
            raise DeezerScenarioError('There is no scenario "{0}"'
                                      .format(scenario))

    def get_scenario_config(self, scenario: str):
        """Get scenario config, return Dict."""
        if self.check_scenario_name_valid(scenario, True):
            return self.config.get(scenario)


class DeezerScenarioError(Exception):
    pass