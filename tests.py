import unittest
import pybotlib
import pandas as pd

import glob
import os

class TestStringMethods(unittest.TestCase):

    def test_pybotlib(self):
        from investigator_RPA import run_robot
        run_robot()
        search_dir = "C:/Users/%s/pybotlib_logs/" % os.environ["USERNAME"]
        files = filter(os.path.isfile, glob.glob(search_dir + "*"))
        files.sort(key=lambda x: os.path.getmtime(x))
        recent_bot = files[-1]
        df = pd.read_csv(recent_bot)
        len_exceptions = df[df["message"].str.contains("ERROR")].shape[0]
        self.assertEqual(0, len_exceptions)
    
if __name__ == '__main__':
    unittest.main()
