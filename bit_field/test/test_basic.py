import unittest
import json
from .. import render
from os import path


class TestBasic(unittest.TestCase):

    def test_basic(self):
        with open(path.join(path.dirname(__file__), 'alpha.json'), 'r') as f:
            data = json.load(f)
            render(data)


if __name__ == '__main__':
    unittest.main()
