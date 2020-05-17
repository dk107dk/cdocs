from cdocs.simple_config import SimpleConfig
import unittest

class ConfigTests(unittest.TestCase):

    def test_get_config_items(self):
        print(f"ConfigTests.test_get_config_items")
        cfg = SimpleConfig()
        items = cfg.get_items("docs", ["public"])
        print(f"test_get_config_items: items: {items}")
        self.assertEqual( len(items), 2, msg="must be 2 items for docs" )
        items = cfg.get_items("fish")
        self.assertEqual( len(items), 0, msg="must be 0 items for fish" )

    def test_get_with_default(self):
        print(f"ConfigTests.test_get_with_default")
        cfg = SimpleConfig()
        oh = cfg.get_with_default("fish", "bats", "yeah!")
        print(f"test_get_with_default: {oh}")
        self.assertEqual( oh, "yeah!", msg="must equal the default value" )


