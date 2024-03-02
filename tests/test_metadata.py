from cdocs.context_metadata import ContextMetadata
import unittest
import os
import logging


class MetadataTests(unittest.TestCase):
    def test_formats(self):
        logging.info("MetadataTests.test_formats")
        metadata = ContextMetadata()
        formats = metadata.formats["public"]
        logging.info(f"MetadataTests.test_formats: formats are: {formats}")
        self.assertEqual(
            2, len(formats), msg=f"formats for public must be 2, not {len(formats)}"
        )
        self.assertIn("xml", formats, msg=f"formats must include xml: {formats}")
        users = metadata.uses_format["xml"]
        logging.info(f"MetadataTests.test_formats: users are: {users}")
        self.assertEqual(2, len(users), msg=f"users of xml must be 2, not {len(users)}")
        self.assertIn("public", users, msg=f"users of xml must include public: {users}")
