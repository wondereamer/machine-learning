'''
Author: your name
Date: 2022-03-05 20:05:32
LastEditTime: 2022-03-05 20:05:32
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/test_analysis.py
'''
import os
import unittest
from pprint import pprint

import util

util.set_test_path_to_sys()

from ml.finance.analysis import orders_to_deals
from ml.finance.datastruct import Deal, Direction, Order, OrderStatus, TradeSide


class AnalysisTest(unittest.TestCase):

    def setUp(self):
        print('setUp...')

    def test_orders_to_deals(self):
        def create_order(time, symbol, direction, side, price, quantity, filled):
            return Order(None, time, symbol, None, None, side, direction, price, quantity, filled, 2)

        orders = [
            create_order("t1", "ibm", Direction.Short, TradeSide.Open, 10, 1, OrderStatus.Filled),
            create_order("t0", "ibm", Direction.Long, TradeSide.Open, 10, 2, OrderStatus.Submitted),
            create_order("t2", "ibm", Direction.Long, TradeSide.Open, 10, 2, OrderStatus.Filled),
            create_order("t3", "ibm", Direction.Long, TradeSide.Open, 12, 2, OrderStatus.PartiallyFilled),
            create_order("t4", "ibm", Direction.Long, TradeSide.Close, 10, 1, OrderStatus.PartiallyFilled),
            create_order("t5", "ibm", Direction.Long, TradeSide.Close, 13, 2, OrderStatus.PartiallyFilled),
            create_order("t6", "ibm", Direction.Long, TradeSide.Close, 13, 3, OrderStatus.PartiallyFilled),
            create_order("t1", "ibm", Direction.Long, TradeSide.Open, 10, 2, OrderStatus.Filled)
        ]
        expected_deals = [
            Deal(Direction.Long, 12, 10, "t3", "t4", 1, 2),
            Deal(Direction.Long, 12, 13, "t3", "t5", 1, 2),
            Deal(Direction.Long, 10, 13, "t2", "t5", 1, 2),
            Deal(Direction.Long, 10, 13, "t2", "t6", 1, 2),
            Deal(Direction.Long, 10, 13, "t1", "t6", 2, 2)
        ]
        deals = orders_to_deals(orders)
        self.assertEquals(expected_deals, deals)
        self.assertEqual(1 * 2, expected_deals[1].profit)

    def test_orders_to_deals_when_invalid_input(self):
        def create_order(time, symbol, direction, side, price, quantity, filled):
            return Order(None, time, symbol, None, None, side, direction, price, quantity, filled, 2)

        orders = [
            create_order("t3", "ibm", Direction.Long, TradeSide.Close, 12, 2, OrderStatus.PartiallyFilled),
        ]

        with self.assertRaises(Exception):
            orders_to_deals(orders)


if __name__ == '__main__':
    unittest.main()