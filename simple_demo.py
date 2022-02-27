'''
Author: your name
Date: 2022-02-19 20:32:30
LastEditTime: 2022-02-27 18:08:01
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/simple_demo.py
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
from ml.plot_widgets.technical_widget import TechnicalFrame, MultiWidgetsFrame
from ml.plot_widgets.slider_widget import Slider, slider_strtime_format
from ml.plot_widgets.frame_widget import AxesWidget, SliderAxesWidget, CandleWidget
from ml.plot_widgets.plotter import SliderPlotter, Volume
from ml.log import wlog, init_loggers
import pandas as pd

init_loggers()

price_data = pd.read_csv("./test.csv", index_col=0, parse_dates=True)


class Deal(object):
    def __init__(self):
        self.open_datetime = None
        self.close_datetime = None
        self.open_price = 0
        self.close_price = 0

    def profit(self):
        return self.close_price - self.open_price

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


class MyAxesWidget(AxesWidget):

    def __init__(self, ax, name):
        AxesWidget.__init__(self, ax, name)

    def on_button_press(self, event):
        print("my test pressed")


def axes_widget_demo():
    ax = plt.axes()
    widget = MyAxesWidget(ax, "test")
    price_plot = ax.plot(price_data)
    widget.add_plot(price_plot, "price")
    widget.show()


def slider_simple_demo():
    fig = plt.figure()
    axes = []
    axes.append(plt.subplot2grid((5, 1), (0, 0), rowspan=4))
    axes.append(plt.subplot2grid((5, 1), (4, 0)))
    widget_size = len(price_data)
    window_size = 50
    # 创建子窗口 
    widget = SliderAxesWidget(axes[0], "subwidget2", widget_size, window_size)
    # 画线
    line = SliderPlotter(axes[0], "slider_plotter", price_data.close.values, price_data.close.values)
    line.ax.plot(price_data.close.values)
    widget.add_plotter(line , False)
    # 创建主窗口
    mainwindow = MultiWidgetsFrame(fig, "multi", widget_size, window_size)
    mainwindow.create_slider(axes[1], price_data.index)
    mainwindow.add_widget(widget)
    mainwindow.show()


def candle_widget_demo():
    fig = plt.figure()
    axes = []
    axes.append(plt.subplot2grid((5, 1), (0, 0), rowspan=4))
    axes.append(plt.subplot2grid((5, 1), (4, 0)))
    widget_size = len(price_data)
    window_size = 50

    candle_widget = CandleWidget(price_data, axes[0], "test", widget_size, window_size)
    candle_widget.plot_candle()


    mainwindow = MultiWidgetsFrame(fig, "multi", widget_size, window_size)
    mainwindow.create_slider(axes[1], price_data.index)
    mainwindow.add_widget(candle_widget)


    slider_pos = mainwindow.slider.ax.get_position()
    bigger_picture_ax = mainwindow.add_axes(
        slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
        zorder = 1000, frameon=False, alpha = 1)
    bigger_picture_ax.plot(price_data.close.values)
    bigger_picture = AxesWidget(bigger_picture_ax, "bigger_picture")                                        

    mainwindow.add_widget(bigger_picture)

    mainwindow.show()

def technical_widget_demo():
    fig = plt.figure()
    window_size = 50
    widget_size = len(price_data)

    frame = TechnicalFrame(fig, widget_size, window_size)
    frame.load_data(price_data)
    axes = frame.init_layout()

    candle_widget = CandleWidget(price_data, axes[0], "candle_widget", widget_size, window_size)
    volume_widget = SliderAxesWidget(axes[1], "subwidget2", widget_size, window_size)

    # 绘制第一个窗口
    candle_widget.plot_line(price_data.close.values, "black", lw=1)
    candle_widget.plot_candle()

    deals = []
    signals = []
    open_time = price_data.index[-12]
    for close_time in price_data.index[-10: -1]:
        signals.append((close_time, price_data.high[close_time], "buy"))
        deal = Deal()
        deal.open_datetime = open_time
        deal.close_datetime = close_time
        deal.open_price = price_data.close[open_time]
        deal.close_price = price_data.close[close_time]
        deals.append(deal)
    
    candle_widget.plot_signals(signals)
    candle_widget.plot_deals(deals)

    # 绘制第2个窗口
    volume_plotter = Volume(price_data.open, price_data.close, price_data.volume)
    volume_plotter.plot(axes[1])
    volume_widget.add_plotter(volume_plotter, False)

    frame.add_widget(candle_widget)
    frame.add_widget(volume_widget)
    frame.show()


#axes_widget_demo()
#candle_widget_demo()
#slider_simple_demo()
technical_widget_demo()