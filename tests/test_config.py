from cdocs.simple_config import SimpleConfig
import unittest

class ConfigTests(unittest.TestCase):

    noise = False
    def _print(self, text:str) -> None:
        if self.noise:
            print(text)

    def off(self) -> bool:
        return False

    def test_get_config_items(self):
        self._print(f"ConfigTests.test_get_config_items")
        if self.off(): return
        cfg = SimpleConfig()
        items = cfg.get_items("docs", ["public"])
        self._print(f"test_get_config_items: items: {items}")
        self.assertEqual( len(items), 4, msg=f"must be 3 items for docs, not {items}" )
        items = cfg.get_items("fish")
        self.assertEqual( len(items), 0, msg=f"must be 0 items for fish, not {items}" )

    def test_get_with_default(self):
        self._print(f"ConfigTests.test_get_with_default")
        if self.off(): return
        cfg = SimpleConfig()
        oh = cfg.get("fish", "bats", "yeah!")
        self._print(f"test_get_with_default: {oh}")
        self.assertEqual( oh, "yeah!", msg="must equal the default value" )

    def test_get_matching_key_for_value(self):
        self._print(f"ConfigTests.test_get_matching_key_for_value")
        if self.off(): return
        cfg = SimpleConfig()
        name = cfg.get_matching_key_for_value("docs", "/Users/davidkershaw/dev/cdocs/docs/internal")
        self._print(f"ConfigTests.test_get_matching_key_for_value: name1: {name}")
        self.assertEqual( name, "internal", msg="must equal the 'internal' root" )
        name = cfg.get_matching_key_for_value("docs", "fish")
        self._print(f"ConfigTests.test_get_matching_key_for_value: name2: {name}")
        self.assertNotEqual( name, "internal", msg="must not equal the 'internal' root" )

