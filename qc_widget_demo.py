'''
Author: wondereamer
Date: 2022-03-05 21:18:04
LastEditTime: 2022-03-06 15:51:20
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/qc_widget_demo.py
'''
import sys
import os
path2 = os.path.dirname(__file__)
sys.path.append(path2)
from json.tool import main
import six
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from ml.plot_widgets.technical_widget import TechnicalFrame
from ml.plot_widgets.slider_widget import slider_strtime_format
from ml.plot_widgets.frame_widget import SliderAxesWidget, CandleWidget
from ml.plot_widgets.plotter import Volume
from ml.log import wlog, init_loggers
from ml.finance.datastruct import Deal, Direction
from ml.data import qc
from ml.util import util
from ml.finance import analysis
from ml.log import wlog as log
import pandas as pd

init_loggers()

class TimeFormatter(Formatter):
    # def __init__(self, dates, fmt='%Y-%m-%d'):
    # 分类 －－format
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind].strftime(self.fmt)


class QCWidget(object):

    def __init__(self):
        pass

    def load_data(self, name, start_date, end_date):
        parser = qc.DataParser(util.data_path)
        self.price_data = parser.parse_trade_bars(name, start_date, end_date)

    def load_result(self, fpath):
        self._result = qc.ResultParser()
        self._result.read_data(fpath)


    def create_widgets(self):
        fig = plt.figure()
        window_size = 50
        widget_size = len(self.price_data)

        frame = TechnicalFrame(fig, widget_size, window_size)
        frame.set_data(self.price_data)
        axes = frame.init_layout()

        candle_widget = CandleWidget(self.price_data, axes[0], "candle_widget", widget_size, window_size)
        volume_widget = SliderAxesWidget(axes[1], "subwidget2", widget_size, window_size)

        # 绘制第一个窗口
        candle_widget.plot_line(self.price_data.close.values, "black", lw=1)
        candle_widget.plot_candle()

        orders = self._result.get_orders()
        deals = analysis.orders_to_deals(orders)
        candle_widget.plot_signals(deals)
        candle_widget.plot_deals(deals)

        # 绘制第2个窗口
        volume_plotter = Volume(self.price_data.open, self.price_data.close, self.price_data.volume)
        volume_plotter.plot(axes[1])
        volume_widget.add_plotter(volume_plotter, False)

        frame.add_widget(candle_widget)
        frame.add_widget(volume_widget)
        frame.show()


widget = QCWidget()
name = "equity.usa.spy-minute"
file_path = os.path.join(util.data_path, "result.json")
widget.load_data(name, '2013-10-07', '2013-10-08')
widget.load_result(file_path)
widget.create_widgets()
