'''
Author: your name
Date: 2022-02-19 20:32:30
LastEditTime: 2022-02-19 23:29:10
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/simple_demo.py
'''
from json.tool import main
import six
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from ml.widgets import mplots
from ml.widgets.technical_widget import TechnicalWidget, MultiWidgets
from ml.widgets.slider_widget import Slider, slider_strtime_format
from ml.widgets.frame_widget import FrameWidget, SliderCompatibleFrameWidget
from ml.widgets.plotter import Line, LineWithX, Volume
import pandas as pd


price_data = pd.read_csv("./test.csv", index_col=0, parse_dates=True)


class MyFrameWidget(FrameWidget):

    def __init__(self, ax, name):
        FrameWidget.__init__(self, ax, name)

    def on_button_press(self, event):
        print("my test pressed")


def frame_widget_demo():
    ax = plt.axes()
    widget = MyFrameWidget(ax, "test")
    price_plot = ax.plot(price_data)
    widget.add_plot(price_plot, "price")
    widget.show()


def slider_widget_demo():
    fig = plt.figure()
    axes = []
    axes.append(plt.subplot2grid((5, 1), (0, 0), rowspan=4))
    axes.append(plt.subplot2grid((5, 1), (4, 0)))
    widget_size = len(price_data)
    window_size = 50

    frame = SliderCompatibleFrameWidget(axes[0], "test", widget_size, window_size)
    candles = mplots.Candles(price_data, 'candles')
    frame.add_plotter(candles, False)
    slider = Slider(axes[1], "slider", widget_size, 10, frame, '', 0, widget_size-1,
                                1, widget_size/50, "%d", price_data.index)

    mainwindow = MultiWidgets(fig, plt, axes, "multi", widget_size)
    mainwindow.add_widget(frame)
    mainwindow.add_widget(slider)
    slider.add_observer(frame.on_slider)
    slider.add_observer(mainwindow.on_slider)
    mainwindow.show()


def technical_widget_demo():
    fig = plt.figure()
    window_size = 50
    widget_size = len(price_data)

    frame = TechnicalWidget(fig, price_data)
    axes = frame.init_layout(min(window_size, len(price_data)))

    subwidget1 = FrameWidget(axes[0], "subwidget1", widget_size, window_size)
    subwidget2 = FrameWidget(axes[1], "subwidget2", widget_size, window_size)
    slider = Slider(axes[2], "slider", widget_size, 10, frame, '', 0, widget_size-1,
                                widget_size-1, widget_size/50, "%d", price_data.index)
    frame.add_widget(0, subwidget1)
    frame.add_widget(1, subwidget2)
    frame.add_widget(2, slider)
    slider.add_observer(subwidget1.on_slider)
    slider.add_observer(subwidget2.on_slider)
    slider.add_observer(frame.on_slider)


#frame_widget()
#slider_widget_demo()
technical_widget_demo()