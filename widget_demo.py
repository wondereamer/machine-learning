'''
Author: your name
Date: 2022-02-19 20:32:30
LastEditTime: 2022-05-03 16:46:12
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
from ml.plot_widgets.frame_widget import AxesWidget, SliderAxesWidget, CandleWidget
from ml.plot_widgets.plotter import SliderPlotter, Volume
from ml.log import wlog, init_loggers
from ml.finance.datastruct import Deal, Direction
import pandas as pd

init_loggers()

price_data = pd.read_csv("./test.csv", index_col=0, parse_dates=True)[0: 100]

#  tradeBar.Open = csv[1].ToDecimal() * _scaleFactor;
#             tradeBar.High = csv[2].ToDecimal() * _scaleFactor;
#             tradeBar.Low = csv[3].ToDecimal() * _scaleFactor;
#             tradeBar.Close = csv[4].ToDecimal() * _scaleFactor;
#             tradeBar.Volume = csv[5].ToDecimal();

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
    data = price_data[0: 100]
    widget_size = len(data)
    window_size = 50

    candle_widget = CandleWidget(data, axes[0], "test", widget_size, window_size)
    candle_widget.plot_candle()


    mainwindow = MultiWidgetsFrame(fig, "multi", widget_size, window_size)
    mainwindow.create_slider(axes[1], data.index)
    mainwindow.add_widget(candle_widget)


    slider_pos = mainwindow.slider.ax.get_position()
    bigger_picture_ax = mainwindow.add_axes(
        slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
        zorder = 1000, frameon=False, alpha = 1)
    bigger_picture_ax.plot(data.close.values)
    bigger_picture = AxesWidget(bigger_picture_ax, "bigger_picture")                                        

    mainwindow.add_widget(bigger_picture)

    mainwindow.show()

def technical_widget_demo():
    fig = plt.figure()
    window_size = 50
    data = price_data[0: 100]
    widget_size = len(data)
    frame = TechnicalFrame(fig, widget_size, window_size)
    frame.set_data(data)
    axes = frame.init_layout()

    candle_widget = CandleWidget(data, axes[0], "candle_widget", widget_size, window_size)
    volume_widget = SliderAxesWidget(axes[1], "subwidget2", widget_size, window_size)

    # 绘制第一个窗口
    # candle_widget.plot_line(data.close.values, "black", lw=1, name="close")
    candle_widget.plot_candle()

    deals = []
    open_time = data.index[-12]
    for close_time in data.index[-10: -1]:
        deal = Deal(Direction.Long, data.close[open_time], data.close[close_time],
            open_time, close_time, 1, 1
        )
        deals.append(deal)
    
    candle_widget.plot_trades(deals)
    candle_widget.plot_deals(deals)

    # 绘制第2个窗口
    volume_plotter = Volume(data.open, data.close, data.volume)
    volume_plotter.plot(axes[1])
    volume_widget.add_plotter(volume_plotter, False)

    frame.add_widget(candle_widget)
    frame.add_widget(volume_widget)
    frame.show()


axes_widget_demo()
# candle_widget_demo()
# slider_simple_demo()
# technical_widget_demo()