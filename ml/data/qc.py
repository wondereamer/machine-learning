'''
Author: your name
Date: 2022-02-28 07:52:42
LastEditTime: 2022-03-05 20:57:19
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/data/qc.py
'''
import json
import datetime
import pandas as pd
from pathlib import Path
from dateutil import parser
from typing import Dict
from dateutil import parser

from ml.finance.datastruct import Direction, OrderStatus, Order, OrderType, TradeSide
from ml.log import dlog as log

def parse_tradebar(path):
    with open(path, "r") as file:
        headers = ["open", "high", "low", "close", "volume"]
        fname = Path(path).stem
        date = parser.parse(fname.split('_')[0])
        def custom_data_parser(offset):
            time = date + datetime.timedelta(milliseconds=int(offset))
            return time
        price_data = pd.read_csv(path, header=None, names=headers,
            index_col=0, date_parser=custom_data_parser)
    return price_data

def parse_strategy_output(path):
    data = json.load(open(path, "r"))
    return data


class ResultParser(object):

    def __init__(self) -> None:
        self._data = None
        self.transactions = None
        self.benchmark = None
        self._orders = None

    def read_data(self, path):
        self._data = json.load(open(path, "r"))

    def get_orders(self):
        if self._orders is not None:
            return self._orders
        self._orders = []
        for d_order in self._data["Orders"].values():
            order = self._parse_order(d_order)
            if order is not None:
                self._orders.append(order)
        return self._orders

    def _parse_order(self, d_order: Dict):
        assert d_order["Direction"] != 3
        try:
            status = OrderStatus(d_order["Status"])
        except Exception as e:
            log.warn("Ignore order with unsupported status: {0}".format(d_order))
            return None
        log.warn(d_order["LastFillTime"])
        order_type = OrderType(d_order["Type"])
        direction = Direction(d_order["Direction"])
        side = TradeSide.Open if d_order["Quantity"] > 0 else TradeSide.Close

        order = Order(
            d_order["Id"], parser.parse(d_order["LastFillTime"]), d_order["Symbol"]["Value"],
            None, order_type, side, direction, d_order["Price"], d_order["Quantity"],
            status, 1
        )
        return order
        
    def get_transactions(self):
        if self._transactions is not None:
            return self._transactions
        self._transactions = list(filter(
                lambda x: x.status in [OrderStatus.Filled, OrderStatus.PartiallyFilled],
                self.get_orders()
            ))
        return self._transactions

    def _parse_benchmark(self):
        self.benchmark = self._data["Charts"]["Benchmark"]











if __name__ == '__main__':
    pass