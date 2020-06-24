import sys
import os
# sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)),'src')))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

import unittest


class Example(unittest.TestCase):
    def test_basic_thing(self):
        self.assertTrue(1==1)

if __name__ == "__main__":
    unittest.main()