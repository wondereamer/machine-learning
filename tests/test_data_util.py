'''
Author: your name
Date: 2022-05-01 18:52:44
LastEditTime: 2022-05-03 16:04:06
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/data/test_data_util.py
'''


from email.utils import parsedate_to_datetime
import os
import unittest
from io import StringIO
import pandas as pd


import util
util.set_home_path_to_sys()

import ml.data.util as datautil
from ml.util import test_path


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.join(test_path, 'data')
        self.qc_data_fanme = os.path.join(self.data_path, "get_available_qc_data.zip")
        self.qc_write_data_fanme = os.path.join(self.data_path,  "write_qc_data.zip")

    def test_tushare_to_qc_daily(self):
        data = r"""
        ,ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount
        0,000001.SZ,20180718,8.75,8.85,8.69,8.7,8.72,-0.02,-0.23,525152.77,460697.377
        1,000001.SZ,20180717,8.74,8.75,8.66,8.72,8.73,-0.01,-0.11,375356.33,326396.994
        """
        ts_df = pd.read_csv(StringIO(data))
        qc_df = datautil.tushare_to_qc_daily(ts_df)
        expected_date = ['20180717 00:00', '20180718 00:00']
        expected_open = [87400, 87500]
        expected_vol = [375356.33, 525152.77]
        self.assertListEqual(expected_date, qc_df[0].values.tolist())
        self.assertListEqual(expected_open, qc_df[1].values.tolist())
        self.assertListEqual(expected_vol, qc_df[5].values.tolist())

    def test_get_last_date_available_of_data(self):
        last_date, data = datautil.get_available_qc_data(self.qc_data_fanme)
        self.assertEqual('19980129', last_date)
        self.assertEqual(19, len(data))

    def test_write_qc_data(self):
        data = r"""
        0,1,2,3,4,5
        20180718 00:00:00,8.75,8.85,8.69,8.7,460697.377
        20180717 00:00:00,8.74,8.75,8.66,8.72,326396.994
        """
        ts_df = pd.read_csv(StringIO(data))
        datautil.write_qc_dta(self.qc_write_data_fanme, ts_df)
        last_date, data = datautil.get_available_qc_data(self.qc_write_data_fanme)
        self.assertEqual(2, len(data))