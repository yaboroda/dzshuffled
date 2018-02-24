import pprint


class Printer(object):
    """All messages in this package prints with this class.

    If you want to silence it, just set silent prop to True
    """

    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        self.silent = False

    def print(self, text):
        if not self.silent:
            print(text)

    def pprint(self, text):
        if not self.silent:
            self.pp.pprint(text)
