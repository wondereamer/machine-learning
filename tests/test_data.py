'''
Author: your name
Date: 2022-02-28 08:01:51
LastEditTime: 2022-03-05 20:42:51
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/data/test_data.py
'''
import os
import unittest
from pprint import pprint

import util

util.set_test_path_to_sys()

from ml.data.qc import ResultParser, parse_tradebar
from ml.finance.analysis import orders_to_deals
from ml.finance.datastruct import Deal, Direction, Order, OrderStatus, TradeSide


class QCTest(unittest.TestCase):

    def setUp(self):
        print('setUp...')

    def tearDown(self):
        print('tearDown...')

    def test_parse_tradebar(self):
        file_path = os.path.join(util.home_path, "data", "20131010_spy_minute_trade.csv")
        bars = parse_tradebar(file_path)
        # print(bars)

    def test_parse_order(self):
        file_path = os.path.join(util.home_path, "data", "result.json")
        result = ResultParser()
        result.read_data(file_path)
        orders = result.get_orders()
        for order in orders:
            print(order)


