'''
Author: your name
Date: 2022-05-01 09:37:17
LastEditTime: 2022-05-03 16:06:46
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/test_data copy.py
'''
'''
Author: your name
Date: 2022-02-28 08:01:51
LastEditTime: 2022-03-13 10:58:05
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/data/test_data.py
'''
import os
import unittest
import shutil
from pprint import pprint

from numpy import ndarray

import util
util.set_home_path_to_sys()

from ml.data.tushare import TradingCalenday, EquityData, Resolution, set_token
from ml.util import test_path
import ml.data.util as datautil


class TestTradingCalenday(unittest.TestCase):

    def test_trading_calenday(self):
        calenday = TradingCalenday("20220401")
        trading_day = '20220403'
        next_trading_day = calenday.get_next_trading_date('SZ', trading_day)
        self.assertEqual("20220406", next_trading_day)

        nature_day = '20220404'
        next_trading_day = calenday.get_next_trading_date('sz', nature_day)
        self.assertEqual("20220406", next_trading_day)


class TestEquityData(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.join(test_path, 'data')
        self.stock = EquityData(self.data_path)
        token = "b82e69b2dcd8b91f9624de77d3a5b194db95065bc1b3a4ef5f876d95"
        set_token(token)

    def test_query_stock_data(self):
        data = self.stock.query_stock_data('000001.SZ', '20100101', '20100108', Resolution.Day)
        self.assertEqual(5, len(data))

        data = self.stock.query_stock_data('000001.SZ', '2010/01/01', '2010/01/08', Resolution.Day)
        self.assertEqual(5, len(data))

    def test_get_stock_code_without_cache(self):
        fname = os.path.join(self.data_path, self.stock.EquityCodesFileName)
        if os.path.exists(fname):
            os.remove(fname)
        codes = self.stock.get_stock_code('sz', False)
        self.assertEqual(2626, len(codes))

    def test_get_stock_code_with_cache(self):
        codes = self.stock.get_stock_code('sz')
        self.assertEqual(2626, len(codes))

    def test_update_data_by_codes_with_exist_data(self):
        # prepare data
        shutil.copy(os.path.join(self.data_path, '000001.zip'), os.path.join(self.data_path, 'equity', 'sz', 'daily'))
        shutil.copy(os.path.join(self.data_path, '000002.zip'), os.path.join(self.data_path, 'equity', 'sz', 'daily'))
        #
        new_num1, new_num2 = self.stock.update_data_by_codes(['000001.SZ', '000002.sz'], '19980123', Resolution.Day)

        last_date1, data1 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000001.zip'))
        last_date2, data2 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000002.zip'))
        self.assertEqual(7, new_num1)
        self.assertEqual(13, new_num2)
        self.assertEqual('19980123', last_date1)
        self.assertEqual('19980123', last_date2)
        self.assertEqual(16, len(data1))
        self.assertEqual(16, len(data2))

    def test_update_data_by_codes_without_exist_data(self):
        os.remove(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000001.zip'))
        os.remove(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000002.zip'))
        new_num1, new_num2 = self.stock.update_data_by_codes(['000001.SZ', '000002.sz'], '19920120', Resolution.Day)
        last_date1, data1 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000001.zip'))
        last_date2, data2 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000002.zip'))
        self.assertEqual(13, new_num1)
        self.assertEqual(13, new_num2)
        self.assertEqual('19920120', last_date1)
        self.assertEqual('19920120', last_date2)
        self.assertEqual(13, len(data1))
        self.assertEqual(13, len(data2))

    def test_update_data_by_exchange(self):
        def handler(func, path, exc_info):
            pass
        shutil.rmtree(os.path.join(self.data_path, 'equity', 'sz', 'daily'), onerror=handler)
        shutil.rmtree(os.path.join(self.data_path, 'equity', 'sh', 'daily'), onerror=handler)
        shutil.rmtree(os.path.join(self.data_path, 'equity', 'bj', 'daily'), onerror=handler)
        # use 1 code, use a small day to test
        old_start_date = TradingCalenday.EquityDailyStartDate
        TradingCalenday.EquityDailyStartDate = '20211101'
        self.stock.EquityCodesFileName = "equity_cn_codes_mini.csv"
        sz_update_num = self.stock.update_data_by_exchange('sz', "20211122", Resolution.Day)
        sh_update_num = self.stock.update_data_by_exchange('sh', "20211122", Resolution.Day)
        bj_update_num = self.stock.update_data_by_exchange('bj', "20211122", Resolution.Day)
        
        self.assertEqual([15, 15], sz_update_num)
        self.assertEqual([15], sh_update_num)
        self.assertEqual([6], bj_update_num)
        last_date1, data1 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000001.zip'))
        last_date2, data2 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sz', 'daily', '000002.zip'))
        last_date3, data3 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'sh', 'daily', '600000.zip'))
        last_date4, data4 = datautil.get_available_qc_data(os.path.join(self.data_path, 'equity', 'bj', 'daily', '872925.zip'))
        self.assertEqual(15, len(data1))
        self.assertEqual(15, len(data2))
        self.assertEqual(15, len(data3))
        self.assertEqual(6, len(data4))
        self.assertEqual(last_date1, '20211122')
        self.assertEqual(last_date2, '20211122')
        self.assertEqual(last_date3, '20211122')
        self.assertEqual(last_date4, '20211122')
        TradingCalenday.EquityDailyStartDate = old_start_date



if __name__ == '__main__':
    unittest.main()
