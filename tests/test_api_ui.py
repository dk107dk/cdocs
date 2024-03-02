from cdocs.cdocs import Cdocs
import unittest
import logging

PATH = "docs"
ROOTNAME = "apiui"
ROOT = PATH + "/" + ROOTNAME


class ApiUiTests(unittest.TestCase):

    noise = False

    def _print(self, text: str) -> None:
        if self.noise:
            print(text)

    def test_index_html(self):
        logging.info("ApiUiTests.test_index")
        cdocs = Cdocs(ROOT)
        doc = cdocs.get_doc("/v1/index.html")
        logging.info(f"ApiUiTests.test_index: doc: {doc}")
