import os
import pytest
import dztoolset.dzshuffled_cli as dz_cli


class TestDzshuffledCli(object):

    def setup_class(self):
        self.config_path = './tests/testcfg.ini'

    def setup(self):
        with pytest.raises(SystemExit):
            dz_cli.main([], self.config_path)

    def teardown(self):
        if os.path.isfile(self.config_path):
            os.remove(self.config_path)

    def test_show_list_of_scenarios(self, capsys):
        assert os.path.isfile(self.config_path)
        with pytest.raises(SystemExit):
            dz_cli.main(['-l'], self.config_path)
        out, err = capsys.readouterr()
        assert 'pl_example' in out
