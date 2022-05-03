'''
Author: your name
Date: 2020-05-03 17:38:48
LastEditTime: 2022-05-01 10:59:27
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/util/util.py
'''
import os
import sys
from pathlib import Path

def cached_func(function):
    """ 参数为key，返回为value。 """
    cache = {}
    def wrapper(*args, **kwargs):
        key = args + (kwd_mark,) + tuple(sorted(kwargs.items()))
        if key in cache:
            return cache[key]
        else:
            result = function(*args, **kwargs)
            cache[key] = result
            return result
    return wrapper


home_path = Path(os.path.dirname(__file__)).parent.absolute()
data_path = os.path.join(Path(os.path.dirname(__file__)).parent.parent.absolute(), "data")
test_path = os.path.join(Path(os.path.dirname(__file__)).parent.parent.absolute(), "tests")

def set_home_path_to_sys():
    sys.path.append(str(home_path))
    print("add to sys path: {0}".format(home_path))