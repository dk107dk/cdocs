from cdocs.simple_config import SimpleConfig
import unittest
import logging


class ConfigTests(unittest.TestCase):
    def test_get_config_items(self):
        logging.info("ConfigTests.test_get_config_items")
        cfg = SimpleConfig()
        items = cfg.get_items("docs", ["public"])
        logging.info(f"test_get_config_items: items: {items}")
        self.assertEqual(len(items), 4, msg=f"must be 3 items for docs, not {items}")
        items = cfg.get_items("fish")
        self.assertEqual(len(items), 0, msg=f"must be 0 items for fish, not {items}")

    def test_get_with_default(self):
        logging.info("ConfigTests.test_get_with_default")
        cfg = SimpleConfig()
        oh = cfg.get("fish", "bats", "yeah!")
        logging.info(f"test_get_with_default: {oh}")
        self.assertEqual(oh, "yeah!", msg="must equal the default value")

    def test_get_matching_key_for_value(self):
        logging.info("ConfigTests.test_get_matching_key_for_value")
        cfg = SimpleConfig()
        name = cfg.get_matching_key_for_value("docs", "docs/internal")
        logging.info(f"ConfigTests.test_get_matching_key_for_value: name1: {name}")
        self.assertEqual(name, "internal", msg="must equal the 'internal' root")
        name = cfg.get_matching_key_for_value("docs", "fish")
        logging.info(f"ConfigTests.test_get_matching_key_for_value: name2: {name}")
        self.assertNotEqual(name, "internal", msg="must not equal the 'internal' root")
