import pytest
import pprint
from dztoolset.printer import Printer


class TestPrinter(object):

    def setup(self):
        self.printer = Printer()
        self.test_phrase = 'Test printing!'
        self.test_object = {'field1': 'value1', 'field2': 'value2'}

    def test_printer_defaults(self):
        assert not self.printer.silent
        assert isinstance(self.printer.pp, pprint.PrettyPrinter)

    def test_print(self, capsys):
        self.printer.print(self.test_phrase)
        out, err = capsys.readouterr()
        assert out == self.test_phrase+'\n'

    def test_print_silent(self, capsys):
        self.printer.silent = True
        self.printer.print(self.test_phrase)
        out, err = capsys.readouterr()
        assert out == ''
