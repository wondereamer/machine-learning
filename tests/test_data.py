'''
Author: your name
Date: 2022-02-28 08:01:51
LastEditTime: 2022-03-10 22:28:04
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/data/test_data.py
'''
import os
import unittest
from pprint import pprint

from numpy import ndarray

import util

util.set_home_path_to_sys()

from ml.data.qc import ResultParser, DataParser
from ml.finance.analysis import orders_to_deals
from ml.finance.datastruct import Deal, Direction, Order, OrderStatus, TradeSide
from ml import util


class QCTest(unittest.TestCase):

    def setUp(self):
        file_path = os.path.join(util.data_path, "result.json")
        self.result = ResultParser()
        self.result.read_data(file_path)
        print('setUp...')

    def tearDown(self):
        print('tearDown...')

    def test_parse_tradebar_by_path(self):
        file_path = os.path.join(util.data_path, "20131007_trade.zip")
        parser = DataParser(util.data_path)
        bars = parser.parse_trade_bars_by_path(file_path)
        self.assertEquals(bars.columns.values.tolist(),
            ["open", "high", "low", "close", "volume"])
        self.assertEquals(821, len(bars))

    def test_parse_tradebar(self):
        name = "equity.usa.spy-minute"
        parser = DataParser(util.data_path)
        bars = parser.parse_trade_bars(name, '2013-10-07', '2013-10-08')
        self.assertEquals(bars.columns.values.tolist(),
            ["open", "high", "low", "close", "volume"])
        self.assertEquals('2013-10-07', str(bars.index[0].date()))
        self.assertEquals('2013-10-08', str(bars.index[-1].date()))
        self.assertEquals(1648, len(bars))

    def test_parse_order(self):
        orders = self.result.get_orders()
        self.assertEquals(1, orders[0].id);
        self.assertEquals(2, orders[1].id);
        self.assertEquals(3, orders[2].id);
        self.assertEquals(TradeSide.Open, orders[0].side);
        self.assertEquals(OrderStatus.Filled, orders[0].status);
        self.assertEquals(Direction.Long, orders[0].direction);

    def test_parse_indicators(self):
        file_path = os.path.join(util.data_path, "CustomIndicatorAlgorithm.json")
        self.result = ResultParser()
        self.result.read_data(file_path)
        rst = self.result.get_indicators()
        self.assertEquals(rst[0]["name"], "SMA60")
        self.assertEquals(rst[0]["info"], "SMA(60,SPY_min)")
        self.assertEquals(len(rst[0]["values"]), 1950)
        self.assertEquals(rst[1]["name"], "SMA10")
        self.assertEquals(rst[1]["info"], "SMA(10,SPY_min)")
        self.assertEquals(len(rst[1]["values"]), 1950)

    def test_align_orders_time_to_data(self):
        name = "equity.usa.spy-minute"
        parser = DataParser(util.data_path)
        bars = parser.parse_trade_bars(name, '2013-10-07', '2013-10-08')
        file_path = os.path.join(util.data_path, "result.json")
        result = ResultParser()
        result.read_data(file_path)
        orders = result.get_orders()
        for order in orders:
            print(order.create_time)
        print("----------")
        orders = result.calcu_time_aligned_orders(orders, bars)
        for order in orders:
            print(order.create_time)

if __name__ == '__main__':
    unittest.main()
