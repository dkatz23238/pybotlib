import unittest
import pybotlib
import pandas as pd

import glob
import os

# remove anything from the list that is not a file (directories, symlinks)
# thanks to J.F. Sebastion for pointing out that the requirement was a list
# of files (presumably not including directories)

class TestStringMethods(unittest.TestCase):

    def test_pybotlib(self):
        from investigator_RPA import run_robot
        run_robot()
        self.assertEqual(0, 0)

if __name__ == '__main__':
    unittest.main()
