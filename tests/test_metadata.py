from cdocs.context_metadata import ContextMetadata
import unittest
import os

class MetadataTests(unittest.TestCase):

    noise = False
    def _print(self, text:str) -> None:
        if self.noise:
            print(text)

    def off(self) -> bool:
        return False

    def test_formats(self):
        self._print(f"MetadataTests.test_formats")
        if self.off(): return
        metadata = ContextMetadata()
        formats = metadata.formats["public"]
        self._print(f"MetadataTests.test_formats: formats are: {formats}")
        self.assertEqual(2, len(formats), msg=f'formats for public must be 2, not {len(formats)}')
        self.assertIn("xml", formats, msg=f"formats must include xml: {formats}")
        users = metadata.uses_format["xml"]
        self._print(f"MetadataTests.test_formats: users are: {users}")
        self.assertEqual(2, len(users), msg=f'users of xml must be 2, not {len(users)}')
        self.assertIn("public", users, msg=f"users of xml must include public: {users}")


