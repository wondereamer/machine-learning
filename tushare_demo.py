'''
Author: your name
Date: 2022-04-13 22:20:30
LastEditTime: 2022-04-28 22:07:51
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tushare_demo.py
'''
from dateutil import parser
from datetime import datetime
import code
import os
import tushare as ts
import pandas as pd
ts.set_token("b82e69b2dcd8b91f9624de77d3a5b194db95065bc1b3a4ef5f876d95")
pro = ts.pro_api()

# 积分和接口： https://tushare.pro/document/1?doc_id=290


def str_to_tushare_date(date: str) -> str:
    return parser.parse(date).strftime('%Y%m%d')


def time_to_tushare_date(date: datetime) -> str:
    return date.strftime('%Y%m%d')


class TradingCalenday(object):

    CalendayCache = {}

    def __init__(self, begin_date: str):
        self._begin_date = str_to_tushare_date(begin_date)

    def get_next_trading_date(self, exchange, date: str):
        tushare_date = str_to_tushare_date(date)

        if tushare_date >= time_to_tushare_date(datetime.now()):
            print("can't get next trading calenday for future")
            return None

        if tushare_date < self._begin_date:
            print("can't get next trading calenday for date before %s" % self._begin_date)
            return None

        if exchange not in self.CalendayCache:
            self.CalendayCache[exchange] = self._query_calenday(exchange)
        calenday = self.CalendayCache[exchange]
        next_date_index = calenday['cal_date'].searchsorted(date, side='right')

        if calenday['cal_date'][next_date_index-1] != date:
            assert False

        for i in range(next_date_index, len(calenday)):
            next_date_is_open = calenday['is_open'][i]
            if next_date_is_open  == 1:
                return calenday['cal_date'][i]
        return None

    def _query_calenday(self, exchange):
        end_date = time_to_tushare_date(datetime.now())
        df = pro.trade_cal(exchange=exchange, start_date=self._begin_date, end_date=end_date)
        return df


def test_trading_calenday():
    calenday = TradingCalenday("20220401")
    next_trading_day = calenday.get_next_trading_date('SZSE', '20220403')
    print(next_trading_day)


class StockData(object):

    EquityDataBeginDate = "20050101"  # previous nature date of data
    DefaultCodesInfo = ["ts_code", "symbol", "name", "list_status", "exchange"]
    ExchangeMap = {
        "SZSE": ("SZ", "深交所"),
        "SSE": ("SH", "上交所")
    }

    def __init__(self) -> None:
        self.calenday = TradingCalenday(self.EquityDataBeginDate)
    
   # SSE上交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源


    def _query_stock_basic(self):
        # https://waditu.com/document/2?doc_id=25
        data = pro.stock_basic(exchange='', list_status='L', fields='exchange,ts_code,symbol,name,area,industry,list_date, list_status')
        return data

    def query_stock_data(self, code, start_date, end_date, period):
        df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
        return df

    def get_stock_code(self, exchange:str=None):
        try:
            codes = pd.read_csv("codes.csv")
        except Exception as e:
            print("query codes from tushare")
            print(e)
            codes = self._query_stock_basic()
            codes.to_csv("codes.csv", index=None)
        mini_codes = codes[self.DefaultCodesInfo]
        mini_codes['symbol'] = mini_codes['symbol'].astype(str)
        if exchange is None:
            return mini_codes
        else:
            for name, data in mini_codes.groupby('exchange'):
                if name == exchange:
                    return data
        return None

    def add_stock_data_with_date(self, path_to_exchange, exchange, init_day, resolution="daily"):
        # 1. when data in dir is empty, create dir, create date info file
        # 2. read date info , get next expecting trading date
        data_path = os.path.join(path_to_exchange, exchange, resolution)
        if os.path.exists(data_path) == False:
            print("create data dir: %s" % data_path)
            os.makedirs(data_path)
            self._write_data_end_date(data_path, self.EquityDataBeginDate)

        data_end_date = self._read_data_end_date(data_path)
        print("exchange %s: data end date %s" % (exchange, data_end_date))

        next_trading_date = self.calenday.get_next_trading_date(exchange, data_end_date)
        if next_trading_date is None:
            print("date is latest, not need to update")
            return

        self._query_exchange_data_by_date(exchange, next_trading_date, resolution)

    def _query_exchange_data_by_date(exchange: str, next_trading_date: str, resolution):
        # get all codes of exchange
        # query data by codes
        if resolution == 'daily':
            pass

    def _write_data_end_date(self, data_path, time: str):
        fpath = os.path.join(data_path, "data_end_date.txt")
        print("write data end date: %s" % (fpath))
        with open(fpath, "w") as f:
            f.write(time)

    def _read_data_end_date(self, data_path):
        fpath = os.path.join(data_path, "data_end_date.txt")
        with open(fpath, "r") as f:
            return f.read()
    


stock = StockData()
test_trading_calenday()
# stock.add_stock_data_with_date("./", "sz", "20050101")
# data = stock.query_stock_data(ts_code='000001.SZ', start_date='20180701', end_date='20180718')
# codes = stock.get_stock_code('SZSE')
# print(codes)
# print(len(codes))
