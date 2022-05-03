'''
Author: your name
Date: 2022-05-01 18:51:16
LastEditTime: 2022-05-02 12:29:49
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/data/util.py
'''
from ast import comprehension
from pydoc import doc
import pandas as pd
import zipfile
from io import StringIO
from dateutil import parser
from datetime import datetime

def tushare_to_qc_daily(ts_data: pd.DataFrame) -> pd.DataFrame:
    qc_df = ts_data[['trade_date', 'open', 'high', 'low', 'close', 'vol']].copy()
    factor = 10000
    for col in ['open', 'high', 'low', 'close']:
        qc_df[col] = qc_df[col] * factor
    qc_df['trade_date'] = qc_df['trade_date'].astype(str) + " 00:00"
    qc_df = qc_df.rename(columns={col: i for i, col in enumerate(qc_df.columns)})[::-1]
    return qc_df

def get_available_qc_data(path) -> str:
    price_data = None
    with zipfile.ZipFile(path, "r") as z:
        fname = z.namelist()[0]
        content = z.read(fname).decode()
        price_data = pd.read_csv(StringIO(content), header=None)

    time = price_data[0].values[-1]
    return time.split(' ')[0], price_data

def write_qc_dta(path, data):
    with zipfile.ZipFile(path, "w") as z:
        with z.open("hello.csv", "w") as new_hello:
            str_data = data.to_csv(None, index=False, header=None)
            new_hello.write(bytes(str_data, 'utf-8'))