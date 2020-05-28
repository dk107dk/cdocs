from cdocs.simple_config import SimpleConfig
import unittest

class ConfigTests(unittest.TestCase):

    noise = True
    def _print(self, text:str) -> None:
        if self.noise:
            print(text)

    def test_get_config_items(self):
        self._print(f"ConfigTests.test_get_config_items")
        cfg = SimpleConfig()
        items = cfg.get_items("docs", ["public"])
        self._print(f"test_get_config_items: items: {items}")
        self.assertEqual( len(items), 2, msg="must be 2 items for docs" )
        items = cfg.get_items("fish")
        self.assertEqual( len(items), 0, msg="must be 0 items for fish" )

    def test_get_with_default(self):
        self._print(f"ConfigTests.test_get_with_default")
        cfg = SimpleConfig()
        oh = cfg.get_with_default("fish", "bats", "yeah!")
        self._print(f"test_get_with_default: {oh}")
        self.assertEqual( oh, "yeah!", msg="must equal the default value" )

    def test_get_matching_key_for_value(self):
        self._print(f"ConfigTests.test_get_matching_key_for_value")
        cfg = SimpleConfig()
        name = cfg.get_matching_key_for_value("docs", "/Users/davidkershaw/dev/cdocs/docs/internal")
        self._print(f"ConfigTests.test_get_matching_key_for_value: name1: {name}")
        self.assertEqual( name, "internal", msg="must equal the 'internal' root" )
        name = cfg.get_matching_key_for_value("docs", "fish")
        self._print(f"ConfigTests.test_get_matching_key_for_value: name2: {name}")
        self.assertNotEqual( name, "internal", msg="must not equal the 'internal' root" )

