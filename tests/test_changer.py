from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
import unittest
import datetime
import time
import os
import logging

PATH: str = "docs/example"


class ChangerTests(unittest.TestCase):
    def test_last_change(self):
        logging.info("ChangerTests.test_last_change")
        cdocs = Cdocs(PATH)
        cdocs.track_last_change = True
        dt = cdocs.get_last_change()
        logging.info(f"Changer.test_last_change: dt: {dt}")
        lcf = cdocs._get_last_change_file_path()
        exists = os.path.exists(lcf)
        logging.info(f"ChangerTests.test_last_change: lcf: {lcf}: {exists}")
        self.assertEqual(exists, True, msg=f"there must be a last change file at {lcf}")
        self.assertIsNotNone(dt, msg="last change cannot be None")
        time.sleep(1)

        cdocs.set_last_change()
        dt2 = cdocs.get_last_change()
        self.assertNotEqual(dt, dt2, msg=f"last change: {dt} must not equal {dt2}")
        time.sleep(1)
        cdocs = Cdocs(PATH)
        cdocs.track_last_change = True
        dt3 = cdocs.get_last_change()
        self.assertEqual(dt3, dt2, msg=f"last change: {dt3} must equal {dt2}")
        cdocs.set_last_change()
        dt4 = cdocs.get_last_change()
        self.assertNotEqual(dt4, dt3, msg=f"last change: {dt4} must not equal {dt3}")
