'''
Author: your name
Date: 2022-02-28 08:06:23
LastEditTime: 2022-03-05 22:03:12
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/tests/data/util.py
'''
import os
import sys
from pathlib import Path

home_path = Path(os.path.dirname(__file__)).parent.absolute()

def set_home_path_to_sys():
    sys.path.append(str(home_path))
    print("add to sys path: {0}".format(home_path))