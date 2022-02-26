'''
Author: your name
Date: 2022-02-19 10:04:35
LastEditTime: 2022-02-26 19:17:42
LastEditors: your name
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/mplots.py
'''
# -*- coding: utf-8 -*-

import six
from six.moves import range
import numpy as np
import inspect
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection


def override_attributes(method):
    # 如果plot函数不带绘图参数，则使用属性值做为参数。
    # 如果带参数，者指标中的plot函数参数能够覆盖本身的属性。
    def wrapper(self, widget, *args, **kwargs):
        self.widget = widget
        # 用函数中的参数覆盖属性。
        arg_names = inspect.getargspec(method).args[2:]
        method_args = {}
        obj_attrs = {}
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)

        try:
            for attr in arg_names:
                obj_attrs[attr] = getattr(self, attr)
        except Exception as e:
            six.print_(e)
            six.print_("构造函数和绘图函数的绘图属性参数不匹配。")
        obj_attrs.update(method_args)
        return method(self, widget, **obj_attrs)
    return wrapper




class TradingSignal(object):
    """ 从信号坐标(时间， 价格)中绘制交易信号。 """
    def __init__(self, signal, name="Signal", c=None, lw=2):
        self.signal = signal
        self.name = name

    def plot(self, widget, c=None, lw=2):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=c, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)

    def y_interval(self, w_left, w_right):
        return 0, 100000000


class TradingSignalPos(object):
    """ 从价格和持仓数据中绘制交易信号图。 """
    def __init__(self, price_data, deals, name="Signal", c=None, lw=2):
        self.signal = []
        self.colors = []
        price_data['row'] = [i for i in range(0, len(price_data))]
        for deal in deals:
            # ((x0, y0), (x1, y1))
            p = ((price_data.row[deal.open_datetime], deal.open_price),
                 (price_data.row[deal.close_datetime], deal.close_price))
            self.signal.append(p)
            self.colors.append(
                (1, 0, 0, 1) if deal.profit() > 0 else (0, 1, 0, 1))
        self.name = name

    def plot(self, widget, lw=2):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=self.colors, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)

    def y_interval(self, w_left, w_right):
        # @todo signal interval
        return 0, 100000000
