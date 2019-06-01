import unittest
import datetime

from pyexchange.okex.utils import *


class TestUtils(unittest.TestCase):
    def test_get_the_due(self):
        print(get_the_due("quarter"))

    def test_get_instrument_id(self):
        print(get_instrument_id("etc_usd", "this_week"))

    # def test_get_the_quarter(self):
    #     print(utils.get_the_quarter(datetime.datetime.now()))
