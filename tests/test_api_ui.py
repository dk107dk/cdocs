from cdocs.cdocs import Cdocs
import unittest

PATH = "/Users/davidkershaw/dev/cdocs/docs"
ROOTNAME = "apiui"
ROOT = PATH + "/" + ROOTNAME

class ApiUiTests(unittest.TestCase):

    noise = True
    def _print(self, text:str) -> None:
        if self.noise:
            print(text)

    def test_index(self):
        self._print(f"ApiUiTests.test_index")
        cdocs = Cdocs(ROOT)
        doc = cdocs.get_doc("/v1/index.html")
        self._print(f"ApiUiTests.test_index: doc: {doc}")

