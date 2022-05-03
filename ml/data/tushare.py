'''
Author: your name
Date: 2022-04-13 22:20:30
LastEditTime: 2022-05-03 16:40:13
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tushare_demo.py
'''
from dateutil import parser
from datetime import datetime, timedelta
import code
import os
from matplotlib.style import available
import tushare as ts
import pandas as pd

from ml.log import dlog as log
from ml.log import init_loggers
import ml.data.util as datautil

init_loggers()


pro = None

# 积分和接口： https://tushare.pro/document/1?doc_id=290


def str_to_tushare_date(date: str) -> str:
    return parser.parse(date).strftime('%Y%m%d')


def time_to_tushare_date(date: datetime) -> str:
    return date.strftime('%Y%m%d')


# SSE上交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源
ExchangeMap = {
    "sz": ("SZSE", "深交所"),
    "sh": ("SSE", "上交所"),
    "bj": ("BSE", "北交所")
}

class Resolution(object):

    Day = "daily"


class TradingCalenday(object):

    CalendayCache = {}
    EquityDailyStartDate = "19920101"
    EquityMinuteStartDate = "20090101"
    

    def __init__(self, begin_date: str):
        self._begin_date = str_to_tushare_date(begin_date)

    def get_next_trading_date(self, exchange, date: str):
        if (exchange.lower() not in list(ExchangeMap.keys())):
            raise Exception("error exchange code: %s" % exchange)

        exchange = exchange.lower()
        tushare_date = str_to_tushare_date(date)

        if tushare_date >= time_to_tushare_date(datetime.now()):
            log.warn("can't get next trading calenday for future")
            return None

        if tushare_date < self._begin_date:
            log.warn("can't get next trading calenday for date before %s" % self._begin_date)
            return None

        if exchange not in self.CalendayCache:
            self.CalendayCache[exchange] = self._query_calenday(exchange)
        calenday = self.CalendayCache[exchange]
        next_date_index = calenday['cal_date'].searchsorted(tushare_date, side='right')

        for i in range(next_date_index, len(calenday)):
            next_date_is_open = calenday['is_open'][i]
            if next_date_is_open  == 1:
                return calenday['cal_date'][i]
        return None

    def _query_calenday(self, exchange):
        end_date = time_to_tushare_date(datetime.now())
        ts_exchange = ExchangeMap[exchange][0]
        df = pro.trade_cal(exchange=ts_exchange, start_date=self._begin_date, end_date=end_date)
        return df



class EquityData(object):

    EquityDataBeginDate = "20050101"  # previous nature date of data
    DefaultCodesInfo = ["ts_code", "symbol", "name", "list_status", "exchange"]
    EquityCodesFileName = "equity_cn_codes.csv"
    EquityDataDir = "equity"

    def __init__(self, data_home_path: str) -> None:
        self.calenday = TradingCalenday(TradingCalenday.EquityDailyStartDate)
        self._init_path(data_home_path)

    def _init_path(self, data_home_path):
        self.data_home = data_home_path
        self.equity_data_home = os.path.join(data_home_path, self.EquityDataDir)
        self._create_if_not_exist_dir(self.data_home)
        self._create_if_not_exist_dir(self.equity_data_home)

    def _create_if_not_exist_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def _query_stock_basic(self):
        # https://waditu.com/document/2?doc_id=25
        data = pro.stock_basic(exchange='', list_status='L', fields='exchange,ts_code,symbol,name,area,industry,list_date, list_status')
        return data

    def query_stock_data(self, code: str, start_date: str, end_date: str, resolution: Resolution):
        """ query stock data from remotes

        Args:
            code (str): symbol code, such as '000001.SZ'
            start_date (str): start of query date, such as '2010-03-01'
            end_date (str): end of query date, such as '2010-03-09'
            resolution (Resolution): resolution, such as  `Resulotion.Day`

        Returns:
            pd.DataFrame: stock data
        """
        if resolution != Resolution.Day:
            raise Exception("Not supported resolution: %s" % resolution)
        log.info("query {0}, start_date: {1}, end_date: {2} from tushare".format(
            code, start_date, end_date))
        code = code.upper()
        start_date = str_to_tushare_date(start_date)
        end_date = str_to_tushare_date(end_date)
        df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
        log.debug("get %s" % str(df))
        return df

    def get_stock_code(self, exchange:str=None, use_file_cache=True):
        # TODO always use memory cache
        fname = os.path.join(self.data_home, self.EquityCodesFileName)
        codes = None
        if use_file_cache:
            try:
                codes = pd.read_csv(fname)
            except Exception as e:
                pass
        if codes is None:
            # not use cache
            # use cache, but no cache file found
            log.info("query codes from tushare")
            codes = self._query_stock_basic()
            log.info("save codes to %s" % fname)
            codes.to_csv(fname, index=None)

        mini_codes = codes[self.DefaultCodesInfo]
        mini_codes['symbol'] = mini_codes['symbol'].astype(str)
        if exchange is None:
            return mini_codes
        else:
            ts_exchange = ExchangeMap[exchange.lower()][0]
            for name, data in mini_codes.groupby('exchange'):
                if name == ts_exchange:
                    return data
        return None

    def update_data_by_exchange(self, exchange: str, end_date: str, resolution: Resolution):
        assert resolution == 'daily'
        # TODO
        # get all codes of exchange
        # query data by codes
        codes = self.get_stock_code(exchange)
        end_date = str_to_tushare_date(end_date)
        return self.update_data_by_codes(codes['ts_code'].values, end_date, resolution)

    def update_data_by_codes(self, codes, end_date, resolution):
        """ query and add data to storage

        Args:
            codes (List[str]): code list, such as ["000001.SZ", "600000._SH"]
            end_date (str): update data to end_date, such as "20110101'
            resolution (Resolution): data resolution, such as Resolution.Day

        Returns:
            List[int]: stock data
        """
        # 1. bi
        new_data_length = []
        for code in codes:
            log.info("update: %s" % code)
            symbol, exchange = tuple(code.split('.'))
            exchange = exchange.lower()
            code_parent_path = os.path.join(self.equity_data_home, exchange, resolution)
            self._create_if_not_exist_dir(code_parent_path)

            code_path = os.path.join(code_parent_path, symbol + ".zip")
            last_date, available_data = self._get_available_data(code_path, exchange, resolution)
            next_nature_date = time_to_tushare_date(parser.parse(last_date) + timedelta(days=1))
            if next_nature_date is None:
                continue
            try:
                new_data = self.query_stock_data(code, str_to_tushare_date(next_nature_date),
                    str_to_tushare_date(end_date), Resolution.Day)
            except:
                return tuple(new_data_length)

            new_qc_data = datautil.tushare_to_qc_daily(new_data)
            log.debug(str(new_qc_data))
            if available_data is not None:
                data = pd.concat([available_data, new_qc_data])
            else:
                data = new_qc_data
            datautil.write_qc_dta(code_path, data)

            new_data_length.append(len(new_data))
            log.info("%s's new data length: %s" % (code, new_data_length))

        return new_data_length

    def _get_available_data(self, code_path, exchange, resolution):
        """ get last date of available data and available data

        Args:
            code_path (str): path of code file
            exchange (str): exchange code, such as 'sz'
            resolution (Resolution): resolution of data

        Returns:
            Tuple(str, pd.DataFrame): (next nature date, available data)
        """
        data = None
        try:
            last_ts_date, data = datautil.get_available_qc_data(code_path)
        except Exception:
            if resolution in [Resolution.Day]:
                last_ts_date = self.calenday.EquityDailyStartDate
            else:
                last_ts_date = self.calenday.EquityMinuteStartDate
        return last_ts_date, data


def set_token(token):
    ts.set_token(token)
    global pro
    pro = ts.pro_api()


def update_tushare_data(token, data_path, exchanges):
    set_token(token)
    for exchange in exchanges:
        stock = EquityData(data_path)
        ts_date = time_to_tushare_date(datetime.now())
        log.info("*" * 30)
        log.info("update exhange: %s" % exchange)
        update_num = stock.update_data_by_exchange(exchange, ts_date, Resolution.Day)
        log.info("detail: %s" % update_num)