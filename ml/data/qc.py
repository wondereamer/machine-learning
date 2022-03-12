'''
Author: your name
Date: 2022-02-28 07:52:42
LastEditTime: 2022-03-12 18:19:35
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/data/qc.py
'''
from ast import arguments
import re
import zipfile
import os
from copy import deepcopy
import json
import datetime
import pandas as pd
from io import StringIO
from pathlib import Path
from dateutil import parser
from typing import Dict, List
from dateutil import parser, tz

from ml.finance.datastruct import Direction, OrderStatus, Order, OrderType, Period, TradeSide, MarketData
from ml.log import dlog as log

class DataParser(object):

    def __init__(self, data_home):
        self._data_home = data_home

    def parse_trade_bars_by_path(self, path):
        headers = ["open", "high", "low", "close", "volume"]
        fname = Path(path).stem
        date = self._fname_to_date(fname)
        def custom_data_parser(offset):
            time = date + datetime.timedelta(milliseconds=int(str(offset)))
            return time

        z = zipfile.ZipFile(path, "r")
        fname = z.namelist()[0]
        content = z.read(fname).decode()
        price_data = pd.read_csv(StringIO(content), header=None, names=headers,
            index_col=0, date_parser=custom_data_parser)
        z.close()
        return self._adjust_price(price_data)
    
    def _adjust_price(self, price_data):
        price_data['open'] = price_data['open'] / 10000
        price_data['close'] = price_data['close'] / 10000
        price_data['high'] = price_data['high'] / 10000
        price_data['low'] = price_data['low'] / 10000
        return price_data

    def _fname_to_date(self, fname):
        return parser.parse(fname.split('_')[0])

    def parse_trade_bars(self, data_symbol, date_start, date_end):
        """ 解析指定时间范围内的trade bar数据

        Args:
            data_symbol (str): 数据的编号，如"equity.usa.spy-minute"。
            date_start (str): 字符类型的日期开始时间，如2019-01-02
            date_end (str): 字符类型的日期结束时间，如2019-01-05
        """
        data_paths = []
        equity, period = data_symbol.split('-')
        type, market, symbol = equity.split('.')
        data_path = os.path.join(self._data_home, type, market, period, symbol)
        date_start = parser.parse(date_start)
        date_end = parser.parse(date_end)
        for root, dirs, files in os.walk(data_path):
            for name in files:
                if name.endswith("trade.zip"):
                    date = self._fname_to_date(name)
                    if date_start <= date and date <= date_end:
                        data_paths.append(os.path.join(root, name))
        bar_frames = [self.parse_trade_bars_by_path(path) for path in sorted(data_paths)]
        return pd.concat(bar_frames)


    
    def parse_quote_bars(self, path):
        raise NotImplementedError

    def parse_trade_ticks(self, path):
        raise NotImplementedError

    def parse_quote_ticks(self, path):
        raise NotImplementedError


class ResultParser(object):

    def __init__(self) -> None:
        self._data = None
        self.transactions = None
        self.benchmark = None
        self._orders = None

    def read_data(self, path):
        self._data = json.load(open(path, "r"))

    def get_orders(self):
        """ QC不支持多空对持仓, 这里就是不支持做空了。
            `orders_to_deals`的行为和这个匹配。

        Returns:
            List[Order]: 订单列表
        """
        if self._orders is not None:
            return self._orders
        self._orders = []
        for d_order in self._data["Orders"].values():
            order = self._parse_order(d_order)
            if order is not None:
                self._orders.append(order)
        return self._orders

    def calcu_time_aligned_orders(self, orders: List[Order], bars: pd.DataFrame):
        # aligned to left time
        for order in orders:
            index = bars.index.searchsorted(order.create_time)
            new_order = deepcopy(order)
            if index == len(bars):
                index -= 1
            new_order.create_time = bars.index[index]
            yield new_order

    def _parse_order(self, d_order: Dict):
        assert d_order["Direction"] != 3
        try:
            status = OrderStatus(d_order["Status"])
        except Exception as e:
            log.warn("Ignore order with unsupported status: {0}".format(d_order))
            return None
        order_type = OrderType(d_order["Type"])
        # direction = Direction(d_order["Direction"])
        direction = Direction.Long   # QC不支持多空对持仓, 这里就是不支持做空了。
        side = TradeSide.Open if d_order["Quantity"] > 0 else TradeSide.Close
        utc_time = parser.parse(d_order["LastFillTime"])
        # local_time = time.astimezone(tz.gettz('Asia/Shanghai'))
        utc_time = pd.to_datetime(utc_time.replace(tzinfo=None)) # utc time without timezone info
        order = Order(
            d_order["Id"], utc_time, d_order["Symbol"]["Value"],
            None, order_type, side, direction, d_order["Price"], abs(d_order["Quantity"]),
            status, 1
        )
        return order

    def get_indicators(self):
        indicators = []
        charts = self._data["Charts"]
        for chart in charts.values():
            for series in chart["Series"].values():
                if '(' in series["Name"] and ')' in series["Name"]:
                    indicator = series
                    indicator["RealName"] = chart["Name"]
                    indicators.append(indicator)
        rst = []
        for indicator in indicators:
            y = [v['y'] for v in indicator["Values"]]
            time = [datetime.datetime.fromtimestamp(v["x"]) for v in indicator["Values"]]
            indicator_ = {
                "name": indicator["RealName"],
                "info": indicator["Name"],
                "values": pd.Series(y, index=time)
            }
            indicator_["info"] =  self._parse_indicator_info(indicator_["info"])
            rst.append(indicator_)
        return rst

    def _parse_indicator_info(self, info):
        m = re.match(r"(.*)\((\d*),(\D*)_(\D*)\)", info)
        map_period = {
            "min": Period.Minute,
            "hour": Period.Hour,
            "day": Period.Day,
        }
        if m is None:
            raise Exception("Failed to parse indicator info")
        type, arg, symbol, period = m.group(1, 2, 3, 4)
        period = map_period[period]
        return {
            "type": type,
            "arguments": arg,
            "symbol": symbol,
            "period": period
        }

    def get_market_data(self, name: str):
        if name == MarketData.TradeBar.name:
            ohlcv = self._get_series(["Open", "High", "Low", "Close", "Volume"], name)
            time = [datetime.datetime.fromtimestamp(v["x"]) for v in ohlcv[0]["Values"]]
            open = [v['y'] for v in ohlcv[0]["Values"]]
            high = [v['y'] for v in ohlcv[1]["Values"]]
            low = [v['y'] for v in ohlcv[2]["Values"]]
            close = [v['y'] for v in ohlcv[3]["Values"]]
            volume = [v['y'] for v in ohlcv[4]["Values"]]
            return pd.DataFrame({
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            }, index=time)
        return None

    def _get_series(self, names: List[str], chart_name=None, is_target_series=None):
        if is_target_series is None:
            is_target_series = lambda x: x["Name"] in names
        rst = []
        charts = self._data["Charts"]
        if chart_name is None:
            for chart in charts.values():
                for series in chart["Series"].values():
                    if is_target_series(series):
                        rst.append(series)
        else:
            chart = charts[chart_name]
            for series in chart["Series"].values():
                if is_target_series(series):
                    rst.append(series)
        return rst

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